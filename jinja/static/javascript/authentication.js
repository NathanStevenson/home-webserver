import { makeRequest } from './index.js';

async function onAuthFormSubmit(event, endpoint) {
    // on form submission prevent normal form action; extract the form arguments as json
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const args = Object.fromEntries(formData.entries());
    // by default fetch follows redirect internally and will make the req but does not update address bar unless specify window.location.href
    const response = await makeRequest("POST", endpoint, args);
}

// when the DOM loads execute these JS functions
document.addEventListener("DOMContentLoaded", () => {
    // when login form is submitted
    if (document.getElementById("login-form")) { document.getElementById("login-form").addEventListener('submit', async(event) => { await onAuthFormSubmit(event, "/login"); }); }
    // when sign in form submitted
    if (document.getElementById("sign-in-form")) { document.getElementById("sign-in-form").addEventListener('submit', async(event) => { await onAuthFormSubmit(event, "/sign_up"); }); }
});