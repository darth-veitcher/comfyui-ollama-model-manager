# ComfyUI Ollama Model Manager

Custom nodes for managing [Ollama](https://ollama.com/) models in ComfyUI workflows. Load and unload models on-demand to optimize memory usage in constrained environments.

## Features

- 🔄 **Auto-Fetch Models** - Models load automatically when you connect nodes (no workflow execution needed!)
- 💬 **Chat Completion** - Full text generation with conversation history
- 🔄 **Dynamic Dropdowns** - Model list updates instantly via ComfyUI API
- 🎯 **Type-Safe Connections** - Client config passed between nodes
- ⬇️ **Load/Unload Models** - Control memory usage efficiently
- 📋 **Beautiful Logging** - Colored console output with JSON file logs
- 💾 **Model Caching** - Per-endpoint caching for better performance
- ✨ **No CORS Issues** - Backend API proxy eliminates browser restrictions

## � Screenshots

<!-- TODO: Add workflow screenshots here -->
_Screenshots coming soon! See the [Quick Start Guide](#-quick-start-guide) below to get started._

## �🚀 30-Second Quickstart

**Want to test it right now?**

1. **Install Ollama**: Download from [ollama.com](https://ollama.com/) and run `ollama pull llama3.2`
2. **Install this extension**: Via ComfyUI-Manager, search "Ollama Manager"
3. **Add 3 nodes**: `Ollama Client` → `Ollama Model Selector` → `Ollama Chat Completion`
4. **Type a prompt**: "Write a haiku about AI"
5. **Execute!** 🎉

That's it! The model selector auto-fetches your models when you connect the nodes.

## Before You Begin

### Prerequisites

1. **Ollama Installed & Running**
   - Download from [ollama.com](https://ollama.com/)
   - Verify it's running: `curl http://localhost:11434/api/tags`
   - Pull at least one model: `ollama pull llama3.2`

2. **ComfyUI Installed**
   - Get it from [github.com/comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)

3. **Python Dependencies** (auto-installed)
   - httpx ≥0.28.1
   - loguru ≥0.7.3
   - rich ≥14.2.0

### Recommended Models for Testing

```bash
# Small & fast (1.3GB) - Great for testing
ollama pull llama3.2

# Multimodal vision (4.7GB) - For image workflows
ollama pull llava

# Coding assistant (3.8GB) - For code generation
ollama pull codellama

# Check what you have installed
ollama list
```

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

### Step 4: Generate Text with Chat

1. Add an **Ollama Chat Completion** node
2. Connect `client` from **Model Selector** (model auto-populates)
3. Enter your prompt in the `prompt` field
4. (Optional) Add a `system_prompt` to control behavior
5. Execute to generate a response!

**Example:**
- **prompt**: "Write a haiku about programming"
- **system_prompt**: "You are a helpful assistant"
- **response**: Returns the generated text
- **history**: Returns the conversation (for multi-turn chat)

### Step 5: Multi-Turn Conversations (Optional)

For conversations with memory:

1. Connect the `history` output from one **Chat Completion** node
2. To the `history` input of the next **Chat Completion** node
3. Each response remembers the previous messages

### Step 6: Unload When Done (Optional)

1. Add an **Ollama Unload Model** node
2. Connect it after your processing
3. This frees up memory

## Nodes Reference

### Core Nodes

| Node | Description |
|------|-------------|
| **Ollama Client** | Creates a reusable Ollama connection config |
| **Ollama Model Selector** | Select model with auto-fetch on connection |
| **Ollama Load Model** | Loads a model into Ollama's memory |
| **Ollama Chat Completion** | Generate text with conversation history |
| **Ollama Unload Model** | Unloads a model to free memory |

### Debug/Utility Nodes

| Node | Description |
|------|-------------|
| **Ollama Debug: History** | Formats conversation history as readable text for inspection |
| **Ollama Debug: History Length** | Returns the number of messages in conversation history |

### Option Nodes (Composable Parameters)

| Node | Parameter | Range/Type | Default | Description |
|------|-----------|------------|---------|-------------|
| **Temperature** | `temperature` | 0.0-2.0 | 0.8 | Controls randomness (0=deterministic, 2=very random) |
| **Seed** | `seed` | INT | 42 | Random seed for reproducible generation |
| **Max Tokens** | `max_tokens` | 1-4096 | 128 | Maximum tokens to generate |
| **Top P** | `top_p` | 0.0-1.0 | 0.9 | Nucleus sampling threshold |
| **Top K** | `top_k` | 1-100 | 40 | Top-k sampling (Ollama-specific) |
| **Repeat Penalty** | `repeat_penalty` | 0.0-2.0 | 1.1 | Penalty for repetition (Ollama-specific) |
| **Extra Body** | `extra_body` | JSON | {} | Advanced parameters (num_ctx, num_gpu, etc.) |

## Advanced Usage

The architecture provides a clean, composable workflow:

```text
[Ollama Client] → [Model Selector] → [Load Model] → [Chat Completion] → [Unload Model]
       ↓               ↓                   ↓                ↓
  (endpoint)     (pick model,        (load with)      (generate text,
                  auto-refresh)       keep_alive)      track history)
```

**Key Benefits:**

- **Reusable Client**: Create one client, connect to multiple nodes
- **Auto-refresh**: Model Selector can refresh the list automatically
- **Type Safety**: Client connection passed between nodes
- **Cleaner Workflows**: Less redundant endpoint configuration
- **Dynamic Dropdowns**: Model list automatically populates after refresh
- **Conversation Memory**: History passed between chat nodes for multi-turn conversations

**Example Workflow: Simple Chat**

```text
1. Ollama Client (endpoint: http://localhost:11434)
       ↓
2. Model Selector (model: "llama3.2", refresh: true)
       ↓
3. Load Model (keep_alive: "-1")
       ↓
4. Chat Completion (prompt: "Hello!")
       ↓
5. Unload Model
```

**Example Workflow: Multi-Turn Conversation**

```text
1. [Client] → [Selector] → [Load] → [Chat 1: "My name is Alice"]
                                          ↓ (history)
                                    [Chat 2: "What's my name?"]
                                          ↓ (history)
                                    [Chat 3: "Tell me a joke"]
       ↓
2. Unload Model
```

**Example Workflow: Chat with Options**

```text
[Client] → [Selector] → [Load Model]
                           ↓
       ┌───────────────────┴────────────────────┐
       ↓                   ↓                     ↓
[Temperature=0.7]    [Seed=42]          [MaxTokens=200]
       └───────────────────┬────────────────────┘
                           ↓ (merged options)
                   [Chat Completion]
                           ↓
                    "Deterministic response"
```

**Example Workflow: Advanced Parameters**

```text
[Temperature=0.8] → [TopK=50] → [RepeatPenalty=1.2] → [ExtraBody]
                                                           ↓
                                                    {"num_ctx": 4096}
                                                           ↓
                                                    [Chat Completion]
```

This pattern optimizes memory by unloading models when not needed, while maintaining full conversation context and precise control over generation parameters.

## 📚 Real-World Use Cases

### Use Case 1: Build a Simple Chatbot

**Goal**: Create a conversational AI that remembers context

**Workflow**:
```text
[Ollama Client] → [Model Selector: llama3.2]
                           ↓
                    [Chat Node 1]
                    prompt: "My name is Alice"
                    system: "You are a friendly assistant"
                           ↓ (pass history)
                    [Chat Node 2]
                    prompt: "What's my name?"
                           ↓
                    Response: "Your name is Alice!"
```

**Why it works**: The `history` output carries conversation context between nodes.

### Use Case 2: Extract Structured Data

**Goal**: Parse unstructured text into JSON for downstream processing

**Workflow**:
```text
[Ollama Client] → [Model Selector: llama3.2]
                           ↓
                    [Chat Completion]
                    format: "json"
                    prompt: "Extract data from: 'John is 35 and lives in NYC'"
                    system: "Return JSON with: name, age, city"
                           ↓
                    Output: {"name": "John", "age": 35, "city": "NYC"}
```

**When to use**: Data extraction, API integrations, workflow automation.

### Use Case 3: Vision + Text Workflows

**Goal**: Analyze images with AI and generate descriptions

**Workflow**:
```text
[Load Image] → [Ollama Client] → [Model Selector: llava]
                                          ↓
                                   [Chat Completion]
                                   image: (connected from Load Image)
                                   prompt: "Describe this image in detail"
                                          ↓
                                   Response: "A sunset over mountains..."
```

**Models with vision**: `llava`, `llava-llama3`, `bakllava`

### Use Case 4: Deterministic Code Generation

**Goal**: Generate the same code every time for testing/CI

**Workflow**:
```text
[Ollama Client] → [Model Selector: codellama]
                           ↓
              [Seed=42] → [Temperature=0.0] → [Chat Completion]
                                               prompt: "Write a Python function to sort a list"
                                                      ↓
                                               (Same code every run - cached!)
```

**Why it works**: Seed + low temperature = deterministic output + ComfyUI caching.

### Use Case 5: Memory-Efficient Batch Processing

**Goal**: Process multiple prompts without keeping all models loaded

**Workflow**:
```text
[Client] → [Selector: llama3.2] → [Load Model]
                                         ↓
                                  [Chat: Process Batch 1]
                                         ↓
                                  [Unload Model]
                                         ↓
           [Selector: codellama] → [Load Model]
                                         ↓
                                  [Chat: Process Batch 2]
                                         ↓
                                  [Unload Model]
```

**When to use**: Limited VRAM, multiple models, sequential processing.

### Use Case 6: AI-Assisted Image Prompts

**Goal**: Generate better Stable Diffusion prompts using AI

**Workflow**:
```text
[User Input: "cat"] → [Ollama Client] → [Model Selector: llama3.2]
                                                  ↓
                                          [Chat Completion]
                                          system: "Expand this into a detailed Stable Diffusion prompt"
                                          prompt: "cat"
                                                  ↓
                                          Response: "A fluffy orange tabby cat with green eyes..."
                                                  ↓
                                          [Stable Diffusion Node]
```

**Result**: Better image quality from AI-enhanced prompts!

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

### Chat Parameters

The **Ollama Chat Completion** node supports:

**Required:**
- `client` - Ollama client connection
- `model` - Model name (auto-populated from selector)
- `prompt` - User message/question

**Optional:**

- `system_prompt` - Instructions to guide model behavior
- `history` - Previous conversation (for multi-turn chat)
- `options` - Generation parameters (temperature, seed, etc.)
- `format` - Output format: "none" (default, text) or "json" (structured JSON)
- `image` - Image input for vision models

**Outputs:**

- `response` - Generated text
- `history` - Updated conversation (connect to next chat node)

**Caching & Performance:**

The chat node intelligently caches results to avoid unnecessary LLM calls:

- **With Seed**: When you provide a seed via the `OllamaOptionSeed` node, identical inputs will be cached (like standard ComfyUI nodes). This prevents wasteful re-execution when re-running the same workflow.
- **Without Seed**: When no seed is provided, the node will always re-execute to generate fresh, non-deterministic responses.

**Example: Deterministic workflow with caching**
```text
[Seed=42] → [Chat Completion] → Output
              ↓
        (Cached on re-run!)
```

This matches ComfyUI's standard behavior and significantly reduces API costs when iterating on workflows.

### JSON Mode (Phase 3)

The **format** parameter enables structured output for workflows that need parseable data:

**Example: Extract structured data**

```text
[Chat Completion]
├── format: "json"
├── prompt: "Extract person data: 'Alice is 30 years old'"
└── system_prompt: "Return JSON with keys: name, age"

Output: {"name": "Alice", "age": 30}
```

**When to use JSON mode:**
- Data extraction workflows
- Structured output for downstream processing
- API integrations requiring JSON
- ComfyUI workflows that parse the response

**Note:** Set `format` to "json" to enable. The model will ensure valid JSON output.

### Debug Utilities (Phase 3)

**Ollama Debug: History** - Inspect conversation memory

```text
[Chat History] → [Debug: History]
                      ↓
           Formatted Text Output:
           === Conversation History (3 messages) ===

           [1] SYSTEM:
               You are helpful

           [2] USER:
               Hello

           [3] ASSISTANT:
               Hi there!
```

**Ollama Debug: History Length** - Count messages

```text
[Chat History] → [History Length] → Output: 5 (messages)
```

**Use cases:**

- Debugging conversation flow
- Monitoring context length
- Workflow conditional logic based on message count
- Understanding what the model "remembers"

### Working with Images (Vision Models)

**Supported Models**: `llava`, `llava-llama3`, `bakllava`

**Basic Image Analysis**:

```text
[Load Image Node] → [Ollama Chat Completion]
                    ├── client: (from Model Selector: llava)
                    ├── image: (connected from Load Image)
                    └── prompt: "What do you see in this image?"
```

**Image + Conversation Context**:

```text
[Load Image] → [Chat 1: "Describe this image"]
                    ↓ (history + image)
               [Chat 2: "What colors are dominant?"]
                    ↓ (history)
               [Chat 3: "Suggest a caption"]
```

**Tips for Vision Workflows**:

- Use `llava` for general image understanding
- Vision models are larger (~4-7GB) - ensure adequate VRAM
- Image input is optional - node works with/without images
- Combine with text-only prompts for creative workflows

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

## 💡 Tips & Best Practices

### Performance Optimization

1. **Keep frequently-used models loaded**: Set `keep_alive: "-1"` to avoid reload delays
2. **Unload when switching models**: Free memory for the next model
3. **Use smaller models for testing**: `llama3.2:1b` is fast and uses less VRAM
4. **Enable caching**: Use `OllamaOptionSeed` for deterministic outputs that cache

### Workflow Design

1. **Reuse Client nodes**: Create one client, connect to multiple nodes
2. **Chain history properly**: Always connect `history` output → `history` input for conversations
3. **Use debug nodes during development**: Monitor conversation length and content
4. **Test with small models first**: Validate workflow logic before using large models

### Prompt Engineering

1. **Write clear system prompts**: Define the model's role and constraints
2. **Be specific in user prompts**: Vague prompts = vague responses
3. **Use JSON mode for structured data**: Set `format: "json"` and describe the schema
4. **Iterate on temperature**: Start at 0.7, adjust based on creativity needs

### Resource Management

1. **Monitor `ollama ps`**: See what's loaded and consuming memory
2. **Set appropriate keep_alive**: Balance convenience vs. memory usage
   - `-1`: Keep forever (for active work)
   - `5m`: Short tasks
   - `0`: Unload immediately (memory-constrained systems)
3. **Use quantized models**: `model:7b-q4` uses less memory than `model:7b`

### Error Handling

1. **Always check Ollama is running**: `curl http://localhost:11434/api/tags`
2. **Test endpoints separately**: Verify Ollama works before debugging ComfyUI
3. **Check logs first**: `logs/ollama_manager.json` has detailed error info
4. **Start simple**: Basic workflow first, add complexity incrementally

### Model Selection Guide

| Use Case | Recommended Model | Size | Notes |
|----------|------------------|------|-------|
| **Quick Testing** | `llama3.2:1b` | 1.3GB | Fast, low memory |
| **General Chat** | `llama3.2` | 2GB | Best balance |
| **Code Generation** | `codellama` | 3.8GB | Trained on code |
| **Image Analysis** | `llava` | 4.7GB | Vision + text |
| **Long Context** | `llama3.2:8b` | 4.7GB | Better reasoning |
| **Production** | `llama3.2:70b` | 40GB | Highest quality |

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
│       ├── nodes.py         # Model management nodes
│       ├── chat.py          # Chat completion node
│       ├── types.py         # Custom type definitions
│       ├── ollama_client.py # API client (fetch, load, unload, chat)
│       ├── api.py           # ComfyUI API routes
│       ├── state.py         # Model cache
│       ├── log_config.py    # Logging setup
│       └── async_utils.py   # Async utilities
├── tests/                   # Pytest test suite (52 tests)
└── web/
    └── ollama_widgets.js    # Auto-fetch UI logic
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

**Symptoms**: Can't find "Ollama" nodes in the Add Node menu

**Solutions**:

1. Check that dependencies are installed: `pip list | grep -E "httpx|loguru|rich"`
2. Restart ComfyUI completely (not just refresh browser)
3. Check ComfyUI console for error messages during startup
4. Verify the custom_nodes folder: `ls ComfyUI/custom_nodes/comfyui-ollama-model-manager`
5. Try reinstalling: `cd custom_nodes/comfyui-ollama-model-manager && python install.py`

### Model dropdown is empty

**Symptoms**: Model Selector dropdown shows no models

**Solutions**:

1. **Check Ollama is running**: `curl http://localhost:11434/api/tags`
   - If error: Start Ollama (`ollama serve` or launch the app)
2. **Check you have models**: `ollama list`
   - If empty: Pull a model (`ollama pull llama3.2`)
3. **Check endpoint URL**: Make sure the Ollama Client node has the correct endpoint
   - Default: `http://localhost:11434`
   - For remote: `http://your-server-ip:11434`
4. **Try manual refresh**: Set `refresh` to `true` in Model Selector and re-execute
5. **Check logs**: Look in `ComfyUI/custom_nodes/comfyui-ollama-model-manager/logs/`

### "Connection refused" or "Cannot connect" errors

**Symptoms**: Errors about connection failures

**Solutions**:

1. **Verify Ollama is accessible**:
   ```bash
   curl http://localhost:11434/api/tags
   ```
   Should return JSON with model list

2. **Check firewall** (if using remote Ollama):
   - Port 11434 must be open
   - Ollama must be bound to `0.0.0.0` not just `127.0.0.1`
   - Set environment variable: `OLLAMA_HOST=0.0.0.0:11434`

3. **Docker users**: Make sure port is exposed
   ```bash
   docker run -p 11434:11434 ollama/ollama
   ```

### Import errors

**Symptoms**: `ModuleNotFoundError: No module named 'httpx'`

**Solutions**:

```bash
# Standard installation
pip install httpx loguru rich

# With uv (faster)
uv pip install httpx loguru rich

# ComfyUI portable (Windows)
ComfyUI\python_embeded\python.exe -m pip install httpx loguru rich

# Virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install httpx loguru rich
```

### Models loading slowly

**Symptoms**: Long wait times when loading models

**Causes & Solutions**:

1. **Large models take time** - `llava:34b` will be slower than `llama3.2:1b`
2. **First load is always slower** - Model needs to be read from disk
3. **Check available RAM/VRAM** - Insufficient memory causes swapping
4. **Use keep_alive wisely** - Keep frequently-used models loaded with `keep_alive: "-1"`
5. **Consider smaller quantized models**: `llama3.2:1b` vs `llama3.2:8b`

### Permission errors (Windows)

**Symptoms**: "Access denied" when installing

**Solutions**:

1. Close ComfyUI completely
2. Run as administrator or use:
   ```bash
   ComfyUI\python_embeded\python.exe -m pip install --upgrade httpx loguru rich
   ```

### Chat responses are repetitive or low quality

**Symptoms**: Model repeats itself or gives poor answers

**Solutions**:

1. **Adjust temperature**: Higher = more creative (try 0.7-1.0)
2. **Increase repeat_penalty**: Use `OllamaOptionRepeatPenalty` node (try 1.1-1.3)
3. **Tune top_p/top_k**: Use `OllamaOptionTopP` and `OllamaOptionTopK`
4. **Better system prompt**: Guide the model's behavior more explicitly
5. **Try a different model**: Some models are better at certain tasks

### "Out of memory" errors

**Symptoms**: CUDA/memory allocation failures

**Solutions**:

1. **Unload unused models**: Use the "Ollama Unload Model" node
2. **Use smaller models**: `llama3.2:1b` instead of `llama3.2:70b`
3. **Reduce context length**: Use `OllamaOptionExtraBody` with `{"num_ctx": 2048}`
4. **Check what's loaded**: Run `ollama ps` to see active models
5. **Close other applications**: Free up VRAM/RAM

### Still having issues?

1. **Check logs**: `ComfyUI/custom_nodes/comfyui-ollama-model-manager/logs/ollama_manager.json`
2. **Enable debug logging**: Set log level in `log_config.py`
3. **Test Ollama directly**: `curl http://localhost:11434/api/generate -d '{"model":"llama3.2","prompt":"test"}'`
4. **Report bugs**: [Open an issue](https://github.com/darth-veitcher/comfyui-ollama-model-manager/issues) with logs

## FAQ

### Q: Do I need to run Ollama on the same machine as ComfyUI?

**A**: No! You can run Ollama on a different machine. Just set the endpoint in the **Ollama Client** node to your remote server's IP:

```text
http://192.168.1.100:11434
```

Make sure Ollama is configured to accept remote connections (`OLLAMA_HOST=0.0.0.0`).

### Q: Can I use this with OpenAI or other LLM APIs?

**A**: This extension is specifically for Ollama. However, Ollama is compatible with the OpenAI API format, so you can point OpenAI-compatible nodes at Ollama's endpoint.

### Q: Why do models load slowly the first time?

**A**: Ollama loads models from disk into RAM/VRAM. First load is always slower. Once loaded, subsequent generations are fast. Use `keep_alive: "-1"` to keep models resident.

### Q: How much memory do I need?

**A**: Depends on the model:

- `llama3.2:1b` → ~1.5GB RAM/VRAM
- `llama3.2:3b` → ~2.5GB RAM/VRAM
- `llama3.2:8b` → ~5GB RAM/VRAM
- `llama3.2:70b` → ~40GB RAM/VRAM

Ollama can use CPU RAM if VRAM is insufficient (but slower).

### Q: Can I run multiple models at once?

**A**: Yes! Load multiple models and switch between them using different Model Selector nodes. Each model consumes memory independently.

### Q: Does this work with LoRAs or fine-tuned models?

**A**: Yes! If you've created or imported models into Ollama, they'll appear in the model list. Use `ollama list` to see all available models.

### Q: How do I update models?

**A**: Use Ollama's CLI:

```bash
ollama pull llama3.2  # Updates to latest version
```

The model list in ComfyUI will update automatically.

### Q: Can I use this offline?

**A**: Yes! Once models are pulled with `ollama pull`, they're stored locally. No internet needed for inference.

### Q: What's the difference between this and other LLM nodes?

**A**: This extension is designed specifically for Ollama with features like:

- Auto-fetching model lists (no manual entry)
- Model loading/unloading for memory management
- Native Ollama parameter support (top_k, repeat_penalty, etc.)
- Built-in conversation history tracking
- No CORS issues (backend proxy)

## License

MIT License - See LICENSE file for details.

## Credits

- Built for [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- Uses [Ollama](https://ollama.com/) API
- Created by [darth-veitcher](https://github.com/darth-veitcher)

## Support

- 🐛 **Report bugs**: [GitHub Issues](https://github.com/darth-veitcher/comfyui-ollama-model-manager/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/darth-veitcher/comfyui-ollama-model-manager/discussions)
- ⭐ **Star the repo** if you find it useful!

---

**Made with ❤️ for the ComfyUI community**
