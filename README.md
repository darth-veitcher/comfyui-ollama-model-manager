# ComfyUI Ollama Model Manager

Custom nodes for managing [Ollama](https://ollama.com/) models in ComfyUI workflows. Load and unload models on-demand to optimize memory usage in constrained environments.

## Features

- � **Auto-Fetch Models** - Models load automatically when you connect nodes (no workflow execution needed!)
- 🔄 **Dynamic Dropdowns** - Model list updates instantly via ComfyUI API
- 🎯 **Type-Safe Connections** - Client config passed between nodes
- ⬇️ **Load/Unload Models** - Control memory usage efficiently
- 📋 **Beautiful Logging** - Colored console output with JSON file logs
- 💾 **Model Caching** - Per-endpoint caching for better performance
- ✨ **No CORS Issues** - Backend API proxy eliminates browser restrictions

## Installation

### Recommended: ComfyUI-Manager

1. Install via [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager)
2. Search for "Ollama Manager"
3. Click Install

### Manual Installation

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/darth-veitcher/comfyui-ollama-model-manager
cd comfyui-ollama-model-manager

# Install dependencies (auto-detects uv or uses pip)
python install.py

# OR manually with uv (recommended)
uv pip install httpx loguru rich

# OR manually with pip
pip install httpx loguru rich
```

For portable ComfyUI installations:

```bash
# Windows Portable
ComfyUI\python_embeded\python.exe install.py

# Or manually
ComfyUI\python_embeded\python.exe -m pip install httpx loguru rich
```

## 🎯 Quick Start Guide

### Step 1: Add Ollama Client

1. Add an **Ollama Client** node to your workflow
2. Set `endpoint` to your Ollama server URL
   - Default: `http://localhost:11434`
   - Or use your remote server URL

### Step 2: Add Model Selector

1. Add an **Ollama Model Selector** node
2. Connect the `client` output from **Ollama Client** to the `client` input
3. **✨ Models auto-fetch immediately!** - No need to execute the workflow
4. Select your desired model from the dropdown

### Step 3: Load the Model

1. Add an **Ollama Load Model** node
2. Connect `client` from **Model Selector**
3. The model dropdown auto-populates with available models
4. Set `keep_alive` (default `-1` keeps it loaded)
5. Execute the workflow to load the model

### Step 4: Use Your Model

Connect to your Ollama processing nodes (text generation, embeddings, etc.)

### Step 5: Unload When Done (Optional)

1. Add an **Ollama Unload Model** node
2. Connect it after your processing
3. This frees up memory

## Nodes Reference

| Node | Description |
|------|-------------|
| **Ollama Client** | Creates a reusable Ollama connection config |
| **Ollama Model Selector** | Select model with auto-fetch on connection |
| **Ollama Load Model** | Loads a model into Ollama's memory |
| **Ollama Unload Model** | Unloads a model to free memory |

## Advanced Usage

The architecture provides a clean, composable workflow:

```text
[Ollama Client] → [Model Selector] → [Load Model] → [Your Processing] → [Unload Model]
       ↓               ↓                   ↓
  (endpoint)     (pick model,        (load with
                  auto-refresh)       keep_alive)
```

**Key Benefits:**
- **Reusable Client**: Create one client, connect to multiple nodes
- **Auto-refresh**: Model Selector can refresh the list automatically
- **Type Safety**: Client connection passed between nodes
- **Cleaner Workflows**: Less redundant endpoint configuration
- **Dynamic Dropdowns**: Model list automatically populates after refresh

**Example Workflow:**

```text
1. Ollama Client (endpoint: http://localhost:11434)
       ↓
2. Model Selector (model: "llama3.2", refresh: true)
       ↓
3. Load Model (keep_alive: "-1")
       ↓
4. [Your Ollama Processing Nodes]
       ↓
5. Unload Model
```

This pattern optimizes memory by unloading models when not needed.

## Configuration

### Ollama Endpoint

Default: `http://localhost:11434`

Override by specifying a different endpoint in the "Refresh Model List" or "Load/Unload" nodes.

### Keep Alive

Control how long models stay in memory:
- `-1` (default): Keep loaded indefinitely
- `5m`: Keep for 5 minutes
- `1h`: Keep for 1 hour
- `0`: Unload immediately

## Logging

Logs are written to:
- **Console**: Colored output with timestamps
- **File**: `logs/ollama_manager.json` (14-day retention, compressed)

Example log output:
```
08:36:30 | INFO     | refresh-abc123 | 🔄 Refreshing model list from http://localhost:11434
08:36:30 | INFO     | refresh-abc123 | ✅ Model list refreshed: 3 models available
08:36:31 | INFO     | load-def456    | ⬇️  Loading model 'llava:latest' (keep_alive=-1)
08:36:32 | INFO     | load-def456    | ✅ Model 'llava:latest' loaded successfully
```

## Requirements

- Python ≥3.12
- httpx ≥0.28.1
- loguru ≥0.7.3
- rich ≥14.2.0
- [Ollama](https://ollama.com/) running locally or remotely

## Development

### Project Structure

```text
comfyui-ollama-model-manager/
├── __init__.py              # ComfyUI entry point
├── install.py               # Dependency installer (uv/pip auto-detect)
├── pyproject.toml           # Package metadata & dependencies
├── src/
│   └── comfyui_ollama_model_manager/
│       ├── __init__.py      # Package init
│       ├── nodes.py         # Node definitions
│       ├── ollama_client.py # API client
│       ├── state.py         # Model cache
│       ├── log_config.py    # Logging setup
│       └── async_utils.py   # Async utilities
└── tests/                   # Pytest test suite
```

### Running Tests

```bash
# With uv (recommended)
uv run pytest

# Or with pip
pip install pytest pytest-asyncio
pytest
```

## Troubleshooting

### Nodes don't appear in ComfyUI

1. Check that dependencies are installed: `pip list | grep -E "httpx|loguru|rich"`
2. Restart ComfyUI completely
3. Check ComfyUI console for error messages
4. Verify Ollama is running: `curl http://localhost:11434/api/tags`

### Import errors

If you see `ModuleNotFoundError`, install dependencies manually:
```bash
pip install httpx loguru rich
```

### Permission errors (Windows)

Close ComfyUI and run:
```bash
ComfyUI\python_embeded\python.exe -m pip install --upgrade httpx loguru rich
```

## License

[Add your license here]

## Credits

- Built for [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- Uses [Ollama](https://ollama.com/) API
