import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";
import { api } from "../../../scripts/api.js";

// Store for YAML/title data
const promptListStore = {
    yamlFiles: [],
    titlesByYaml: {},
};

// Helper to find widget by name
function findWidget(node, name) {
    return node.widgets?.find(w => w.name === name);
}

// Helper to refresh node display
function refreshNode(node) {
    if (!node) return;

    const previousSize = Array.isArray(node.size) ? [...node.size] : null;

    if (ComfyWidgets?.refreshNode) {
        ComfyWidgets.refreshNode(node);
    } else {
        const size = node.computeSize?.();
        if (Array.isArray(size)) {
            if (typeof node.setSize === "function") {
                node.setSize(size);
            } else {
                node.size = [...size];
            }
        }
        app.graph.setDirtyCanvas(true, true);
    }

    if (!previousSize) return;

    const targetSize = [previousSize[0], previousSize[1]];

    if (typeof node.setSize === "function") {
        node.setSize(targetSize);
    } else if (Array.isArray(node.size)) {
        node.size[0] = targetSize[0];
        node.size[1] = targetSize[1];
    } else {
        node.size = [...targetSize];
    }

    app.graph.setDirtyCanvas(true, true);
}

// Setup socket listeners
function setupSocketListeners() {
    // Listen for enum updates
    api.addEventListener("ns_promptlist_enum", (event) => {
        const data = event.detail;
        promptListStore.yamlFiles = data.yaml_files || [];
        promptListStore.titlesByYaml = data.titles_by_yaml || {};

        // Update all NS-PromptList nodes
        app.graph._nodes.forEach(node => {
            if (node.type === "NS-PromptList") {
                updateNodeEnums(node);
            }
        });
    });

    // Listen for widget updates
    api.addEventListener("ns_promptlist_set_widgets", (event) => {
        const data = event.detail;
        const targetNodeId = data.node_id;

        // Only update the specific node if node_id is provided
        if (targetNodeId) {
            const targetNode = app.graph._nodes.find(n => n.id === targetNodeId);
            if (targetNode && targetNode.type === "NS-PromptList") {
                const titleWidget = findWidget(targetNode, "title");
                const promptWidget = findWidget(targetNode, "prompt");

                if (titleWidget) titleWidget.value = data.title || "";
                if (promptWidget) promptWidget.value = data.prompt || "";

                refreshNode(targetNode);
            }
        } else {
            // Fallback: update active node only
            const activeNode = app.canvas.node_over || app.canvas.selected_nodes?.[0];

            if (activeNode && activeNode.type === "NS-PromptList") {
                const titleWidget = findWidget(activeNode, "title");
                const promptWidget = findWidget(activeNode, "prompt");

                if (titleWidget) titleWidget.value = data.title || "";
                if (promptWidget) promptWidget.value = data.prompt || "";

                refreshNode(activeNode);
            }
        }
    });
}

// Force reload YAML list
async function reloadYamlList() {
    try {
        // This will trigger the backend to refresh and broadcast new enum data
        await api.fetchApi("/ns_promptlist/reload_yamls", {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });
    } catch (error) {
        console.error("Error reloading YAML list:", error);
    }
}

// Update node combo box options
function updateNodeEnums(node) {
    const yamlWidget = findWidget(node, "select_yaml");
    const selectWidget = findWidget(node, "select");

    if (yamlWidget && promptListStore.yamlFiles.length > 0) {
        // Update YAML options
        const currentYaml = yamlWidget.value;
        yamlWidget.options.values = promptListStore.yamlFiles;

        // Keep current selection if it still exists
        if (promptListStore.yamlFiles.includes(currentYaml)) {
            yamlWidget.value = currentYaml;
        } else {
            yamlWidget.value = promptListStore.yamlFiles[0];
        }
    }

    if (selectWidget && yamlWidget) {
        // Update title options based on current YAML
        const currentTitle = selectWidget.value;
        const titles = promptListStore.titlesByYaml[yamlWidget.value] || [""];
        selectWidget.options.values = titles;

        // Keep current selection if it still exists
        if (titles.includes(currentTitle)) {
            selectWidget.value = currentTitle;
        } else if (titles[0] && titles[0] !== "") {
            selectWidget.value = titles[0];
            // Fetch prompt for the new selection
            requestPromptData(yamlWidget.value, titles[0], node.id);
        } else {
            selectWidget.value = "";
        }
    }

    refreshNode(node);
}

