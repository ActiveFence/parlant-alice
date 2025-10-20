# parlant-activefence

ActiveFence integration for Parlant - A Python package that provides content moderation and compliance checking for Parlant applications using ActiveFence's threat analysis & detection services.

## Installation

You can install `parlant-activefence` using pip:

```bash
pip install parlant-activefence
```

## Usage

### Basic Usage

The `parlant-activefence` package integrates with Parlant's framework to provide automatic content moderation and compliance checking. Here's how to use it:

```python
from parlant.contrib.activefence import ActiveFence

# Configure Parlant server to use ActiveFence moderation services
# Will use environment variables for configuration
async with p.Server(configure_container=ActiveFence().configure_container) as server:

```

At a minimum, an API key must be configured. This and more can be supplied using environment variables.
The following environment variables can be used to configure ActiveFence integration:

| Variable | Description | Default |
|----------|-------------|---------|
| `ACTIVEFENCE_API_KEY` | ActiveFence API key for authentication | None (required) |
| `ACTIVEFENCE_APP_NAME` | Application name for identification | Unknown |
| `ACTIVEFENCE_BLOCKED_MESSAGE` | Message to display when content is blocked | "The generated message was blocked by guardrails." |

These values can also be passed directly when initializing the container:

```python
from parlant.contrib.activefence import ActiveFence

moderation = ActiveFence(api_key="API_KEY",app_name="APP_NAME", blocked_message="This message was blocked")
async with p.Server(configure_container=moderation.configure_container) as server:
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.