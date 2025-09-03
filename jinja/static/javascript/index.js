
// perform the network request and return whatever JSON the server returns
export async function makeRequest(method = 'GET', endpoint, body=null) {
    // set the options; if not GET then set content to be JSON and have the args be passed along
    const options = { method: method.toUpperCase() };
    if (body && method.toUpperCase() !== 'GET') {
        options.body = JSON.stringify(body);
        options.headers = {'Content-Type': 'application/json'}; 
    }
    // make the request; if redirected jump to page; if ok return JSON; if not ok console error; if exception console err
    try {
        const response = await fetch(endpoint, options);
        if (response.redirected) {
            window.location.href = response.url;
            return;
        }
        if (response.ok) {
            return await response.json();
        } else {
            console.error(`Request to ${endpoint} failed ${response.status}: ${response.statusText}`);
        }
    } catch (err) {
        console.error(`Exception on server:`, err);
    }
}

function toggleDarkMode() {
    const body = document.getElementsByTagName('body')[0];
    const dark_mode_btn = document.getElementById('dark-mode-button');
    if (body.className == "dark") { body.className = "light"; dark_mode_btn.innerHTML = '&#127774;' }
    else { body.className = "dark"; dark_mode_btn.innerHTML = '&#127769;' }
}

// when the DOM loads execute these JS functions
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("dark-mode-button").addEventListener('click', toggleDarkMode);
});