
const imgEl = document.getElementById('video');
const ws = new WebSocket(`/ws/view/1`); // can dynamically switch this id to see other cameras
ws.binaryType = "arraybuffer";

ws.onopen = () => { statusEl.textContent = "connected"; };
ws.onclose = () => { statusEl.textContent = "disconnected"; };

ws.onmessage = (evt) => {
    // Try parse JSON (errors/info), else assume JPEG
    if (typeof evt.data === "string") {
        try {
        const msg = JSON.parse(evt.data);
        if (msg.type === "error") {
            statusEl.textContent = `error: ${msg.reason}`;
        }
        } catch {}
        return;
    }
    const blob = new Blob([evt.data], { type: "image/jpeg" });
    const url = URL.createObjectURL(blob);
    imgEl.src = url;
    // Clean up the previous blob URL on next frame
    imgEl.onload = () => URL.revokeObjectURL(url);
};