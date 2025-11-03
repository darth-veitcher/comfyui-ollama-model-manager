# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - feature/phase-3-advanced branch

### Added - Phase 3: Advanced Features (JSON Mode & Debug Utilities) 🚧

- 🔧 **JSON Mode** - Structured output for parseable data
  - Added `format` parameter to `chat_completion()` API
  - Added format dropdown to OllamaChatCompletion node ("none" or "json")
  - Enables data extraction workflows and API integrations
- 🐛 **Debug Utility Nodes** - Inspect conversation state
  - **OllamaDebugHistory** - Format conversation history as readable text
  - **OllamaHistoryLength** - Count messages in conversation
- 📝 Comprehensive test coverage (11 new tests, 107 total)
- 📚 Updated documentation with JSON mode examples and debug utilities

### Technical Changes

**Phase 3:**
- Extended `ollama_client.py` with `format` parameter in `chat_completion()`
- Updated `chat.py` to add format dropdown to OllamaChatCompletion
- Added 2 debug nodes: `OllamaDebugHistory` and `OllamaHistoryLength`
- Updated `__init__.py` to register debug nodes
- Added `tests/test_chat.py::TestPhase3Features` - 11 tests
- Updated README.md with JSON mode section and debug utilities

### Test Results

- **107 tests passing** (31 base + 32 chat + 44 options)
- 100% coverage for Phase 3 features

## [Released] - main branch

### Added - Phase 1: Chat Completion ✅

- ✨ **OllamaChatCompletion node** - Full text generation with conversation history
- 💬 Chat completion via Ollama's `/api/chat` endpoint
- 🔄 Multi-turn conversation support with history management
- 🎯 System prompts for behavior control
- 🖼️ Vision support (image inputs for multimodal models)
- 📝 Comprehensive test coverage (21 new tests, 52 total)
- 🔒 Type-safe connections with custom `OLLAMA_HISTORY` and `OLLAMA_OPTIONS` types
- 📚 Updated documentation with chat examples and multi-turn workflows

### Added - Phase 2: Option Nodes ✅

- 🎛️ **7 Composable Option Nodes** - Chain parameters together
  - **OllamaOptionTemperature** - Control randomness (0.0-2.0)
  - **OllamaOptionSeed** - Reproducible generation with seed
  - **OllamaOptionMaxTokens** - Limit response length (maps to num_predict)
  - **OllamaOptionTopP** - Nucleus sampling (0.0-1.0)
  - **OllamaOptionTopK** - Top-k sampling (Ollama-specific)
  - **OllamaOptionRepeatPenalty** - Control repetition (Ollama-specific)
  - **OllamaOptionExtraBody** - Advanced parameters via JSON
- 🔗 Merge pattern from comfyui-openai-api for clean option chaining
- ✅ JSON validation for ExtraBody node
- 📝 44 comprehensive tests for all option nodes (96 total)
- 📚 Documentation with option chaining examples

### Technical Changes

**Phase 1:**
- Added `src/comfyui_ollama_model_manager/chat.py` - Chat completion node
- Added `src/comfyui_ollama_model_manager/types.py` - Custom types
- Extended `ollama_client.py` with `chat_completion()` function
- Added `tests/test_chat.py` - 21 tests

**Phase 2:**
- Added `src/comfyui_ollama_model_manager/options.py` - 7 option nodes
- Updated `__init__.py` to register all option nodes
- Added `tests/test_options.py` - 44 tests
- Updated README.md with option tables and examples

### Test Results

- **96 tests passing** (31 base + 21 chat + 44 options)
- 100% coverage for chat and option functionality
- All nodes tested for merge pattern, chaining, and validation

### Coming Next

- Phase 3: Advanced features (streaming, JSON mode, function calling)
- Integration testing with real Ollama instance
- Example workflows and tutorials

## [1.0.0] - 2025-11-02

### Architecture

- Refactored to clean 4-node architecture:
  - `OllamaClient` - Reusable connection configuration
  - `OllamaModelSelector` - Model selection with optional auto-refresh
  - `OllamaLoadModel` - Load models into memory
  - `OllamaUnloadModel` - Unload models to free memory

### Features

- COMBO dropdown for model selection with cached models
- Per-endpoint model caching for better performance
- Dynamic dropdown updates after workflow execution
- Python backend handles all Ollama API calls (no CORS issues)
- Type-safe `OLLAMA_CLIENT` connection passing between nodes
- Beautiful logging with loguru (console + JSON file output)

### Changed

- Model input changed from STRING to COMBO for better UX
- Removed all JavaScript fetch calls to avoid CORS restrictions
- Models fetched only via Python backend during workflow execution
- Simplified JavaScript to only update dropdowns from execution results
- Added models_json output to OllamaModelSelector for downstream node population

### Added

- ARCHITECTURE.md - Complete system design documentation
- TESTING.md - Comprehensive testing guide
- Per-endpoint model caching in state.py
