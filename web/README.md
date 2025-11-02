# Custom Web Extensions for Ollama Model Manager

This directory contains JavaScript extensions that add custom UI widgets to the ComfyUI nodes.

## Files

### `ollama_widgets.js`
Custom widget implementation for displaying model lists directly on the `OllamaRefreshModelList` node.

## How It Works

When the `OllamaRefreshModelList` node executes:

1. **Python Side**: The node returns UI data in the format:
   ```python
   {
       "ui": {
           "models_display": ["formatted text"],
           "model_count": [count],
           "model_list": [list]
       },
       "result": (models_json, dependencies)
   }
   ```

2. **JavaScript Side**: The extension intercepts the `onExecuted` callback and:
   - Creates a custom multiline text widget
   - Styles it with a dark theme and monospace font
   - Displays the formatted model list directly on the node
   - Auto-sizes the widget for optimal display

## Features

- ✅ **No extra nodes needed** - Models display directly on the refresh node
- ✅ **Custom styling** - Dark theme with syntax highlighting
- ✅ **Read-only display** - Prevents accidental edits
- ✅ **Auto-sizing** - Widget adjusts to content
- ✅ **Persistent** - Display remains after workflow reload

## Styling

The widget uses custom CSS with:
- Dark background (#1e1e1e)
- Monospace font (Consolas, Monaco, Courier New)
- Scrollable overflow for long lists
- Model count highlighted in teal

## ComfyUI Integration

ComfyUI automatically loads JavaScript files from the `web` directory of custom nodes when the `WEB_DIRECTORY` variable is set in `__init__.py`.
