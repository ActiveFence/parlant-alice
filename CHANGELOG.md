# Changelog

## 0.2.0

### Breaking changes

- Messages are evaluated through the WonderFence v2 API (`/v2/evaluate/message`) using `WonderFenceV2Client`, so they are evaluated against the policies assigned to a specific application in the Application Inventory.
- `app_id` (or the `ALICE_APP_ID` environment variable) is required and must be the application's UUID. `Alice` raises a `ValueError` at construction when it is missing or is not a UUID.
- `app_name`, the `Alice.app_name` attribute and the `ALICE_APP_NAME` environment variable are removed. The v1 model-context variables (`ALICE_MODEL_PROVIDER`, `ALICE_MODEL_NAME`, `ALICE_MODEL_VERSION`, `ALICE_PLATFORM`) are no longer sent; the v2 API does not take them.
- `Alice.check_message` takes `customer_id` instead of `agent_id`. `AliceNLPServiceWrapper` and `AliceModerationService` take an `app_id` argument after the client.
- Requires `wonderfence-sdk>=3.0.0,<4`.

### Fixes

- Works with `wonderfence-sdk` 3.x: the SDK is called with keyword arguments, and `session_id` and `user_id` are always sent. 0.1.x failed on every evaluation against `wonderfence-sdk` 3.x, which a fresh install resolves to.
- Customer messages send the session's customer ID as `user_id`. 0.1.x passed it as `customer_id`, which the SDK ignored, so no user was sent.
- Agent replies send the session's customer ID as `user_id` too, so both sides of a conversation share one user. 0.1.x sent the agent ID.
- An invalid session or customer ID (empty, whitespace-only, or over 100 characters) is reported as a moderation service failure, like any other evaluation error.
