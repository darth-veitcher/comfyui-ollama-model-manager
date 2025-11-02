# Changelog

All notable changes to this project will be documented in this file.

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
