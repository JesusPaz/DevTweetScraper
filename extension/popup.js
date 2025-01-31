const switchElement = document.getElementById("auto-save-switch");
const statusElement = document.getElementById("status");

// Load switch state from storage
chrome.storage.sync.get("autoSaveEnabled", (data) => {
    switchElement.checked = data.autoSaveEnabled || false;
    statusElement.textContent = `Auto-Save is ${data.autoSaveEnabled ? "ON" : "OFF"}`;
});

// Listen for changes to the switch
switchElement.addEventListener("change", () => {
    const isEnabled = switchElement.checked;
    chrome.storage.sync.set({ autoSaveEnabled: isEnabled }, () => {
        statusElement.textContent = `Auto-Save is ${isEnabled ? "ON" : "OFF"}`;
        console.log(`Auto-Save ${isEnabled ? "enabled" : "disabled"}`);
    });

    // Notify content script of state change
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
            chrome.tabs.sendMessage(tabs[0].id, { action: "toggleAutoSave", enabled: isEnabled });
        }
    });
});
