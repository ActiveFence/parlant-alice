from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock, create_autospec

import pytest
from wonderfence_sdk.client import AnalysisContext, WonderFenceV2Client
from wonderfence_sdk.models import Actions, DetectionResults, EvaluateMessageResponse, MessageType

import parlant.sdk as p
from parlant.contrib.alice import Alice
from parlant.contrib.alice.moderation_service import AliceModerationService
from parlant.core.nlp.moderation import CustomerModerationContext

API_KEY = "test-api-key"
APP_ID = "7f3c2a8e-1b4d-4e6f-9a0c-5d2e8b1f3a7c"
SESSION_ID = "session-1"
CUSTOMER_ID = "customer-1"
AGENT_ID = "agent-1"


@pytest.fixture(autouse=True)
def clear_alice_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("ALICE_API_KEY", "ALICE_APP_ID", "ALICE_BLOCKED_MESSAGE"):
        monkeypatch.delenv(name, raising=False)


def make_response(action: Actions, action_text: str | None = None) -> EvaluateMessageResponse:
    return EvaluateMessageResponse(
        correlation_id="correlation-1",
        action=action,
        action_text=action_text,
        detections=[DetectionResults(type="test_violation", score=0.9)],
    )


def make_alice(response: EvaluateMessageResponse) -> tuple[Alice, AsyncMock]:
    alice = Alice(api_key=API_KEY, app_id=APP_ID, blocked_message="blocked")
    mock_client = create_autospec(WonderFenceV2Client, instance=True)
    mock_client.evaluate_response.return_value = response
    mock_client.evaluate_prompt.return_value = response
    alice._client = mock_client
    return alice, mock_client


def make_real_client(response: EvaluateMessageResponse) -> tuple[WonderFenceV2Client, AsyncMock]:
    """A real client whose HTTP layer is stubbed, so the SDK's public method signatures are exercised."""
    client = WonderFenceV2Client(api_key=API_KEY)
    mock_http_call = AsyncMock(return_value=response)
    client._async_internal_call = mock_http_call  # type: ignore[method-assign]
    return client, mock_http_call


def make_engine_context(customer_id: str = CUSTOMER_ID) -> Any:
    return SimpleNamespace(
        session=SimpleNamespace(id=SESSION_ID, customer_id=customer_id),
        agent=SimpleNamespace(id=AGENT_ID, name="Otto Carmen"),
        logger=MagicMock(),
        tracer=SimpleNamespace(trace_id="trace-1"),
        session_event_emitter=AsyncMock(),
    )


class TestConstruction:
    def test_reads_api_key_and_app_id_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ALICE_API_KEY", API_KEY)
        monkeypatch.setenv("ALICE_APP_ID", APP_ID)

        actual = Alice()

        assert actual.api_key == API_KEY
        assert actual.app_id == APP_ID
        assert isinstance(actual._client, WonderFenceV2Client)

    def test_app_id_is_sent_in_canonical_form(self) -> None:
        actual = Alice(api_key=API_KEY, app_id="{" + APP_ID.upper() + "}")

        assert actual.app_id == APP_ID

    def test_missing_app_id_raises(self) -> None:
        with pytest.raises(ValueError, match="ALICE_APP_ID"):
            Alice(api_key=API_KEY)

    def test_non_uuid_app_id_raises(self) -> None:
        with pytest.raises(ValueError, match="must be a UUID"):
            Alice(api_key=API_KEY, app_id="my-app")

    def test_missing_api_key_raises(self) -> None:
        with pytest.raises(ValueError, match="ALICE_API_KEY"):
            Alice(app_id=APP_ID)


