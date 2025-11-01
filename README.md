# ComfyUI Ollama Model Manager

A basic set of nodes to allow the fine-grained control of models being served via Ollama. This is useful during workflows in constrained environments where you need to use a language or vision model but then need to immediately unload it afterwards to avoid memory issues.

## Nodes exposed

| Name | Description |
| - | - |
| OllamaRefreshModelList | Refresh Model List |
| OllamaSelectModel | Select Model |
| OllamaLoadSelectedModel | Load Selected Model |
| OllamaUnloadSelectedModel | Unload Selected Model |

## Example Usage

Refresh Model List --> Select Model --> Load Model --> Caption Image --> Unload Model --> Stable Diffusion
