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

// Register extension with ComfyUI
app.registerExtension({
    name: "OllamaModelManager.ModelsDisplay",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // Only apply to OllamaRefreshModelList node
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
                infoWidget.inputEl.readOnly = true;
                infoWidget.inputEl.style.opacity = "0.6";
                infoWidget.inputEl.style.fontStyle = "italic";
            };
        }
    }
});

console.log("[Ollama Model Manager] Custom widgets loaded");
