import { onFormSubmit } from './index.js';

// submits the login form request
async function onLoginForm(event, endpoint) {
    event.preventDefault();
    return await onFormSubmit(event, endpoint);
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
    if (document.getElementById("login-form")) { document.getElementById("login-form").addEventListener('submit', async(event) => { 
        const response = await onLoginForm(event, "/login"); 
        if (response.error) {
            const error_text = document.getElementById('error-text');
            error_text.textContent = response.error;
            error_text.className = "show-error-matching";
        }
        });
    }
    // when sign in form submitted
    if (document.getElementById("reset-password")) { document.getElementById("reset-password").addEventListener('submit', async(event) => { await onResetPassword(event, "/reset_password"); }); }
});