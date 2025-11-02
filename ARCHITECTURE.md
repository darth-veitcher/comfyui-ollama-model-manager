# Architecture

## Overview

The ComfyUI Ollama Model Manager has been refactored into a cleaner, more composable architecture that separates concerns and provides better reusability.

## Node Architecture

### New Design (v2)

```
┌─────────────────┐
│ Ollama Client   │  → Creates OLLAMA_CLIENT config
└────────┬────────┘
         │ (client: OLLAMA_CLIENT)
         ↓
┌──────────────────┐
│ Model Selector   │  → Selects model, optional auto-refresh
└────────┬─────────┘
         │ (client: OLLAMA_CLIENT, model: STRING)
         ↓
┌──────────────────┐
│ Load/Unload Model│  → Operations on selected model
└──────────────────┘
```

### Components

#### 1. OllamaClient
**Purpose**: Configuration node that creates a reusable client connection

**Inputs**:
- `endpoint` (STRING): Ollama server URL

**Outputs**:
- `client` (OLLAMA_CLIENT): Connection config dict

**Benefits**:
- Single source of truth for endpoint
- Can be connected to multiple downstream nodes
- Type-safe connection passing

#### 2. OllamaModelSelector
**Purpose**: Model selection with optional refresh capability

**Inputs**:
- `client` (OLLAMA_CLIENT): Connection from OllamaClient
- `model` (STRING): Model name to select
- `refresh` (BOOLEAN, optional): Whether to refresh model list

**Outputs**:
- `client` (OLLAMA_CLIENT): Pass-through for chaining
- `model` (STRING): Selected model name

**Benefits**:
- Auto-refresh when connected
- Manual refresh button available
- Passes client through for chaining

#### 3. OllamaLoadModel / OllamaUnloadModel
**Purpose**: Load or unload models from memory

**Inputs**:
- `client` (OLLAMA_CLIENT): Connection config
- `model` (STRING): Model to load/unload
- `keep_alive` (STRING, Load only): How long to keep in memory
- `dependencies` (*,  optional): For control flow

**Outputs**:
- `client` (OLLAMA_CLIENT): Pass-through for chaining
- `result` (STRING): JSON response from Ollama
- `dependencies` (*): Pass-through for control flow

**Benefits**:
- No need to specify endpoint multiple times
- Clean chaining with client pass-through
- Control flow support via dependencies

## Custom Types

### OLLAMA_CLIENT
A custom ComfyUI type that represents an Ollama connection configuration.

**Structure**:
```python
{
    "endpoint": str,  # Ollama server URL
    "type": "ollama_client"  # Type identifier
}
```

**Benefits**:
- Type-safe connections in ComfyUI graph
- Visual distinction from plain STRING types
- Can be extended with auth, headers, etc.

## Legacy Nodes

For backwards compatibility, the following legacy nodes are still available:

- **OllamaRefreshModelList**: Fetches and displays model list
- **OllamaSelectModel**: Manual model selection with dropdown

These nodes are marked as `[Legacy]` in the UI and will be maintained for existing workflows.

## Frontend (JavaScript)

### Widget System

The `web/ollama_widgets.js` file provides custom ComfyUI widgets:

1. **Custom Display Widget**: Shows model list in OllamaRefreshModelList
2. **Dynamic Dropdowns**: Converts STRING inputs to COMBO dropdowns when connected
3. **Auto-update**: Refreshes dropdowns when source nodes execute

### How it Works

1. **Connection Detection**: Watches for `onConnectionsChange` events
2. **Model Extraction**: Uses `getModelsFromConnectedNode()` helper
3. **Widget Conversion**: Converts STRING widget to COMBO with model list
4. **State Management**: Restores dropdowns when loading workflows

### Supported Connections

- New Architecture: `OllamaModelSelector` → Load/Unload nodes
- Legacy: `OllamaRefreshModelList` → Load/Unload nodes

## State Management

### Model Cache

Models are cached at the module level in `state.py`:

```python
_models_cache: dict[str, list[str]] = {}
```

**Key**: Ollama endpoint URL
**Value**: List of model names

**Benefits**:
- Shared across all node instances
- Reduces redundant API calls
- Persists during ComfyUI session

## Testing

All nodes have comprehensive test coverage:

- Unit tests for each node class
- Mocked HTTP calls
- Async operation testing
- 36 passing tests with 0 warnings

Run tests with:
```bash
uv run pytest -v
```

## Migration Guide

### From Legacy to New Architecture

**Before (Legacy)**:
```text
Refresh Model List → Select Model → Load Model
```

**After (New)**:
```text
Ollama Client → Model Selector → Load Model
```

**Benefits of Migration**:
1. **Fewer nodes**: Client config can be reused
2. **Cleaner workflows**: Less visual clutter
3. **Better typing**: Type-safe connections
4. **Auto-refresh**: Model list updates automatically

**No Breaking Changes**: Legacy nodes remain available

## Development

### Adding New Features

1. **New Node**: Add class to `nodes.py`
2. **Register**: Update `__init__.py` NODE_CLASS_MAPPINGS
3. **Tests**: Add test class to `test_nodes.py`
4. **JavaScript**: Update `ollama_widgets.js` if needed

### Custom Types

To add new custom types (like OLLAMA_CLIENT):

1. Define in node's RETURN_TYPES tuple
2. Use in downstream INPUT_TYPES
3. Pass dict/object with type identifier

ComfyUI will automatically create visual distinction.

## Future Enhancements

Possible improvements:

- [ ] Authentication support in OLLAMA_CLIENT
- [ ] Batch model operations
- [ ] Model search/filter in selector
- [ ] Persistent model preferences
- [ ] Connection pooling
- [ ] Health check node
