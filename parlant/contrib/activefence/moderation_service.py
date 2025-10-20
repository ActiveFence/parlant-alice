from activefence_client_sdk.client import ActiveFenceClient, AnalysisContext
from activefence_client_sdk.models import Actions
from typing_extensions import override

from parlant.core.loggers import Logger
from parlant.core.nlp.embedding import Embedder
from parlant.core.nlp.generation import SchematicGenerator, T
from parlant.core.nlp.moderation import CustomerModerationContext, ModerationCheck, ModerationService
from parlant.core.nlp.service import NLPService


class ActiveFenceNLPServiceWrapper(NLPService):
    def __init__(self, original_nlp_service: NLPService, activefence_client: ActiveFenceClient, logger: Logger):
        self._original_nlp_service = original_nlp_service
        self._activefence_client = activefence_client
        self._logger = logger

    async def get_schematic_generator(self, t: type[T]) -> SchematicGenerator[T]:
        return await self._original_nlp_service.get_schematic_generator(t)

    async def get_embedder(self) -> Embedder:
        return await self._original_nlp_service.get_embedder()

    async def get_moderation_service(self) -> ModerationService:
        return ActiveFenceModerationService(self._logger, self._activefence_client)


class ActiveFenceModerationService(ModerationService):
    def __init__(self, logger: Logger, client: ActiveFenceClient) -> None:
        self._logger = logger
        self._client = client

    @override
    async def moderate_customer(self, context: CustomerModerationContext) -> ModerationCheck:
        with self._logger.operation("ActiveFence Moderation Request"):
            analysis_context = AnalysisContext(
                session_id=context.session.id,
                customer_id=context.session.customer_id,
            )

            try:
                response = await self._client.evaluate_prompt(context.message, analysis_context)
            except Exception as e:
                raise Exception("Moderation service failure (ActiveFence)") from e

        return ModerationCheck(
            flagged=response.action == Actions.BLOCK,
            tags=[detection.type for detection in response.detections],
        )
