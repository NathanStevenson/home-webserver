import { makeRequest } from './index.js';

// toggle between light and dark mode when clicked
function toggleDarkMode() {
    const body = document.getElementsByTagName('body')[0];
    if (body.className == "dark") { 
        body.className = "light";
        localStorage.setItem('theme', 'light');
    }
    else {
        body.className = "dark"; 
        localStorage.setItem('theme', 'dark');
    }
}

// converts a form to JSON and makes a POST request - return response if there is one
async function onFormSubmit(event, endpoint) {
    // on form submission prevent normal form action; extract the form arguments as json
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const args = Object.fromEntries(formData.entries());
    // by default fetch follows redirect internally and will make the req but does not update address bar unless specify window.location.href
    const response = await makeRequest("POST", endpoint, args);
    return response;
}

// submits the login form request
async function onApplyChangesForm(event, endpoint) {
    event.preventDefault();
    return await onFormSubmit(event, endpoint);
}

document.addEventListener("DOMContentLoaded", () => {
    // when the DOM loads - read the dark/light mode cookie to see how to display
    document.getElementById("darkToggle").addEventListener('click', toggleDarkMode);

    // submit changes to the backend
    if (document.getElementById("apply-changes-form")) { document.getElementById("apply-changes-form").addEventListener('submit', async(event) => { 
        const response = await onApplyChangesForm(event, "/apply_changes");
        if (response.error) {
            const error_text = document.getElementById('error-text');
            error_text.className = "show-error-matching";
            error_text.textContent = response.error;
        }
        }); 
    }
    // depending on light/dark mode have the toggle class correct
    const body = document.getElementsByTagName('body')[0];
    const darkModeToggle = document.getElementById('darkToggle');
    const theme = localStorage.getItem('theme');
    if (theme == "dark") { 
        darkModeToggle.checked = true;
    }
    else {
        darkModeToggle.checked = false;
    }
});