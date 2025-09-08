import { makeRequest } from './index.js';

// converts a form to JSON and makes a POST request
async function onFormSubmit(event, endpoint) {
    // on form submission prevent normal form action; extract the form arguments as json
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const args = Object.fromEntries(formData.entries());
    // by default fetch follows redirect internally and will make the req but does not update address bar unless specify window.location.href
    const response = await makeRequest("POST", endpoint, args);
}

// submits the login form request
async function onLoginForm(event, endpoint) {
    event.preventDefault();
    onFormSubmit(event, endpoint);
}

// submits the reset-password form request
async function onResetPassword(event, endpoint) {
    // before submitting network request make sure they match if not spit back error and do not request
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const args = Object.fromEntries(formData.entries());
    if (args.password !== args.password_verify) {
        document.getElementById("error-text").className = "show-error-matching";
        return
    }
    onFormSubmit(event, endpoint);
}

// when the DOM loads execute these JS functions
document.addEventListener("DOMContentLoaded", () => {
    // when login form is submitted
    if (document.getElementById("login-form")) { document.getElementById("login-form").addEventListener('submit', async(event) => { await onLoginForm(event, "/login"); }); }
    // when sign in form submitted
    if (document.getElementById("reset-password")) { document.getElementById("reset-password").addEventListener('submit', async(event) => { await onResetPassword(event, "/reset_password"); }); }
});