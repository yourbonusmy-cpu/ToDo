const container = document.getElementById("stats-container");

const minCountInput = document.getElementById("min-count");
const excludeDailyInput = document.getElementById("exclude-daily");


/* --------------------------------------------------
LOAD DATA
-------------------------------------------------- */

async function loadStats() {

    const min = minCountInput.value || 3;
    const excludeDaily = excludeDailyInput.checked ? "1" : "0";

    const res = await fetch(
        `/api/statistics/?min=${min}&exclude_daily=${excludeDaily}`
    );

    const json = await res.json();

    renderStats(json.weekdays, json.data);
}


/* --------------------------------------------------
RENDER
-------------------------------------------------- */

function renderStats(weekdaysMap, data) {

    container.innerHTML = "";

    // порядок дней
    const order = [2, 3, 4, 5, 6, 7, 1];

    order.forEach(dayNum => {

        const label = weekdaysMap[dayNum];
        const tasks = data[dayNum] || [];

        const row = document.createElement("div");
        row.className = "card p-3";

        row.innerHTML = `
            <div class="d-flex align-items-start">

                <!-- DAY -->
                <div class="fw-bold me-3" style="width: 40px;">
                    ${label}.
                </div>

                <!-- TASKS -->
                <div class="d-flex flex-wrap gap-3 flex-grow-1">
                    ${
                        tasks.length
                        ? tasks.map(renderTask).join("")
                        : `<span class="text-muted small">нет данных</span>`
                    }
                </div>

            </div>
        `;

        container.appendChild(row);

    });

}


/* --------------------------------------------------
TASK UI
-------------------------------------------------- */

function renderTask(task) {

    const icon = task.icon
        ? `<img src="${MEDIA_URL + task.icon}" width="40" height="40">`
        : `<div style="width:40px;height:40px;"></div>`;

    return `
        <div class="position-relative text-center" style="width:70px">

            <!-- COUNT -->
            <span class="badge bg-primary position-absolute top-0 end-0">
                ${task.count}
            </span>

            <!-- ICON -->
            <div class="border rounded p-2 bg-light">
                ${icon}
            </div>

            <!-- TITLE -->
            <div class="small mt-1 text-truncate" title="${task.title}">
                ${task.title}
            </div>

        </div>
    `;
}


/* --------------------------------------------------
AUTO FILTER
-------------------------------------------------- */

let timer = null;

function triggerReload() {

    clearTimeout(timer);

    timer = setTimeout(() => {
        loadStats();
    }, 300);

}

minCountInput.addEventListener("input", triggerReload);
excludeDailyInput.addEventListener("change", triggerReload);


/* --------------------------------------------------
INIT
-------------------------------------------------- */

loadStats();