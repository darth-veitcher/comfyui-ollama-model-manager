/**
 * Custom widgets for Ollama Model Manager nodes in ComfyUI
 */

import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

// Add custom styling for the display widget
const style = document.createElement("style");
style.textContent = `
    .ollama-models-display {
        background-color: #1e1e1e;
        color: #d4d4d4;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 12px;
        padding: 10px;
        border-radius: 4px;
        border: 1px solid #3e3e3e;
        white-space: pre;
        overflow-x: auto;
        max-height: 300px;
        overflow-y: auto;
        margin: 5px 0;
    }

    .ollama-model-count {
        color: #4ec9b0;
        font-weight: bold;
    }
`;
document.head.appendChild(style);

// Helper function to convert models_json to dropdown options
function parseModelsJson(modelsJsonString) {
    try {
        const models = JSON.parse(modelsJsonString);
        if (Array.isArray(models) && models.length > 0) {
            return models;
        }
    } catch (e) {
        console.warn("[Ollama] Failed to parse models_json:", e);
    }
    return null;
}

// Helper function to update model dropdown widget
function updateModelDropdown(node, models) {
    const modelWidget = node.widgets?.find(w => w.name === "model");
    if (modelWidget && models && models.length > 0) {
        // Convert to combo widget
        modelWidget.type = "combo";
        modelWidget.options = { values: models };
        
        // Set default value if current value is empty or not in list
        if (!modelWidget.value || !models.includes(modelWidget.value)) {
            modelWidget.value = models[0];
        }
        
        console.log(`[Ollama] Updated dropdown with ${models.length} models`);
        return true;
    }
    return false;
}

// Register extension with ComfyUI
app.registerExtension({
    name: "OllamaModelManager.ModelsDisplay",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // Handle OllamaRefreshModelList node
        if (nodeData.name === "OllamaRefreshModelList") {

            // Store original onExecuted callback
            const onExecuted = nodeType.prototype.onExecuted;

            // Override onExecuted to handle our custom UI data
            nodeType.prototype.onExecuted = function(message) {
                // Call original onExecuted if it exists
                if (onExecuted) {
                    onExecuted.apply(this, arguments);
                }

                // Handle our custom models display
                if (message?.models_display) {
                    const displayText = message.models_display[0];
                    const modelCount = message.model_count?.[0] || 0;
                    const modelList = message.model_list?.[0] || [];

                    // Remove any existing display widget
                    const existingWidget = this.widgets?.find(w => w.name === "models_display_widget");
                    if (existingWidget) {
                        this.widgets = this.widgets.filter(w => w !== existingWidget);
                    }

                    // Create a custom display widget
                    const widget = ComfyWidgets["STRING"](this, "models_display_widget", ["STRING", {
                        multiline: true,
                        default: displayText
                    }], app).widget;

                    widget.inputEl.readOnly = true;
                    widget.inputEl.className = "ollama-models-display";
                    widget.value = displayText;

                    // Store metadata
                    widget.modelCount = modelCount;
                    widget.modelList = modelList;

                    // Adjust widget size
                    widget.computeSize = function(width) {
                        return [width, 150];
                    };

                    // Add the widget
                    if (!this.widgets) {
                        this.widgets = [];
                    }
                    this.widgets.push(widget);

                    // Update node size
                    this.setSize(this.computeSize());

                    console.log(`[Ollama] Displayed ${modelCount} models`);
                }
            };

            // Add a visual indicator when node is created
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                if (onNodeCreated) {
                    onNodeCreated.apply(this, arguments);
                }

                // Add a helpful text widget by default
                const infoWidget = this.addWidget("text", "ℹ️ info", "Execute to see models", () => {}, {
                    serialize: false
                });

                // Wait for widget to be fully initialized
                if (infoWidget && infoWidget.inputEl) {
                    infoWidget.inputEl.readOnly = true;
                    infoWidget.inputEl.style.opacity = "0.6";
                    infoWidget.inputEl.style.fontStyle = "italic";
                }
            };
        }

        // Handle OllamaLoadSelectedModel and OllamaUnloadSelectedModel nodes
        if (nodeData.name === "OllamaLoadSelectedModel" || nodeData.name === "OllamaUnloadSelectedModel") {
            
            // Store original onConnectionsChange callback
            const onConnectionsChange = nodeType.prototype.onConnectionsChange;
            
            // Override to detect when models_json is connected
            nodeType.prototype.onConnectionsChange = function(type, index, connected, link_info) {
                // Call original callback if it exists
                if (onConnectionsChange) {
                    onConnectionsChange.apply(this, arguments);
                }
                
                // Only process input connections
                if (type === 1 && connected) {  // type 1 = input
                    // Find the models_json input
                    const input = this.inputs?.find(i => i.name === "models_json");
                    if (input && input.link != null) {
                        // Get the connected node
                        const link = this.graph.links[input.link];
                        if (link) {
                            const sourceNode = this.graph.getNodeById(link.origin_id);
                            
                            // If connected to a Refresh node that has already executed
                            if (sourceNode && sourceNode.type === "OllamaRefreshModelList") {
                                // Check if the source node has outputs
                                const outputSlot = sourceNode.outputs?.[0];  // models_json is first output
                                if (outputSlot?.value) {
                                    const models = parseModelsJson(outputSlot.value);
                                    if (models) {
                                        updateModelDropdown(this, models);
                                    }
                                }
                            }
                        }
                    }
                }
                
                // If disconnected, revert to text input
                if (type === 1 && !connected) {
                    const input = this.inputs?.find((i, idx) => idx === index);
                    if (input?.name === "models_json") {
                        const modelWidget = this.widgets?.find(w => w.name === "model");
                        if (modelWidget && modelWidget.type === "combo") {
                            // Revert to text input
                            modelWidget.type = "text";
                            delete modelWidget.options;
                            console.log("[Ollama] Reverted to text input");
                        }
                    }
                }
            };
            
            // Override onExecuted to handle updates when connected node executes
            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function(message) {
                // Call original onExecuted if it exists
                if (onExecuted) {
                    onExecuted.apply(this, arguments);
                }
                
                // Check if models_json input is connected
                const input = this.inputs?.find(i => i.name === "models_json");
                if (input && input.link != null) {
                    const link = this.graph.links[input.link];
                    if (link) {
                        const sourceNode = this.graph.getNodeById(link.origin_id);
                        if (sourceNode && sourceNode.type === "OllamaRefreshModelList") {
                            const outputSlot = sourceNode.outputs?.[0];
                            if (outputSlot?.value) {
                                const models = parseModelsJson(outputSlot.value);
                                if (models) {
                                    updateModelDropdown(this, models);
                                }
                            }
                        }
                    }
                }
            };
            
            // Hook into onConfigure to restore dropdown state when loading workflow
            const onConfigure = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function(info) {
                if (onConfigure) {
                    onConfigure.apply(this, arguments);
                }
                
                // Defer the check to allow graph to be fully loaded
                setTimeout(() => {
                    const input = this.inputs?.find(i => i.name === "models_json");
                    if (input && input.link != null) {
                        const link = this.graph.links[input.link];
                        if (link) {
                            const sourceNode = this.graph.getNodeById(link.origin_id);
                            if (sourceNode && sourceNode.type === "OllamaRefreshModelList") {
                                const outputSlot = sourceNode.outputs?.[0];
                                if (outputSlot?.value) {
                                    const models = parseModelsJson(outputSlot.value);
                                    if (models) {
                                        updateModelDropdown(this, models);
                                    }
                                }
                            }
                        }
                    }
                }, 100);
            };
        }
    }
});

console.log("[Ollama Model Manager] Custom widgets loaded");
