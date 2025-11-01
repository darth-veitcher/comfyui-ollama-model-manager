# ComfyUI Ollama Model Manager

Custom nodes for managing [Ollama](https://ollama.com/) models in ComfyUI workflows. Load and unload models on-demand to optimize memory usage in constrained environments.

## Features

- 🔄 **Refresh Model List** - Fetch available models from Ollama
- 🎯 **Select Model** - Choose from a dropdown (strongly-typed, no manual entry)
- ⬇️ **Load Model** - Load a model into Ollama's memory
- ⬆️ **Unload Model** - Free up memory by unloading models
- 📋 **Beautiful Logging** - Colored console output with JSON file logs
- 🧵 **Thread-safe** - Concurrent workflow execution supported

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

## Nodes

| Node | Description |
|------|-------------|
| **Ollama (Refresh Model List)** | Fetches available models from Ollama API (`/api/tags`) |
| **Ollama (Select Model)** | Presents cached models as a dropdown selector |
| **Ollama (Load Selected Model)** | Loads the selected model into memory |
| **Ollama (Unload Selected Model)** | Unloads the model to free memory |

## Example Workflow

```text
Refresh Model List → Select Model → Load Model → [Your Ollama Node] → Unload Model
```

**Typical use case:**

```text
Refresh Models → Select "llava:latest" → Load Model → 
  Caption Image with LLaVA → Unload Model → 
  Text to Image with Stable Diffusion
```

This pattern ensures you can use vision/language models without keeping them loaded during image generation.

### Important: Refreshing Dropdowns

After running the "Refresh Model List" node:

1. **Right-click** on Select/Load/Unload nodes
2. Choose **"Refresh"** from the context menu
3. The dropdown will update with the latest models

Alternatively, reload your workflow file to refresh all node dropdowns.

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
