import { onFormSubmit } from './index.js';

// submits the Update Message form request
async function onUpdateMessage(event, endpoint) {
    event.preventDefault();
    return await onFormSubmit(event, endpoint);
}

// populate the device form based on the device selected
function populateDeviceForm() {
    const selectDevice = document.getElementById('pi_name');
    if (selectDevice) {
        for (const pi_info of all_pi_info) {
            if (selectDevice.value == pi_info.name) {
                const messageElem   = document.getElementById('message');
                const colorElem     = document.getElementById('color');
                const wrapText      = document.getElementById('wrap_text');
                messageElem.value   = pi_info.message;
                colorElem.value     = pi_info.color;
                if (pi_info.text_wrap == true) {
                    wrapText.checked = true;
                } else {
                    wrapText.checked = false;
                }
            }
        }
    }
}

// when the DOM loads execute these JS functions
document.addEventListener("DOMContentLoaded", () => {
    // on DOM load see which device is selected and load that device info
    populateDeviceForm();

    // when the value of the select box changes also populate the form
    if (document.getElementById('pi_name')) { document.getElementById('pi_name').addEventListener('change', () => populateDeviceForm()); }

    // when submitting update message form
    if (document.getElementById("update-led-message-form")) { document.getElementById("update-led-message-form").addEventListener('submit', async(event) => { await onUpdateMessage(event, "/led/update_message"); }); }
});