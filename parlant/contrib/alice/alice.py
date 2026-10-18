"""
Alice integration module.

This module provides the Alice class for integrating with Alice services.
"""

import os
import uuid
from typing import Any, Optional

from wonderfence_sdk.client import AnalysisContext, WonderFenceV2Client
from wonderfence_sdk.models import Actions, EvaluateMessageResponse

import parlant.sdk as p

from .moderation_service import AliceNLPServiceWrapper


class Alice:
    def __init__(
        self,
        api_key: Optional[str] = None,
        app_id: Optional[str] = None,
        blocked_message: Optional[str] = None,
    ):
        """
        Initialize the Alice client.

        Args:
            api_key: Alice API key for authentication. If not provided, will be loaded from ALICE_API_KEY env var.
            app_id: ID (UUID) of the application in Alice's Application Inventory whose policies evaluate the messages. If not provided, will be loaded from ALICE_APP_ID env var.
            blocked_message: Message to display when content is blocked. If not provided, will be loaded from ALICE_BLOCKED_MESSAGE env var, or defaults to 'The generated message was blocked by guardrails.'
        """
        self.api_key = api_key or os.getenv("ALICE_API_KEY")
        self.blocked_message = blocked_message or os.getenv(
            "ALICE_BLOCKED_MESSAGE", "The generated message was blocked by guardrails."
        )

        if not self.api_key:
            raise ValueError(
                "Alice API key is required. Please provide it via the 'api_key' parameter "
                "or set the ALICE_API_KEY environment variable."
            )

        resolved_app_id = app_id or os.getenv("ALICE_APP_ID")
        if not resolved_app_id:
            raise ValueError(
                "Alice application ID is required. Please provide it via the 'app_id' parameter "
                "or set the ALICE_APP_ID environment variable."
            )
        try:
            # Canonical form: the API matches app_id as a string, so "{...}" or uppercase would not resolve.
            self.app_id: str = str(uuid.UUID(resolved_app_id))
        except ValueError as e:
            raise ValueError(f"Alice application ID must be a UUID, got '{resolved_app_id}'.") from e

        self._client = WonderFenceV2Client(api_key=self.api_key)

    async def check_message(self, message: str, session_id: str, customer_id: str) -> EvaluateMessageResponse:
        try:
            analysis_context = AnalysisContext(session_id=session_id, user_id=customer_id)
            analysis_result = await self._client.evaluate_response(
                app_id=self.app_id, context=analysis_context, response=message
            )
        except Exception as e:
            raise Exception("Moderation service failure (Alice)") from e

        return analysis_result

    async def check_message_compliance(
        self, ctx: p.EngineContext, payload: Any, exc: Exception | None
    ) -> p.EngineHookResult:
        generated_message = payload

        result = await self.check_message(generated_message, ctx.session.id, ctx.session.customer_id)

        if result.action == Actions.DETECT:
            ctx.logger.warning(f"Detected a non-compliant message: '{generated_message}': {result.detections}.")
        elif result.action in (Actions.BLOCK, Actions.MASK):
            message = result.action_text if result.action == Actions.MASK else self.blocked_message

            ctx.logger.warning(f"Prevented sending a non-compliant message: '{generated_message}'.")

            await ctx.session_event_emitter.emit_message_event(
                trace_id=ctx.tracer.trace_id,
                data=p.MessageEventData(
                    message=message,
                    participant={"id": ctx.agent.id, "display_name": ctx.agent.name},
                ),
            )

            return p.EngineHookResult.BAIL  # Do not send this message

        return p.EngineHookResult.CALL_NEXT  # Continue with the normal process

    async def configure_container(self, container: p.Container) -> p.Container:
        # Get the original NLPService, logger, and meter from the container
        original_nlp_service = container[p.NLPService]
        logger = container[p.Logger]
        meter = container[p.Meter]

        # Create a wrapper that overrides get_moderation_service
        wrapped_nlp_service = AliceNLPServiceWrapper(original_nlp_service, self._client, self.app_id, logger, meter)

        container[p.NLPService] = wrapped_nlp_service
        container[p.EngineHooks].on_message_generated.append(self.check_message_compliance)

        return container
