# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

- **Auto-fetch models on connection**: OllamaModelSelector now automatically fetches models when a client is connected
- Direct Ollama API calls from JavaScript for instant model list updates without needing to execute the workflow

### Fixed

- OllamaModelSelector now displays as a dropdown from the start (changed from STRING to COMBO input)
- Model dropdown properly refreshes when the node is executed
- Added UI change trigger to ensure dropdown updates are visible immediately
- Improved console logging for debugging dropdown updates

### Modified

- OllamaModelSelector's `model` input now uses cached models for initial dropdown population
- JavaScript widget handlers updated to work with native COMBO widgets instead of converting from STRING
- Added graph change trigger to force UI updates when dropdown values change
- `onConnectionsChange` now makes direct API call to `{endpoint}/api/tags` to fetch models instantly
- Downstream Load/Unload nodes are automatically updated when models are fetched

### Technical Details

The key change is in `nodes.py` - `OllamaModelSelector.INPUT_TYPES()`:

- **Before**: `"model": ("STRING", {"default": "", "multiline": False})`
- **After**: `"model": (model_list,)` where `model_list` is cached models or `[""]`

This means the model selector now:

1. Shows as a dropdown immediately (no need to execute first)
2. Populates with cached models if available
3. Updates when executed with `refresh=true`
4. Propagates model list to downstream Load/Unload nodes

## [Previous] - 2024-12-XX

### Changed

- Refactored to 4-node architecture: OllamaClient, OllamaModelSelector, OllamaLoadModel, OllamaUnloadModel
- Removed legacy nodes (OllamaRefreshModelList, OllamaSelectModel)
- Implemented per-endpoint model caching
- Added models_json output to OllamaModelSelector for downstream node population

### Added

- ARCHITECTURE.md - Complete system design documentation
- TESTING.md - Comprehensive testing guide
- Per-endpoint model caching in state.py
