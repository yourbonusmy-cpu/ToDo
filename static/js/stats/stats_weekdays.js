const container = document.getElementById("stats-container");

const minCountInput = document.getElementById("min-count");

const taskCheckboxes = document.querySelectorAll(".task-toggle");
const resetTasksBtn = document.getElementById("reset-tasks-filter");
const tasksLabel = document.getElementById("tasks-dropdown-label");

const searchInput = document.getElementById("tasks-search-input");
const taskItems = document.querySelectorAll(".task-item");

/* --------------------------------------------------
GET EXCLUDED TASKS
-------------------------------------------------- */

function getExcludedTasks() {
  return Array.from(taskCheckboxes)
    .filter((cb) => cb.checked)
    .map((cb) => cb.value);
}

/* --------------------------------------------------
LOAD DATA
-------------------------------------------------- */

async function loadStats() {
  const min = minCountInput.value || 3;
  const excluded = getExcludedTasks();

  const params = new URLSearchParams({
    min: min,
  });

  excluded.forEach((id) => params.append("exclude_tasks", id));

  const res = await fetch(`/api/statistics/?${params.toString()}`);
  const json = await res.json();

  renderStats(json.weekdays, json.data);
}

/* --------------------------------------------------
RENDER
-------------------------------------------------- */

function renderStats(weekdaysMap, data) {
  container.innerHTML = "";

  const order = [2, 3, 4, 5, 6, 7, 1];

  order.forEach((dayNum) => {
    const label = weekdaysMap[dayNum];
    const tasks = data[dayNum] || [];

    const row = document.createElement("div");
    row.className = "card p-3";

    row.innerHTML = `
      <div class="d-flex align-items-start">

        <div class="fw-bold me-3" style="width: 40px;">
          ${label}.
        </div>

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

      <span class="badge bg-primary position-absolute top-0 end-0">
        ${task.count}
      </span>

      <div class="border rounded p-2 bg-light">
        ${icon}
      </div>

      <div class="small mt-1 text-truncate" title="${task.title}">
        ${task.title}
      </div>

    </div>
  `;
}

/* --------------------------------------------------
LABEL UPDATE
-------------------------------------------------- */

function updateTasksLabel() {
  const selected = getExcludedTasks().length;

  if (selected === 0) {
    tasksLabel.textContent = "Исключить задачи";
  } else {
    tasksLabel.textContent = `Исключено: ${selected}`;
  }
}

/* --------------------------------------------------
AUTO FILTER
-------------------------------------------------- */

function filterTasksList() {
  const query = searchInput.value.toLowerCase().trim();

  taskItems.forEach((item) => {
    const text = item.innerText.toLowerCase();

    if (text.includes(query)) {
      item.style.display = "";
    } else {
      item.style.display = "none";
    }
  });
}

let searchTimer = null;

searchInput.addEventListener("input", () => {
  clearTimeout(searchTimer);

  searchTimer = setTimeout(() => {
    filterTasksList();
  }, 300);
});

let timer = null;

function triggerReload() {
  clearTimeout(timer);

  timer = setTimeout(() => {
    loadStats();
  }, 300);
}

minCountInput.addEventListener("input", triggerReload);

taskCheckboxes.forEach((cb) => {
  cb.addEventListener("change", () => {
    updateTasksLabel();
    triggerReload();
  });
});

resetTasksBtn.addEventListener("click", () => {
  taskCheckboxes.forEach((cb) => (cb.checked = false));

  searchInput.value = "";
  filterTasksList();

  updateTasksLabel();
  triggerReload();
});

/* --------------------------------------------------
INIT
-------------------------------------------------- */

updateTasksLabel();
loadStats();