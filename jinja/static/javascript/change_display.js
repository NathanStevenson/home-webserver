import { onFormSubmit } from './index.js';

async function onChangeLEDDisplay(event, endpoint) {
    event.preventDefault();
    return await onFormSubmit(event, endpoint);
}

// when the DOM loads execute these JS functions
document.addEventListener("DOMContentLoaded", () => {
    // when submitting change display form
    if (document.getElementById("change-led-display-form")) { document.getElementById("change-led-display-form").addEventListener('submit', async(event) => { await onChangeLEDDisplay(event, "/led/change_display"); }); }
});