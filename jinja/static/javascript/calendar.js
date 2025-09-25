import { makeRequest } from './index.js';

const calendarGrid          = document.getElementById("calendarGrid");
const monthYear             = document.getElementById("monthYear");
const modal                 = document.getElementById("eventModal");
const eventDateInput        = document.getElementById("eventDate");
const eventTitleInput       = document.getElementById("eventTitle");
const eventTimeInput        = document.getElementById("eventTime");
const eventDescInput        = document.getElementById("eventDesc");
const eventIdInput          = document.getElementById("eventId");
const modalTitle            = document.getElementById("modalTitle");

const inputTitle = document.getElementById('eventTitle');
const charCountSpan = document.getElementById('charCount');
const maxLength = inputTitle.getAttribute('maxlength');

inputTitle.addEventListener('input', () => {
    const currentLength = inputTitle.value.length;
    charCountSpan.textContent = `${currentLength}/${maxLength}`;
});

let events = {}; // store events as { "YYYY-M-D": [{id, title, description, color}] }
let selectedDate = "";

// Track displayed month/year
let currentYear = new Date().getFullYear();
let currentMonth = new Date().getMonth();

// Generate the calendar for that month/year
function generateCalendar(year, month) {
    monthYear.textContent = new Date(year, month).toLocaleString("default", { month: "long", year: "numeric" });

    // Generate all the days by getting first day of this month and day before first day of next month
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month+1, 0).getDate();

    calendarGrid.innerHTML = "";

    // populate the weekdays in the 7 wide grid
    const dayNames = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
    dayNames.forEach(d => {
        const div = document.createElement("div");
        div.textContent = d;
        div.className = "day-name";
        calendarGrid.appendChild(div);
    });

    // day blank slots before first day of month
    for (let i=0; i<firstDay; i++) {
        const div = document.createElement("div");
        calendarGrid.appendChild(div);
    }

    // create the divs in the calendar;
    for (let d=1; d<=daysInMonth; d++) {
        const dateKey = `${year}-${month+1}-${d}`;
        const div = document.createElement("div");
        div.className = "day";
        div.innerHTML = `<div class="date">${d}</div>`;

        // if there is an event on that date then display it and add a click event
        if (events[dateKey]) {
            events[dateKey].forEach((ev) => {
                const evDiv = document.createElement("div");
                evDiv.className = "event";
                evDiv.textContent = ev.title;
                evDiv.style.backgroundColor = ev.color;
                evDiv.onclick = (e) => {
                    e.stopPropagation();
                    openModal(dateKey, ev);
                };
                div.appendChild(evDiv);
            });
        }

        div.onclick = () => openModal(dateKey);
        calendarGrid.appendChild(div);
    }
}

// Open the modal either with a view feature or 
function openModal(dateKey, event=null) {
    selectedDate = dateKey;
    modal.style.display = "flex";
    eventDateInput.value = dateKey;

    // if event already exists have the update event modal shown + correct callback attached
    if (event) {
        // update model
        modalTitle.textContent = "Update Event";
        eventTimeInput.value = event.hour + ":" + event.minute;
        eventTitleInput.value = event.title;
        eventDescInput.value = event.description;
        eventIdInput.value = event.id;
        // update the text count correctly
        const length = inputTitle.value.length;
        charCountSpan.textContent = `${length}/${maxLength}`;
        // style buttons accordingly
        document.getElementById("add-item-btn").style.display       = "none";
        document.getElementById("delete-item-btn").style.display    = "inline-block";
        document.getElementById("update-item-btn").style.display    = "inline-block";
        // hook up buttons to proper callbacks
        document.getElementById("update-item-btn").addEventListener("click", () => addOrUpdateCalendarEvent("PATCH"));
        document.getElementById("cancel-item-btn").addEventListener("click", () => closeModal());
        document.getElementById("delete-item-btn").addEventListener("click", () => deleteCalendarEvent());

    // if event does not already exist then add it 
    } else {
        modalTitle.textContent = "Add Event";
        eventTimeInput.value = "";
        eventTitleInput.value = "";
        eventDescInput.value = "";
        eventIdInput.value = "";
        // style buttons accordingly
        document.getElementById("add-item-btn").style.display       = "inline-block";
        document.getElementById("delete-item-btn").style.display    = "none";
        document.getElementById("update-item-btn").style.display    = "none";
        // hook up buttons to proper callbacks
        document.getElementById("add-item-btn").addEventListener("click", () => addOrUpdateCalendarEvent("POST"));
        document.getElementById("cancel-item-btn").addEventListener("click", () => closeModal());
    }
}

// close modal
function closeModal() {
    modal.style.display = "none";
}

// callback to add or update the given event in the DB
async function addOrUpdateCalendarEvent(request_method) {
    // update the backend + store results in db; auto reload page to show the new event
    const args = {};
    // "YYYY-M-D"
    const splitDate = selectedDate.split("-", 3);
    const splitTime = eventTimeInput.value.trim().split(":");
    args.year           = splitDate[0];
    args.month          = splitDate[1];
    args.day            = splitDate[2];
    args.hour           = splitTime[0];
    args.minute         = splitTime[1];
    args.title          = eventTitleInput.value.trim();
    args.description    = eventDescInput.value.trim();
    args.id             = parseInt(eventIdInput.value.trim()); 

    // make request to the backend with the updated 
    await makeRequest(request_method, "/calendar/event", args);
}

// callback to delete the given event in the DB
async function deleteCalendarEvent() {
    const event_id = eventIdInput.value.trim();
    await makeRequest("DELETE", `/calendar/event/${event_id}`, null); 
}

// close modal when clicking outside modal
window.onclick = (e) => {
    if (e.target === modal) closeModal();
};

// Navigation between calendar components
document.getElementById("prevMonth").onclick = () => {
    currentMonth--;
    if (currentMonth < 0) {
        currentMonth = 11;
        currentYear--;
    }
    generateCalendar(currentYear, currentMonth);
    };

    document.getElementById("nextMonth").onclick = () => {
    currentMonth++;
    if (currentMonth > 11) {
        currentMonth = 0;
        currentYear++;
    }
    generateCalendar(currentYear, currentMonth);
};

// when the DOM loads execute these JS functions
document.addEventListener("DOMContentLoaded", () => {
    // Populate the events based on the current ones stored in the DB
    for (const event of all_calendar_events) {
        // store events as { "YYYY-M-D": [{id, title, description}] }
        const event_key = event.year + "-" + event.month + "-" + event.day;
        // if events[key] is not initialized then need to set it to an empty array
        if (!events[event_key]) { events[event_key] = []; }
        // color is dynamic users can change their color for the event and it will be reflected across all calendars 
        events[event_key].push({"id": event.id, "title": event.title, "description": event.description, "color": event.user.cal_event_color, "hour": event.hour, "minute": event.minute});
    }

    // Initial render based on the current year and month
    generateCalendar(currentYear, currentMonth);
});