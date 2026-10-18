from typing_extensions import override
from wonderfence_sdk.client import AnalysisContext, WonderFenceV2Client
from wonderfence_sdk.models import Actions

from parlant.core.loggers import Logger
from parlant.core.meter import Meter
from parlant.core.nlp.embedding import Embedder
from parlant.core.nlp.generation import SchematicGenerator, StreamingTextGenerator, T
from parlant.core.nlp.moderation import (
    BaseModerationService,
    CustomerModerationContext,
    ModerationCheck,
    ModerationService,
)
from parlant.core.nlp.service import EmbedderHints, NLPService, SchematicGeneratorHints, StreamingTextGeneratorHints


class AliceNLPServiceWrapper(NLPService):
    def __init__(
        self,
        original_nlp_service: NLPService,
        alice_client: WonderFenceV2Client,
        app_id: str,
        logger: Logger,
        meter: Meter,
    ):
        self._original_nlp_service = original_nlp_service
        self._alice_client = alice_client
        self._app_id = app_id
        self._logger = logger
        self._meter = meter

    @property
    def supports_streaming(self) -> bool:
        return self._original_nlp_service.supports_streaming

    async def get_schematic_generator(self, t: type[T], hints: SchematicGeneratorHints = {}) -> SchematicGenerator[T]:
        return await self._original_nlp_service.get_schematic_generator(t, hints)

    async def get_streaming_text_generator(self, hints: StreamingTextGeneratorHints = {}) -> StreamingTextGenerator:
        return await self._original_nlp_service.get_streaming_text_generator(hints)

    async def get_embedder(self, hints: EmbedderHints = {}) -> Embedder:
        return await self._original_nlp_service.get_embedder(hints)

    async def get_moderation_service(self) -> ModerationService:
        return AliceModerationService(self._logger, self._meter, self._alice_client, self._app_id)


class AliceModerationService(BaseModerationService):
    def __init__(self, logger: Logger, meter: Meter, client: WonderFenceV2Client, app_id: str) -> None:
        super().__init__(logger, meter)
        self._client = client
        self._app_id = app_id

    @override
    async def do_moderate(self, context: CustomerModerationContext) -> ModerationCheck:
        with self.logger.scope("Alice Moderation Request"):
            try:
                analysis_context = AnalysisContext(session_id=context.session.id, user_id=context.session.customer_id)
                response = await self._client.evaluate_prompt(
                    app_id=self._app_id, context=analysis_context, prompt=context.message
                )
            except Exception as e:
                raise Exception("Moderation service failure (Alice)") from e

        return ModerationCheck(
            flagged=response.action == Actions.BLOCK,
            tags=[detection.type for detection in response.detections],
        )
