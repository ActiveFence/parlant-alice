"""
Alice integration module.

This module provides the Alice class for integrating with Alice services.
"""

import os
from typing import Any, Optional

from wonderfence_sdk.client import AnalysisContext
from wonderfence_sdk.client import WonderFenceClient as SDKClient
from wonderfence_sdk.models import Actions, EvaluateMessageResponse, ImageInput

import parlant.sdk as p

from .moderation_service import AliceNLPServiceWrapper


class Alice:
    def __init__(
        self,
        api_key: Optional[str] = None,
        app_name: Optional[str] = None,
        blocked_message: Optional[str] = None,
    ):
        """
        Initialize the Alice client.

        Args:
            api_key: Alice API key for authentication. If not provided, will be loaded from ALICE_API_KEY env var.
            app_name: Application name for identification. If not provided, will be loaded from ALICE_APP_NAME env var.
            blocked_message: Message to display when content is blocked. If not provided, will be loaded from ALICE_BLOCKED_MESSAGE env var, or defaults to 'The generated message was blocked by guardrails.'
        """
        self.api_key = api_key or os.getenv("ALICE_API_KEY")
        self.app_name = app_name or os.getenv("ALICE_APP_NAME")
        self.blocked_message = blocked_message or os.getenv(
            "ALICE_BLOCKED_MESSAGE", "The generated message was blocked by guardrails."
        )

        if not self.api_key:
            raise ValueError(
                "Alice API key is required. Please provide it via the 'api_key' parameter "
                "or set the ALICE_API_KEY environment variable."
            )

        self._client = SDKClient(api_key=self.api_key, app_name=self.app_name)

    async def check_message(
        self,
        session_id: str,
        agent_id: str,
        message: Optional[str] = None,
        image: Optional[ImageInput] = None,
    ) -> EvaluateMessageResponse:
        """
        Check a message (text or image) for policy violations.

        Args:
            session_id: Session identifier
            agent_id: Agent identifier
            message: Text message to check (mutually exclusive with image)
            image: ImageInput object for image checking (mutually exclusive with message)

        Returns:
            EvaluateMessageResponse with moderation results

        Raises:
            ValueError: If neither or both message and image are provided
            Exception: If moderation service fails
        """
        if message is None and image is None:
            raise ValueError("Either message or image must be provided")
        if message is not None and image is not None:
            raise ValueError("Cannot provide both message and image - they are mutually exclusive")

        analysis_context = AnalysisContext(
            user_id=agent_id,
            session_id=session_id,
        )
        try:
            analysis_result = await self._client.evaluate_response(
                context=analysis_context,
                response=message,
                image=image,
            )
        except Exception as e:
            raise Exception("Moderation service failure (Alice)") from e

        return analysis_result

    async def check_message_compliance(
        self, ctx: p.EngineContext, payload: Any, exc: Exception | None
    ) -> p.EngineHookResult:
        generated_message = payload

        result = await self.check_message(
            session_id=ctx.session.id,
            agent_id=ctx.agent.id,
            message=generated_message,
        )

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
        wrapped_nlp_service = AliceNLPServiceWrapper(original_nlp_service, self._client, logger, meter)

        container[p.NLPService] = wrapped_nlp_service
        container[p.EngineHooks].on_message_generated.append(self.check_message_compliance)

        # Register the Alice instance in the container for use in custom tools
        container[Alice] = self

        return container
