import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "ComfyUI.SimpleChat.Config.V3", // Use a new name to avoid browser caching issues
    async nodeCreated(node, app) {
        if (node.comfyClass === "SimpleChatConfig") {
            // --- WIDGET REPLACEMENT AND REORDERING ---

            // Find the original string widget for 'model'
            const modelWidgetIndex = node.widgets.findIndex((w) => w.name === "model");
            if (modelWidgetIndex === -1) return;
            const originalModelWidget = node.widgets[modelWidgetIndex];
            const originalModelValue = originalModelWidget.value;

            // Step 1: Create new widgets using the addWidget API. This appends them temporarily.
            const newModelCombo = node.addWidget("combo", "model", originalModelValue, () => {}, {
                values: [originalModelValue || ""]
            });
            const refreshButton = node.addWidget("button", "Refresh Models", "refresh", () => {});

            // Step 2: Remove the newly created widgets from the end of the array.
            // We now have fully constructed widget objects, detached from the node's widget list.
            node.widgets.pop(); // removes refreshButton
            node.widgets.pop(); // removes newModelCombo

            // Step 3: Remove the original string widget from its position.
            node.widgets.splice(modelWidgetIndex, 1);

            // Step 4: Insert the new, constructed widgets back into the array at the correct positions.
            node.widgets.splice(modelWidgetIndex, 0, newModelCombo);     // Insert combo where the old one was.
            node.widgets.splice(modelWidgetIndex + 1, 0, refreshButton); // Insert button right after it.

            // --- END WIDGET MANIPULATION ---

            // Now, find all widgets again to be safe and attach logic
            const providerWidget = node.widgets.find((w) => w.name === "provider");
            const apiKeyWidget = node.widgets.find((w) => w.name === "api_key");
            const baseUrlWidget = node.widgets.find((w) => w.name === "base_url");

            // Attach the callback logic to the refresh button
            refreshButton.callback = () => {
                const provider = providerWidget.value;
                const apiKey = apiKeyWidget.value;
                const baseUrl = baseUrlWidget ? baseUrlWidget.value : "";

                if (!apiKey) {
                    alert("Please enter an API Key first.");
                    return;
                }

                refreshButton.label = "Loading...";
                refreshButton.disabled = true;
                node.setDirtyCanvas(true, true);

                const url = `/simplechat/models/${provider}?api_key=${encodeURIComponent(apiKey)}&base_url=${encodeURIComponent(baseUrl)}`;

                api.fetchApi(url)
                    .then(response => response.json())
                    .then(models => {
                        if (Array.isArray(models) && models.length > 0) {
                            newModelCombo.options.values = models;
                            if (!newModelCombo.value || !models.includes(newModelCombo.value)) {
                                newModelCombo.value = models[0];
                            }
                        } else {
                            newModelCombo.options.values = [];
                            newModelCombo.value = "";
                            alert("No models found.");
                        }
                    })
                    .catch(err => {
                        console.error("Error fetching models:", err);
                        alert("Error fetching models: " + err.message);
                    })
                    .finally(() => {
                        refreshButton.label = "Refresh Models";
                        refreshButton.disabled = false;
                        node.setDirtyCanvas(true, true);
                    });
            };

            // Trigger a redraw to ensure the node resizes correctly after manipulation
            node.computeSize();
            node.setDirtyCanvas(true, true);
        }
    }
});
