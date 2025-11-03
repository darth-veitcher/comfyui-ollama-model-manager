# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - develop branch

### Added - Phase 1: Chat Completion

- ✨ **OllamaChatCompletion node** - Full text generation with conversation history
- 💬 Chat completion via Ollama's `/api/chat` endpoint
- 🔄 Multi-turn conversation support with history management
- 🎯 System prompts for behavior control
- 🖼️ Vision support (image inputs for multimodal models)
- 📝 Comprehensive test coverage (21 new tests, 52 total)
- 🔒 Type-safe connections with custom `OLLAMA_HISTORY` and `OLLAMA_OPTIONS` types
- 📚 Updated documentation with chat examples and multi-turn workflows

### Technical Changes

- Added `src/comfyui_ollama_model_manager/chat.py` - Chat completion node implementation
- Added `src/comfyui_ollama_model_manager/types.py` - Custom type definitions
- Extended `ollama_client.py` with `chat_completion()` async function
- Updated `__init__.py` to register OllamaChatCompletion node
- Added `tests/test_chat.py` - 21 comprehensive tests
- Updated README.md with chat documentation and workflow examples
- Updated INTEGRATION_PROPOSAL.md with Phase 1-3 roadmap

### Coming Next

- Phase 2: Option nodes (Temperature, Seed, MaxTokens, TopP, TopK, RepeatPenalty)
- Phase 3: Advanced features (streaming, JSON mode, function calling)

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
