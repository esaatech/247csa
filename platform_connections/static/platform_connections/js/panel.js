function closePlatformPanel(event) {
    console.log("closePlatformPanel called");
    if (event) {
        event.preventDefault();
    }
    const panel = document.getElementById('platformPanelWrapper');
    if (panel) {
        panel.classList.remove('translate-x-0');
        panel.classList.add('translate-x-full');
    }
}

function togglePlatformPanel() {
    const panel = document.getElementById('platformPanelWrapper');
    if (panel) {
        if (panel.classList.contains('translate-x-0')) {
            // Panel is open — close it
            panel.classList.remove('translate-x-0');
            panel.classList.add('translate-x-full');
        } else {
            // Panel is closed — open it
            panel.classList.remove('translate-x-full');
            panel.classList.add('translate-x-0');
        }
    }
}

function updateConnectionMap(platform, connectionId) {
    const input = document.getElementById("connectionMap");
    let map = {};

    try {
        map = JSON.parse(input.value || '{}');
    } catch (e) {
        console.error("Invalid JSON in connectionMap");
    }

    map[platform] = connectionId;
    input.value = JSON.stringify(map);
}