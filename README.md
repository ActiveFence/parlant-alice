# parlant-activefence

ActiveFence integration for Parlant - A Python package for content moderation and threat detection.

## Installation

You can install `parlant-activefence` using pip:

```bash
pip install parlant-activefence
```

For development installation:

```bash
pip install -e ".[dev]"
```

## Usage

### Basic Usage

```python
from parlant.contrib.activefence import ActiveFence

# Initialize the client
client = ActiveFence(api_key="your-api-key")

# Analyze content for threats
result = client.analyze_content("This is some content to analyze")
print(result)

# Get threat intelligence
intel = client.get_threat_intelligence("malware")
print(intel)

# Report an incident
incident_data = {
    "type": "phishing",
    "description": "Suspicious email detected",
    "severity": "high"
}
report = client.report_incident(incident_data)
print(report)
```

### Advanced Usage

```python
from parlant.contrib.activefence import ActiveFence

# Initialize with custom base URL
client = ActiveFence(
    api_key="your-api-key",
    base_url="https://custom-api.activefence.com"
)

# Authenticate separately
client.authenticate("your-api-key")

# Analyze different content types
text_result = client.analyze_content("Text content", content_type="text")
image_result = client.analyze_content("base64_image_data", content_type="image")
```

## API Reference

### ActiveFence Class

#### `__init__(api_key=None, base_url=None)`

Initialize the ActiveFence client.

**Parameters:**
- `api_key` (str, optional): ActiveFence API key for authentication
- `base_url` (str, optional): Base URL for ActiveFence API

#### `authenticate(api_key)`

Authenticate with ActiveFence API.

**Parameters:**
- `api_key` (str): ActiveFence API key

**Returns:**
- `bool`: True if authentication successful

#### `analyze_content(content, content_type="text")`

Analyze content for threats and violations.

**Parameters:**
- `content` (str): Content to analyze
- `content_type` (str): Type of content (text, image, video, etc.)

**Returns:**
- `Dict[str, Any]`: Analysis results

#### `get_threat_intelligence(query)`

Retrieve threat intelligence information.

**Parameters:**
- `query` (str): Search query for threat intelligence

**Returns:**
- `Dict[str, Any]`: Threat intelligence data

#### `report_incident(incident_data)`

Report a security incident to ActiveFence.

**Parameters:**
- `incident_data` (Dict[str, Any]): Dictionary containing incident details

**Returns:**
- `Dict[str, Any]`: Report confirmation

## Development

### Setting up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/parlant/parlant-activefence.git
cd parlant-activefence
```

2. Install in development mode:
```bash
pip install -e ".[dev]"
```

3. Run tests:
```bash
pytest
```

4. Run linting:
```bash
flake8 parlant/
black parlant/
mypy parlant/
```

### Project Structure

```
parlant-activefence/
├── parlant/
│   ├── __init__.py
│   └── contrib/
│       ├── __init__.py
│       └── activefence/
│           ├── __init__.py
│           └── activefence.py
├── tests/
├── setup.py
├── pyproject.toml
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue on GitHub or contact the Parlant team at team@parlant.com.