class TestResponseEvaluation:
    async def test_sends_app_id_session_and_customer_as_user(self) -> None:
        alice, mock_client = make_alice(make_response(Actions.NO_ACTION))

        await alice.check_message_compliance(make_engine_context(), "hello", None)

        mock_client.evaluate_response.assert_awaited_once_with(
            app_id=APP_ID,
            context=AnalysisContext(session_id=SESSION_ID, user_id=CUSTOMER_ID),
            response="hello",
        )

    async def test_reaches_the_sdk_v2_request_with_ids(self) -> None:
        alice = Alice(api_key=API_KEY, app_id=APP_ID)
        alice._client, mock_http_call = make_real_client(make_response(Actions.NO_ACTION))

        await alice.check_message_compliance(make_engine_context(), "hello", None)

        call = mock_http_call.await_args.kwargs
        assert call["type"] == MessageType.RESPONSE
        assert (call["app_id"], call["session_id"], call["user_id"], call["text"]) == (
            APP_ID,
            SESSION_ID,
            CUSTOMER_ID,
            "hello",
        )

    async def test_invalid_customer_id_is_wrapped(self) -> None:
        alice, _ = make_alice(make_response(Actions.NO_ACTION))

        with pytest.raises(Exception, match="Moderation service failure"):
            await alice.check_message_compliance(make_engine_context(customer_id="x" * 101), "hello", None)

    async def test_no_action_continues(self) -> None:
        alice, _ = make_alice(make_response(Actions.NO_ACTION))
        ctx = make_engine_context()

        actual = await alice.check_message_compliance(ctx, "hello", None)

        assert actual == p.EngineHookResult.CALL_NEXT
        ctx.session_event_emitter.emit_message_event.assert_not_awaited()

    async def test_detect_logs_and_continues(self) -> None:
        alice, _ = make_alice(make_response(Actions.DETECT))
        ctx = make_engine_context()

        actual = await alice.check_message_compliance(ctx, "hello", None)

        assert actual == p.EngineHookResult.CALL_NEXT
        ctx.logger.warning.assert_called_once()
        ctx.session_event_emitter.emit_message_event.assert_not_awaited()

    async def test_block_emits_blocked_message_and_bails(self) -> None:
        alice, _ = make_alice(make_response(Actions.BLOCK))
        ctx = make_engine_context()

        actual = await alice.check_message_compliance(ctx, "hello", None)

        assert actual == p.EngineHookResult.BAIL
        emitted = ctx.session_event_emitter.emit_message_event.await_args.kwargs["data"]
        assert emitted["message"] == "blocked"

    async def test_mask_emits_action_text_and_bails(self) -> None:
        alice, _ = make_alice(make_response(Actions.MASK, action_text="h***o"))
        ctx = make_engine_context()

        actual = await alice.check_message_compliance(ctx, "hello", None)

        assert actual == p.EngineHookResult.BAIL
        emitted = ctx.session_event_emitter.emit_message_event.await_args.kwargs["data"]
        assert emitted["message"] == "h***o"

    async def test_sdk_failure_is_wrapped(self) -> None:
        alice, mock_client = make_alice(make_response(Actions.NO_ACTION))
        mock_client.evaluate_response.side_effect = RuntimeError("boom")

        with pytest.raises(Exception, match="Moderation service failure"):
            await alice.check_message_compliance(make_engine_context(), "hello", None)


class TestPromptModeration:
    def make_service(self, response: EvaluateMessageResponse) -> tuple[AliceModerationService, AsyncMock]:
        mock_client = create_autospec(WonderFenceV2Client, instance=True)
        mock_client.evaluate_prompt.return_value = response
        service = AliceModerationService(MagicMock(), MagicMock(), mock_client, APP_ID)
        return service, mock_client

    def make_context(self, customer_id: str = CUSTOMER_ID) -> Any:
        session = SimpleNamespace(id=SESSION_ID, customer_id=customer_id)
        return CustomerModerationContext(session=session, message="hi there")  # type: ignore[arg-type]

    async def test_sends_app_id_session_and_customer_as_user(self) -> None:
        service, mock_client = self.make_service(make_response(Actions.NO_ACTION))

        await service.do_moderate(self.make_context())

        mock_client.evaluate_prompt.assert_awaited_once_with(
            app_id=APP_ID,
            context=AnalysisContext(session_id=SESSION_ID, user_id=CUSTOMER_ID),
            prompt="hi there",
        )

    async def test_reaches_the_sdk_v2_request_with_ids(self) -> None:
        client, mock_http_call = make_real_client(make_response(Actions.NO_ACTION))
        service = AliceModerationService(MagicMock(), MagicMock(), client, APP_ID)

        await service.do_moderate(self.make_context())

        call = mock_http_call.await_args.kwargs
        assert call["type"] == MessageType.PROMPT
        assert (call["app_id"], call["session_id"], call["user_id"], call["text"]) == (
            APP_ID,
            SESSION_ID,
            CUSTOMER_ID,
            "hi there",
        )

    async def test_invalid_customer_id_is_wrapped(self) -> None:
        service, _ = self.make_service(make_response(Actions.NO_ACTION))

        with pytest.raises(Exception, match="Moderation service failure"):
            await service.do_moderate(self.make_context(customer_id="   "))

    @pytest.mark.parametrize(
        ("action", "expected_flagged"),
        [(Actions.BLOCK, True), (Actions.MASK, False), (Actions.DETECT, False), (Actions.NO_ACTION, False)],
    )
    async def test_flags_only_block(self, action: Actions, expected_flagged: bool) -> None:
        service, _ = self.make_service(make_response(action))

        actual = await service.do_moderate(self.make_context())

        assert actual.flagged is expected_flagged
        assert actual.tags == ["test_violation"]

    async def test_sdk_failure_is_wrapped(self) -> None:
        service, mock_client = self.make_service(make_response(Actions.NO_ACTION))
        mock_client.evaluate_prompt.side_effect = RuntimeError("boom")

        with pytest.raises(Exception, match="Moderation service failure"):
            await service.do_moderate(self.make_context())
