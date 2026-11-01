const API_URL = "http://127.0.0.1:5000/process";

async function simplifyNotice() {
    const noticeInput = document.getElementById("notice");
    const button = document.getElementById("simplifyBtn");
    const status = document.getElementById("status");
    const results = document.getElementById("results");

    const notice = noticeInput.value.trim();

    if (!notice) {
        status.textContent = "Please paste a college notice first.";
        noticeInput.focus();
        return;
    }

    button.disabled = true;
    button.textContent = "Simplifying...";
    status.textContent = "Reading your notice. This may take a moment...";
    results.hidden = true;

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ notice })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Unable to process the notice.");
        }

        document.getElementById("summary").textContent =
            data.summary || "No summary generated.";

        displayList("eventDates", data.event_dates);
        displayList("deadlines", data.deadlines);
        displayList("amounts", data.amounts);
        displayList("eligibility", data.eligibility);
        displayList("actions", data.required_actions);
        displayList("consequences", data.consequences);

        results.hidden = false;
        status.textContent = "Your notice has been simplified.";

        results.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    } catch (error) {
        console.error("NotiEase error:", error);
        status.textContent =
            "Couldn't connect to NotiEase. Check that the Flask server is running and try again.";

    } finally {
        button.disabled = false;
        button.innerHTML = 'Simplify notice <span>→</span>';
    }
}


function displayList(elementId, items) {
    const list = document.getElementById(elementId);

    if (!list) {
        console.error(`Missing element with id="${elementId}" in index.html`);
        return;
    }

    list.replaceChildren();

    if (!Array.isArray(items) || items.length === 0) {
        const item = document.createElement("li");
        item.textContent = "No information detected.";
        item.className = "empty-result";
        list.appendChild(item);
        return;
    }

    items.forEach(text => {
        const item = document.createElement("li");
        item.textContent = text;
        list.appendChild(item);
    });
}