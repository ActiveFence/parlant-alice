# parlant-activefence

ActiveFence integration for Parlant - A Python package that provides content moderation and compliance checking for Parlant applications using ActiveFence's threat analysis & detection services.


## Introduction
ActiveFence’s Trust and Safety (T&S) is the world’s leading tool stack for Trust & Safety teams. With ActiveFence’s end-to-end solution, Trust & Safety teams of all sizes can protect users from malicious activity and online harm – regardless of content format, language or abuse area. Integrating with the T&S platform enables you to detect, collect and analyze harmful content that may put your users and brand at risk. By combining AI and a team of subject-matter experts, the ActiveFence T&S platform enables you to be agile and proactive for maximum efficiency, scalability and impact.

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

### Impact

Using ActiveFence's moderation as shown will Analyze messages sent by the user to the AI agent, and the response by the AI agent to the user.
This way, you can handle abusive messages from users and shield the application from malicious prompts, as well as make sure the agent responses align to your policies.

User messages blocked by ActiveFence will not reach the agent, but it will get a flagged message indication a censored user request. You can guide the agent to respond to such messages using the Parlant guidelines, like so:
```python
await agent.create_guideline(
        condition="the customer's last message is censored",
        action="respond with a polite refusal to answer the question, mention that the message was censored based on guardrails analysis",
    )
```

Analysis of the agent responses works a bit different. When a policy violation is detected, a warning is logged using Parlant's internal logger. This warning message will look like this:
[warning  ] [ReuwnpD7Gzn::process][MessageEventComposer][CannedResponseGenerator] Prevented sending a non-compliant message: 'However, I can't respond to your previous message because it was censored based on our guardrails analysis. If you have another question or need assistance, feel free to ask.'.

If the ActiveFence analysis marks the response as BLOCKED, the message itself will not be returned to the user, and instead a preconfigured block message will be returned.
This message can be configured as described above.

### Example

Here is a complete example of setting up a Parlant server with ActiveFence moderation:
```python
import asyncio
import parlant.sdk as p
from parlant.contrib.activefence import ActiveFence

async def main():
    async with p.Server(configure_container=ActiveFence(api_key="<API_KEY>",app_name="test").configure_container) as server:
        agent = await server.create_agent(
            name="Otto Carmen",
            description="You work at a computer parts store",
        )
        print(agent.id)

        blocked = await agent.create_guideline(
            condition="the customer's last message is censored",
            action="respond with a polite refusal to answer the question, mention that the message was censored based on guardrails analysis",
        )

asyncio.run(main())
```

And this is an example of a basic client that calls this server, and prints the messages returned by the agent to the console:
```python
import asyncio
from parlant.client import ParlantClient

async def main():

    client = ParlantClient(base_url='http://localhost:8800')
    session = client.sessions.create(
        agent_id='<AGENT ID>',
        allow_greeting=False,
        title="test",
    )
    session_id = session.id
    client.sessions.create_event(
        session_id,
        kind="message",
        source="customer",
        message='Should I sue about this?',
        moderation="auto",
    )

    last_offset = 0
    while (True):
        try:
            events = client.sessions.list_events(session_id=session_id,
                min_offset=last_offset,
                wait_for_data=30,
                kinds="message",
            )
            for event in events:
                print(event)
                last_offset = max(last_offset, event.offset + 1)
        except Exception as e:
            print(e)

asyncio.run(main())
```

Enabled moderation="auto" will trigger the user prompt analysis, and if the ActiveFence policy is configured for it, it will block the message for including legal advice, even if the LLM is not configured to respond to this.
## License

This project is licensed under the MIT License - see the LICENSE file for details.