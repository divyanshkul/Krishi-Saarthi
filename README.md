# Krishi Saarthi

Agentic AI-powered agricultural advisor platform serving India's 120 million farmers. Provides hyperlocal farming guidance, disease diagnosis, market intelligence, and crisis support through specialized AI models.

## Long Form Synopsis:

The Misfits - Paper: https://dub.sh/TheMisfitsSynopsisMain

## Demo Video:

Krishi Saarthi - Demo Video: https://dub.sh/TheMisfitsDemo

## Repository Structure

| Folder       | Description                                                                      |
| ------------ | -------------------------------------------------------------------------------- |
| `backend/`   | Python FastAPI backend with AI/ML orchestration                                  |
| `mobile/`    | Flutter cross-platform mobile application                                        |
| `core-ml/`   | ML models submodule hosted on Lightning AI CUDA server                           |
| `mlscripts/` | Training scripts for QLoRA fine-tuning, instruction-tuned TinyLlama, LSTM models |

## Architecture

- **Backend**: Python FastAPI with AI/ML orchestration
- **Mobile**: Flutter cross-platform application
- **AI Models**: LoRA-tuned VLM, Kisan Call Centre prompt-tuned TinyLlama, LSTM forecasting, Kisan Call Centre prompt-tuned TinyLlama, RAG based Agricultural scheme advisor
- **Data Sources**: Government APIs, KCC transcripts, agricultural datasets

## Prerequisites

### Backend Requirements

- Python 3.12
- Poetry (dependency management)

### Mobile Requirements

- Flutter SDK 3.0+
- Dart SDK
- Android Studio / VS Code
- Android SDK (for Android development)
- Xcode (for iOS development on macOS)

## Backend Setup

### 1. Install Poetry

```bash
# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### 2. Clone Submodules

```bash
git submodule update --init --recursive
```

### 3. Setup Backend

```bash
cd backend
poetry config virtualenvs.in-project true
poetry install --no-root
```

### 4. Run Backend

```bash
# Option 1: With Poetry
poetry run python main.py

# Option 2: Activate environment first
poetry shell
python main.py

# Option 3: With uvicorn
poetry run uvicorn main:app --reload
```

Backend will be available at http://localhost:8000
API documentation at http://localhost:8000/docs

## Mobile Setup

### 1. Install Flutter

#### Windows

```bash
# Download Flutter SDK from https://flutter.dev/docs/get-started/install/windows
# Extract and add to PATH
```

#### macOS

```bash
# Using Homebrew
brew install --cask flutter

# Or download from https://flutter.dev/docs/get-started/install/macos
```

#### Linux

```bash
# Download Flutter SDK
wget https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.16.0-stable.tar.xz
tar xf flutter_linux_3.16.0-stable.tar.xz
export PATH="$PATH:`pwd`/flutter/bin"
```

### 2. Verify Flutter Installation

```bash
flutter doctor
```

### 3. Setup Mobile App

```bash
cd mobile
flutter pub get
```

### 4. Run Mobile App

```bash
# List available devices
flutter devices

# Run on specific device
flutter run -d <device_id>

# Run on Android emulator
flutter run

# Run on iOS simulator (macOS only)
flutter run -d ios
```

## Development Workflow

### Start Both Applications

```bash
# Terminal 1 - Backend
cd backend
poetry shell
python main.py

# Terminal 2 - Mobile
cd mobile
flutter run
```

### API Testing

Import the Postman collection for comprehensive API testing:

- **Collection**: `backend/krishi_saarthi_production_postman_collection.json`
- **Base URL**: `http://localhost:8000`
- **Endpoints**: Chat processing, Twilio integration, mandi prices, government schemes, KCC advice, YouTube recommendations, guided farming mode

### Quick API Endpoints

- Health Check: `GET /health`
- API Health: `GET /api/health/`
- Sample: `GET /api/sample/`
- Hello: `GET /api/sample/hello/{name}`

## Project Structure

| Folder       | Description                                                                      |
| ------------ | -------------------------------------------------------------------------------- |
| `backend/`   | Python FastAPI backend with AI/ML orchestration                                  |
| `mobile/`    | Flutter cross-platform mobile application                                        |
| `core-ml/`   | ML models submodule hosted on Lightning AI CUDA server                           |
| `mlscripts/` | Training scripts for QLoRA fine-tuning, instruction-tuned TinyLlama, LSTM models |

```
krishi-saarthi/
├── backend/          # Python FastAPI backend
│   ├── main.py      # Application entry point
│   ├── pyproject.toml
│   └── app/         # Main application package
│       ├── api/     # API routes and endpoints
│       ├── core/    # Core configuration
│       ├── models/  # ML model loading and inference
│       ├── services/# Business logic services
│       ├── utils/   # Utility functions
│       └── schemas/ # API schemas
├── mobile/          # Flutter mobile application
│   ├── pubspec.yaml
│   └── lib/
├── core-ml/         # ML models submodule (Lightning AI CUDA server)
│   ├── models/      # Pre-trained AI models
│   ├── training/    # Training scripts and datasets
│   └── inference/   # Model inference services
└── mlscripts/       # Training scripts for QLoRA fine-tuning, instruction-tuned TinyLlama, LSTM models
```

## Troubleshooting

### Backend Issues

- Ensure Python 3.12 is installed
- Run `poetry install --no-root` if dependencies fail
- Check `poetry show` for installed packages

### Mobile Issues

- Run `flutter doctor` to check setup
- Ensure Android SDK is properly configured
- For iOS: Xcode must be installed on macOS
- Clear Flutter cache: `flutter clean && flutter pub get`

## Key Features

- Vision-based crop disease diagnosis
- LSTM price forecasting and market intelligence
- Multilingual conversational AI agent
- SMS fallback via Twilio integration
- Crisis detection and safety protocols
- Government scheme matching