// Hook select widget change handler
function hookSelectChange(node) {
    if (node.type !== "NS-PromptList") return;

    const yamlWidget = findWidget(node, "select_yaml");
    const selectWidget = findWidget(node, "select");

    // Helper to get original callback
    function getOriginalCallback(widget) {
        if (!widget || !widget.callback) return null;
        // If it's our wrapper, return the original
        if (widget.callback._originalCallback) {
            return widget.callback._originalCallback;
        }
        return widget.callback;
    }

    // Store original callbacks (unwrapped)
    const originalYamlCallback = getOriginalCallback(yamlWidget);
    const originalSelectCallback = getOriginalCallback(selectWidget);

    // Hook YAML selection change
    if (yamlWidget) {
        const newCallback = function (value) {
            // Call original if exists
            if (originalYamlCallback) {
                originalYamlCallback.call(this, value);
            }

            // Update title options for this specific node
            const titles = promptListStore.titlesByYaml[value] || [""];
            if (selectWidget) {
                selectWidget.options.values = titles;
                // Auto-select first title if available
                selectWidget.value = titles[0] || "";

                // If we have a title, fetch its prompt
                if (titles[0]) {
                    requestPromptData(value, titles[0], node.id);
                }
            }

            refreshNode(node);
        };
        // Store original for future unwrapping
        newCallback._originalCallback = originalYamlCallback;
        yamlWidget.callback = newCallback;
    }

    // Hook title selection change
    if (selectWidget) {
        const newCallback = function (value) {
            // Call original if exists
            if (originalSelectCallback) {
                originalSelectCallback.call(this, value);
            }

            // Fetch prompt data for this specific node
            if (value) {
                requestPromptData(yamlWidget?.value || "", value, node.id);
            }
        };
        // Store original for future unwrapping
        newCallback._originalCallback = originalSelectCallback;
        selectWidget.callback = newCallback;
    }
}

// Request prompt data from backend
async function requestPromptData(yamlFile, title, nodeId = null) {
    if (!yamlFile || !title) return;

    try {
        await api.fetchApi("/ns_promptlist/get_prompt", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                yaml: yamlFile,
                title: title,
                node_id: nodeId
            })
        });
    } catch (error) {
        console.error("Error fetching prompt data:", error);
    }
}

// Extension registration
app.registerExtension({
    name: "NS.PromptList",

    async setup() {
        // Setup socket listeners
        setupSocketListeners();

        // Request initial YAML list on setup
        setTimeout(async () => {
            await reloadYamlList();
        }, 500);

        // Hook into node addition
        const origNodeAdded = app.graph.onNodeAdded;
        app.graph.onNodeAdded = function (node) {
            if (origNodeAdded) {
                origNodeAdded.call(this, node);
            }

            // Hook our node type
            if (node.type === "NS-PromptList") {
                setTimeout(() => {
                    hookSelectChange(node);
                    updateNodeEnums(node);
                    // Request fresh data when node is added
                    reloadYamlList();
                }, 0);
            }
        };
    },

    async nodeCreated(node) {
        if (node.type === "NS-PromptList") {
            // Set minimum size for the node
            node.size = [400, 300];
            node.computeSize = function () {
                const size = LGraphNode.prototype.computeSize.apply(this, arguments);
                // Ensure minimum width and height
                size[0] = Math.max(size[0], 400);
                size[1] = Math.max(size[1], 300);
                return size;
            };

            // Add delete button
            const deleteButton = node.addWidget("button", "delete_title", "", () => {
                const yamlWidget = findWidget(node, "select_yaml");
                const titleWidget = findWidget(node, "title");

                if (yamlWidget?.value && titleWidget?.value) {
                    if (confirm(`Delete title "${titleWidget.value}" from ${yamlWidget.value}?`)) {
                        // Call backend delete (would need to implement API endpoint)
                        console.log("Delete not implemented in this version");
                    }
                }
            });

            // Initialize with first title after a short delay
            setTimeout(() => {
                const yamlWidget = findWidget(node, "select_yaml");
                const selectWidget = findWidget(node, "select");

                if (yamlWidget && selectWidget) {
                    const currentYaml = yamlWidget.value;
                    const titles = promptListStore.titlesByYaml[currentYaml];

                    if (titles && titles.length > 0 && titles[0] !== "") {
                        selectWidget.value = titles[0];
                        requestPromptData(currentYaml, titles[0], node.id);
                    }
                }
            }, 100);
        }
    }
});