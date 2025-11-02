# Custom Web Extensions for Ollama Model Manager

This directory contains JavaScript extensions that enhance the ComfyUI nodes with dynamic dropdowns.

## Files

### `ollama_widgets.js`
Implements dynamic model dropdown updates for Ollama nodes.

## How It Works

1. **User connects nodes**: `OllamaClient` → `OllamaModelSelector` → `OllamaLoadModel`
2. **User executes workflow**: With `refresh=true` on `OllamaModelSelector`
3. **Python backend**: Fetches models from Ollama API (no CORS issues)
4. **JavaScript updates**: Parses execution results and updates all model dropdowns

## Features

- ✅ **Dynamic dropdowns** - Model lists update automatically after execution
- ✅ **No CORS issues** - All API calls through Python backend
- ✅ **Downstream propagation** - Load/Unload nodes get updated automatically
- ✅ **Custom styling** - Clean, readable dropdown display
- ✅ **Cached models** - Persists between workflow executions

## Architecture

The JavaScript hooks into ComfyUI's execution lifecycle:
- `onExecuted`: Updates dropdowns when `OllamaModelSelector` executes
- `onConnectionsChange`: Logs connection events for debugging
- `updateModelDropdown`: Helper function to refresh COMBO widgets

All model fetching happens in Python to avoid browser CORS restrictions.
