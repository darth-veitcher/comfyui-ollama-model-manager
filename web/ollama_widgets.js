/**
 * Custom widgets for Ollama Model Manager nodes in ComfyUI
 *
 * Supports both new and legacy node architectures:
 * - New: OllamaClient → OllamaModelSelector → Load/Unload
 * - Legacy: OllamaRefreshModelList → OllamaSelectModel → Load/Unload
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
    if (!modelWidget) {
        console.warn("[Ollama] No model widget found on node:", node.type);
        return false;
    }

    if (!models || models.length === 0) {
        console.warn("[Ollama] No models to update");
        return false;
    }

    console.log(`[Ollama] Updating model widget on ${node.type}:`, {
        currentValue: modelWidget.value,
        currentType: modelWidget.type,
        hasOptions: !!modelWidget.options,
        modelsCount: models.length,
        models: models
    });

    // Ensure widget is a combo type
    modelWidget.type = "combo";

    // Update combo widget values
    if (!modelWidget.options) {
        modelWidget.options = {};
    }
    modelWidget.options.values = models;

    // Set default value if current value is empty or not in list
    if (!modelWidget.value || !models.includes(modelWidget.value)) {
        modelWidget.value = models[0];
        console.log(`[Ollama] Set default model to: ${models[0]}`);
    }

    // Force widget to recompute size
    if (modelWidget.computeSize) {
        modelWidget.computeSize();
    }

    // Trigger multiple UI updates to ensure visibility
    if (node.setDirtyCanvas) {
        node.setDirtyCanvas(true, true);
    }

    if (node.graph) {
        if (node.graph.change) {
            node.graph.change();
        }
        if (node.graph.setDirtyCanvas) {
            node.graph.setDirtyCanvas(true, true);
        }
    }

    // Force a node size recalculation
    if (node.onResize) {
        node.onResize();
    }

    console.log(`[Ollama] ✓ Updated dropdown with ${models.length} models`);
    return true;
}

// Helper to get models from connected source node
function getModelsFromConnectedNode(node) {
    // Check for client input from OllamaModelSelector
    const clientInput = node.inputs?.find(i => i.name === "client");
    if (clientInput && clientInput.link != null) {
        const link = node.graph.links[clientInput.link];
        if (link) {
            const sourceNode = node.graph.getNodeById(link.origin_id);

            // Check if source is OllamaModelSelector
            if (sourceNode && sourceNode.type === "OllamaModelSelector") {
                // models_json is the 3rd output (index 2)
                const modelsJsonOutput = sourceNode.outputs?.[2];
                if (modelsJsonOutput?.value) {
                    console.log("[Ollama] Found models from OllamaModelSelector:", modelsJsonOutput.value);
                    return parseModelsJson(modelsJsonOutput.value);
                }
                console.log("[Ollama] No models_json value in OllamaModelSelector output");
            }
        }
    }

    return null;
}

// Register extension with ComfyUI
app.registerExtension({
    name: "OllamaModelManager.ModelsDisplay",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // Handle OllamaModelSelector (new architecture)
        if (nodeData.name === "OllamaModelSelector") {
            const onExecuted = nodeType.prototype.onExecuted;

            nodeType.prototype.onExecuted = function(message) {
                if (onExecuted) {
                    onExecuted.apply(this, arguments);
                }

                // Update model dropdown when executed
                if (message?.models_json) {
                    const modelsJson = message.models_json[0];
                    const models = parseModelsJson(modelsJson);
                    if (models) {
                        console.log("[Ollama] OllamaModelSelector executed with", models.length, "models");
                        updateModelDropdown(this, models);

                        // Notify downstream nodes connected to client output (index 0)
                        const clientOutput = this.outputs?.[0];
                        if (clientOutput?.links && clientOutput.links.length > 0) {
                            for (const linkId of clientOutput.links) {
                                const link = this.graph.links[linkId];
                                if (link) {
                                    const targetNode = this.graph.getNodeById(link.target_id);
                                    if (targetNode) {
                                        console.log("[Ollama] Updating dropdown on downstream node:", targetNode.type);
                                        updateModelDropdown(targetNode, models);
                                    }
                                }
                            }
                        }
                    }
                }
            };

            // Auto-refresh when client is connected
            const onConnectionsChange = nodeType.prototype.onConnectionsChange;
            nodeType.prototype.onConnectionsChange = async function(type, index, connected, link_info) {
                console.log("[Ollama] onConnectionsChange fired:", {type, index, connected, link_info});
                
                if (onConnectionsChange) {
                    onConnectionsChange.apply(this, arguments);
                }

                if (type === 1 && connected) {  // Input connected
                    console.log("[Ollama] Input connection detected, checking if it's client...");
                    const input = this.inputs?.find((i, idx) => idx === index);
                    console.log("[Ollama] Input:", input);
                    
                    if (input?.name === "client") {
                        console.log("[Ollama] ✓ Client connected to Model Selector - fetching models");

                        // Get the client endpoint from the connected node
                        const link = this.graph.links[this.inputs[0].link];
                        console.log("[Ollama] Link:", link);
                        
                        if (link) {
                            const clientNode = this.graph.getNodeById(link.origin_id);
                            console.log("[Ollama] Client node:", clientNode);
                            
                            if (clientNode && clientNode.type === "OllamaClient") {
                                const endpointWidget = clientNode.widgets?.find(w => w.name === "endpoint");
                                const endpoint = endpointWidget?.value || "http://localhost:11434";

                                console.log("[Ollama] ✓ Fetching models from:", endpoint);

                                try {
                                    // Make direct API call to Ollama
                                    const response = await fetch(`${endpoint}/api/tags`);
                                    console.log("[Ollama] Fetch response:", response);
                                    
                                    if (response.ok) {
                                        const data = await response.json();
                                        console.log("[Ollama] API response data:", data);
                                        const models = data.models?.map(m => m.name) || [];

                                        console.log("[Ollama] ✓ Fetched", models.length, "models:", models);

                                        if (models.length > 0) {
                                            updateModelDropdown(this, models);

                                            // Also update downstream Load/Unload nodes
                                            const clientOutput = this.outputs?.[0];
                                            if (clientOutput?.links && clientOutput.links.length > 0) {
                                                for (const linkId of clientOutput.links) {
                                                    const link = this.graph.links[linkId];
                                                    if (link) {
                                                        const targetNode = this.graph.getNodeById(link.target_id);
                                                        if (targetNode) {
                                                            console.log("[Ollama] Auto-updating downstream node:", targetNode.type);
                                                            updateModelDropdown(targetNode, models);
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    } else {
                                        console.warn("[Ollama] Failed to fetch models:", response.status, response.statusText);
                                    }
                                } catch (error) {
                                    console.error("[Ollama] Error fetching models:", error);
                                }
                            }
                        }
                    }
                }
            };

            // Also hook into onConnectInput as a backup
            const onConnectInput = nodeType.prototype.onConnectInput;
            nodeType.prototype.onConnectInput = function(inputIndex, outputType, outputSlot, outputNode, outputIndex) {
                console.log("[Ollama] onConnectInput called:", {inputIndex, outputType, outputNode: outputNode?.type});
                
                const result = onConnectInput ? onConnectInput.apply(this, arguments) : true;
                
                // If client input is connected, trigger fetch
                if (inputIndex === 0 && outputNode?.type === "OllamaClient") {
                    console.log("[Ollama] Client input connected via onConnectInput - triggering fetch");
                    
                    // Small delay to ensure connection is fully established
                    setTimeout(async () => {
                        const endpointWidget = outputNode.widgets?.find(w => w.name === "endpoint");
                        const endpoint = endpointWidget?.value || "http://localhost:11434";
                        
                        console.log("[Ollama] Fetching models from:", endpoint);
                        
                        try {
                            const response = await fetch(`${endpoint}/api/tags`);
                            if (response.ok) {
                                const data = await response.json();
                                const models = data.models?.map(m => m.name) || [];
                                
                                console.log("[Ollama] ✓ Fetched", models.length, "models");
                                
                                if (models.length > 0) {
                                    updateModelDropdown(this, models);
                                }
                            }
                        } catch (error) {
                            console.error("[Ollama] Error:", error);
                        }
                    }.bind(this), 100);
                }
                
                return result;
            };

            // Add a hint when node is created
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                if (onNodeCreated) {
                    onNodeCreated.apply(this, arguments);
                }

                console.log("[Ollama] OllamaModelSelector created - connect a client to auto-fetch models");
            };
        }

        // Handle OllamaLoadModel and OllamaUnloadModel
        if (nodeData.name === "OllamaLoadModel" || nodeData.name === "OllamaUnloadModel") {

            // Store original onConnectionsChange callback
            const onConnectionsChange = nodeType.prototype.onConnectionsChange;

            // Override to detect when models source is connected
            nodeType.prototype.onConnectionsChange = function(type, index, connected, link_info) {
                // Call original callback if it exists
                if (onConnectionsChange) {
                    onConnectionsChange.apply(this, arguments);
                }

                // Only process input connections
                if (type === 1 && connected) {  // type 1 = input
                    const models = getModelsFromConnectedNode(this);
                    if (models) {
                        updateModelDropdown(this, models);
                    }
                }

                // If disconnected, revert to text input
                if (type === 1 && !connected) {
                    const input = this.inputs?.find((i, idx) => idx === index);
                    if (input?.name === "models_json" || input?.name === "client") {
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

                const models = getModelsFromConnectedNode(this);
                if (models) {
                    updateModelDropdown(this, models);
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
                    const models = getModelsFromConnectedNode(this);
                    if (models) {
                        updateModelDropdown(this, models);
                    }
                }, 100);
            };
        }
    }
});

console.log("[Ollama Model Manager] Custom widgets loaded");
