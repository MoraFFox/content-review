# BanShield

Video Ad Compliance Scanner powered by CrewAI, FastAPI, and Azure AI services.

## Features

- **Multi-Agent Orchestration**: CrewAI agents for compliance, vision, and audio analysis
- **FastAPI API**: RESTful endpoints for video upload and URL-based scanning
- **Azure AI Integration**: Vision analysis and LLM-based reasoning via Azure OpenAI
- **Vector Storage**: Qdrant for embedding and similarity search
- **Audio Transcription**: OpenAI Whisper for speech-to-text analysis
- **Playwright**: Browser automation for web-based ad capture

## Prerequisites

- Windows 10/11
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- Azure OpenAI resource
- Qdrant instance (local or cloud)

## Quick Start

### 1. Clone and enter the project

```powershell
cd banshield
```

### 2. Run the Windows setup script

```powershell
.\scripts\setup.ps1
```

Or manually:

```powershell
# Create virtual environment
uv venv

# Install dependencies
uv pip install -e ".[dev]"

# Install Playwright browsers
playwright install
```

### 3. Configure environment variables

```powershell
copy .env.example .env
```

Edit `.env` and fill in your Azure and Qdrant credentials:

```env
AZURE_API_KEY=your-azure-api-key-here
AZURE_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_API_VERSION=2024-10-21
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### 4. Run the application

```powershell
uv run banshield
```

Or directly:

```powershell
uv run python -m banshield.main
```

The API will be available at `http://localhost:8000`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/scan` | Upload and scan a video file |
| POST | `/api/v1/scan/url` | Scan a video from a URL |

## Development

### Run tests

```powershell
uv run pytest
```

### Run linting

```powershell
uv run ruff check .
uv run ruff format .
```

### Type checking

```powershell
uv run mypy src/banshield
```

## Project Structure

```
banshield/
├── src/banshield/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Settings management
│   ├── api/
│   │   ├── routes.py        # API endpoints
│   │   └── models.py        # Pydantic schemas
│   ├── agents/
│   │   ├── compliance_agent.py
│   │   ├── vision_agent.py
│   │   └── audio_agent.py
│   ├── services/
│   │   ├── azure_vision.py
│   │   ├── azure_reasoning.py
│   │   ├── whisper_service.py
│   │   └── qdrant_service.py
│   ├── crew/
│   │   └── compliance_crew.py
│   └── utils/
│       └── helpers.py
├── tests/                   # Test suite
├── data/                    # Data storage
├── scripts/
│   └── setup.ps1           # Windows setup script
├── pyproject.toml          # Project config & dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

## License

MIT
