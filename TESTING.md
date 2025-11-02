# Testing the New Architecture

## How the Model Selector Works

The `OllamaModelSelector` node now properly outputs the models list for downstream nodes:

### Workflow Setup

1. **Add OllamaClient node**
   - Set endpoint: `http://localhost:11434` (or your Ollama server)

2. **Add OllamaModelSelector node**
   - Connect `client` from OllamaClient
   - Type a model name (or it will show dropdown once refreshed)
   - Set `refresh` to `true` to fetch the model list

3. **Add OllamaLoadModel node**
   - Connect `client` from OllamaModelSelector
   - The `model` field should automatically become a dropdown with available models!

4. **Execute the workflow**
   - Run OllamaClient first
   - Then run OllamaModelSelector with `refresh=true`
   - The Load node's model dropdown should populate automatically

### What Happens

1. **OllamaModelSelector executes** with `refresh=true`:
   - Fetches models from Ollama API
   - Caches them in memory
   - Returns: `(client, model, models_json)`
   - Sends UI message with models_json

2. **JavaScript widget receives the message**:
   - Parses the models_json
   - Updates OllamaModelSelector's own dropdown
   - **Pushes update to downstream nodes** connected via client output
   - Converts STRING inputs to COMBO dropdowns

3. **Load/Unload nodes update**:
   - When connected to OllamaModelSelector via client
   - JavaScript detects the connection
   - Automatically populates model dropdown
   - No need to manually type model names!

### Expected Behavior

**Before refresh:**
- Load/Unload nodes show text input for model

**After refresh:**
- Model input becomes a dropdown
- Shows all available models from Ollama
- Can select from list instead of typing

### Debug Console Messages

When working correctly, you should see:
```
[Ollama] OllamaModelSelector executed with X models
[Ollama] Updating dropdown on downstream node: OllamaLoadModel
[Ollama] Updated dropdown with X models
```

### Common Issues

**Dropdown not appearing:**
1. Make sure OllamaModelSelector has been executed at least once
2. Check that `refresh` is set to `true` on first run
3. Verify client connection is properly linked
4. Check browser console for JavaScript errors

**No models in dropdown:**
1. Verify Ollama server is running
2. Check endpoint URL is correct
3. Make sure you have models pulled in Ollama (`ollama list`)
4. Check ComfyUI console for error messages

### Comparison with Legacy

**Legacy workflow:**
```
OllamaRefreshModelList → models_json → OllamaLoadSelectedModel
```

**New workflow:**
```
OllamaClient → OllamaModelSelector → OllamaLoadModel
            ↓          (with refresh)        ↓
        (client)                          (client)
```

**Key difference:**
- New: Models flow through client connection
- Legacy: Models flow through explicit models_json output
- New: One refresh button on selector
- Legacy: Separate refresh node

Both work, but the new architecture is cleaner!
