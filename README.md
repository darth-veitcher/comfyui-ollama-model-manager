# ComfyUI Ollama Model Manager# ComfyUI Ollama Model Manager



Custom nodes for managing [Ollama](https://ollama.com/) models in ComfyUI workflows. Load and unload models on-demand to optimize memory usage.Custom nodes for managing [Ollama](https://ollama.com/) models in ComfyUI workflows. Load and unload models on-demand to optimize memory usage in constrained environments.



## Features## Features



- 🔄 **Dynamic Model Selection** - Dropdown automatically populated from Ollama- 🔄 **Refresh Model List** - Fetch available models from Ollama

- 🎯 **Type-Safe Connections** - Client config passed between nodes- 🎯 **Select Model** - Choose from a dropdown (strongly-typed, no manual entry)

- ⬇️ **Load/Unload Models** - Control memory usage efficiently- ⬇️ **Load Model** - Load a model into Ollama's memory

- 📋 **Beautiful Logging** - Colored console output with JSON logs- ⬆️ **Unload Model** - Free up memory by unloading models

- 💾 **Model Caching** - Per-endpoint caching for better performance- 📋 **Beautiful Logging** - Colored console output with JSON file logs

- 🧵 **Thread-safe** - Concurrent workflow execution supported

## Installation

## Installation

### Via ComfyUI-Manager (Recommended)

### Recommended: ComfyUI-Manager

1. Install [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager)

2. Search for "Ollama Manager"1. Install via [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager)

3. Click Install2. Search for "Ollama Manager"

3. Click Install

### Manual Installation

### Manual Installation

```bash

cd ComfyUI/custom_nodes```bash

git clone https://github.com/darth-veitcher/comfyui-ollama-model-managercd ComfyUI/custom_nodes

cd comfyui-ollama-model-managergit clone https://github.com/darth-veitcher/comfyui-ollama-model-manager

cd comfyui-ollama-model-manager

# Install dependencies (auto-detects uv or pip)

python install.py# Install dependencies (auto-detects uv or uses pip)

```python install.py



## Architecture# OR manually with uv (recommended)

uv pip install httpx loguru rich

The package provides 4 nodes for a clean, composable workflow:

# OR manually with pip

```pip install httpx loguru rich

┌─────────────────┐```

│ Ollama Client   │  → Creates reusable connection config

└────────┬────────┘For portable ComfyUI installations:

         ↓ OLLAMA_CLIENT

┌─────────────────┐```bash

│ Model Selector  │  → Select model, optional refresh# Windows Portable

└────────┬────────┘ComfyUI\python_embeded\python.exe install.py

         ↓ (client, model)

┌─────────────────┐# Or manually

│ Load Model      │  → Load into memoryComfyUI\python_embeded\python.exe -m pip install httpx loguru rich

└────────┬────────┘```

         ↓ 

    [Processing]## Nodes

         ↓

┌─────────────────┐| Node | Description |

│ Unload Model    │  → Free memory|------|-------------|

└─────────────────┘| **Ollama Client** | Creates a reusable Ollama connection config |

```| **Ollama Model Selector** | Select model with optional auto-refresh |

| **Ollama Load Model** | Loads a model into Ollama's memory |

### Nodes| **Ollama Unload Model** | Unloads a model to free memory |



| Node | Inputs | Outputs | Purpose |## Usage

|------|--------|---------|---------|

| **Ollama Client** | endpoint (STRING) | client (OLLAMA_CLIENT) | Create connection config |The architecture provides a clean, composable workflow:

| **Model Selector** | client, model (COMBO), refresh (BOOL) | client, model, models_json | Select model with auto-refresh |

| **Load Model** | client, model, keep_alive (STRING) | client, result | Load model into memory |```text

| **Unload Model** | client, model | client, result | Unload model to free memory |[Ollama Client] → [Model Selector] → [Load Model] → [Your Processing] → [Unload Model]

       ↓               ↓                   ↓

## Usage  (endpoint)     (pick model,        (load with

                  auto-refresh)       keep_alive)

### Basic Workflow```



1. **Add Ollama Client****Key Benefits:**

   - Set `endpoint`: `http://localhost:11434`- **Reusable Client**: Create one client, connect to multiple nodes

- **Auto-refresh**: Model Selector can refresh the list automatically

2. **Add Model Selector**- **Type Safety**: Client connection passed between nodes

   - Connect `client` from Ollama Client- **Cleaner Workflows**: Less redundant endpoint configuration

   - Set `refresh`: `true` (first time)- **Dynamic Dropdowns**: Model list automatically populates after refresh

   - Execute workflow to fetch models

   - Select model from dropdown**Example Workflow:**



3. **Add Load Model**```text

   - Connect `client` from Model Selector1. Ollama Client (endpoint: http://localhost:11434)

   - Model dropdown auto-populates after refresh       ↓

   - Set `keep_alive`: `-1` (keep loaded)2. Model Selector (model: "llama3.2", refresh: true)

       ↓

4. **[Your Ollama Processing Nodes]**3. Load Model (keep_alive: "-1")

       ↓

5. **Add Unload Model**4. [Your Ollama Processing Nodes]

   - Connect to free memory when done       ↓

5. Unload Model

### Keep Alive Options```



Control how long models stay in memory:This pattern optimizes memory by unloading models when not needed.

- `-1`: Keep loaded indefinitely (default)

- `5m`: Keep for 5 minutes## Configuration

- `1h`: Keep for 1 hour

- `0`: Unload immediately after use### Ollama Endpoint



## ConfigurationDefault: `http://localhost:11434`



### Default EndpointOverride by specifying a different endpoint in the "Refresh Model List" or "Load/Unload" nodes.



Default: `http://localhost:11434`### Keep Alive



Override by setting a different endpoint in the Ollama Client node.Control how long models stay in memory:

- `-1` (default): Keep loaded indefinitely

### Model Refresh- `5m`: Keep for 5 minutes

- `1h`: Keep for 1 hour

The Model Selector caches models per endpoint. Set `refresh=true` and execute the workflow to:- `0`: Unload immediately

- Fetch current model list from Ollama

- Update cache## Logging

- Populate dropdowns on all connected nodes

Logs are written to:

## Logging- **Console**: Colored output with timestamps

- **File**: `logs/ollama_manager.json` (14-day retention, compressed)

Logs written to:

- **Console**: Colored output with emoji indicatorsExample log output:

- **File**: `logs/ollama_manager.json` (14-day retention)```

08:36:30 | INFO     | refresh-abc123 | 🔄 Refreshing model list from http://localhost:11434

Example output:08:36:30 | INFO     | refresh-abc123 | ✅ Model list refreshed: 3 models available

```08:36:31 | INFO     | load-def456    | ⬇️  Loading model 'llava:latest' (keep_alive=-1)

12:49:03 | INFO | client-abc123 | 🔌 Created Ollama client for http://localhost:1143408:36:32 | INFO     | load-def456    | ✅ Model 'llava:latest' loaded successfully

12:49:03 | INFO | select-def456 | 🔄 Refreshing model list from http://localhost:11434```

12:49:03 | INFO | select-def456 | ✅ Model list refreshed: 3 models available

12:49:03 | INFO | load-ghi789   | 🚀 Loading model 'llama3.2' from http://localhost:11434## Requirements

12:49:03 | INFO | load-ghi789   | ✅ Model 'llama3.2' loaded successfully

```- Python ≥3.12

- httpx ≥0.28.1

## Requirements- loguru ≥0.7.3

- rich ≥14.2.0

- Python ≥3.12- [Ollama](https://ollama.com/) running locally or remotely

- httpx ≥0.28.1

- loguru ≥0.7.3## Development

- [Ollama](https://ollama.com/) running locally or remotely

### Project Structure

## Development

```text

### Project Structurecomfyui-ollama-model-manager/

├── __init__.py              # ComfyUI entry point

```├── install.py               # Dependency installer (uv/pip auto-detect)

comfyui-ollama-model-manager/├── pyproject.toml           # Package metadata & dependencies

├── __init__.py              # ComfyUI entry point├── src/

├── install.py               # Dependency installer│   └── comfyui_ollama_model_manager/

├── pyproject.toml           # Package metadata│       ├── __init__.py      # Package init

├── src/│       ├── nodes.py         # Node definitions

│   └── comfyui_ollama_model_manager/│       ├── ollama_client.py # API client

│       ├── nodes.py         # 4 node definitions│       ├── state.py         # Model cache

│       ├── ollama_client.py # API client│       ├── log_config.py    # Logging setup

│       ├── state.py         # Model cache│       └── async_utils.py   # Async utilities

│       ├── log_config.py    # Logging setup└── tests/                   # Pytest test suite

│       └── async_utils.py   # Async utilities```

├── tests/                   # 29 passing tests

└── web/### Running Tests

    └── ollama_widgets.js    # Dynamic dropdown UI

``````bash

# With uv (recommended)

### Running Testsuv run pytest



```bash# Or with pip

uv run pytestpip install pytest pytest-asyncio

```pytest

```

## Troubleshooting

## Troubleshooting

### Models not appearing in dropdown

### Nodes don't appear in ComfyUI

1. Connect Ollama Client to Model Selector

2. Set `refresh=true`1. Check that dependencies are installed: `pip list | grep -E "httpx|loguru|rich"`

3. Execute workflow (Queue Prompt)2. Restart ComfyUI completely

4. Dropdown updates after execution3. Check ComfyUI console for error messages

4. Verify Ollama is running: `curl http://localhost:11434/api/tags`

### Nodes don't appear

### Import errors

1. Check dependencies: `pip list | grep -E "httpx|loguru"`

2. Restart ComfyUI completelyIf you see `ModuleNotFoundError`, install dependencies manually:

3. Check console for errors```bash

pip install httpx loguru rich

### Import errors```



```bash### Permission errors (Windows)

pip install httpx loguru

```Close ComfyUI and run:

```bash

## LicenseComfyUI\python_embeded\python.exe -m pip install --upgrade httpx loguru rich

```

MIT

## License

## Credits

[Add your license here]

- Built for [ComfyUI](https://github.com/comfyanonymous/ComfyUI)

- Uses [Ollama](https://ollama.com/) API## Credits


- Built for [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- Uses [Ollama](https://ollama.com/) API
