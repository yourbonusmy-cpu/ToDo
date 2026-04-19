/* --------------------------------------------------
STATE
-------------------------------------------------- */

const visibilityEye = document.getElementById("visibility-eye");
const eyeLabel = document.getElementById("visibility-label");
const selectedContainer = document.getElementById("selected-tasks");
const taskDetailCard = document.getElementById("task-detail-card");

const detailIcon = document.getElementById("task-detail-icon");
const detailTitle = document.getElementById("task-detail-title");

const detailAmount = document.getElementById("task-detail-amount");
const detailTime = document.getElementById("task-detail-time");
const detailDescription = document.getElementById("task-detail-description");

const blockTitleInput = document.getElementById("block-title");
const blockDateInput = document.getElementById("block-date");

const passwordToggle = document.getElementById("task-password-toggle");
const passwordContainer = document.getElementById("task-password-container");
const passwordInput = document.getElementById("task-password");
const passwordEye = document.getElementById("password-eye");
const decryptBtn = document.getElementById("decrypt-btn");
const encryptedLabel = document.getElementById("encrypted-label");

const weatherSwitch = document.getElementById("weather-switch");
const weatherContainer = document.getElementById("weather-container");

const selected = [];
const taskState = {};

weatherSwitch.addEventListener("change", () => {
  if (weatherSwitch.checked) {
    weatherContainer.style.display = "flex";
    loadWeather();
  } else {
    weatherContainer.style.display = "none";
    currentWeatherData = null;
  }
});

async function loadWeather() {
  const res = await fetch("/api/weather/?city=Москва");
  if (!res.ok) return;

  const data = await res.json();

  currentWeatherData = data.weather;

  renderWeatherCompact(currentWeatherData);
}

//function renderWeatherCompact(weather) {
//    const row = document.getElementById("weather-row");
//    row.innerHTML = "";
//
//    const order = ["Утро", "День", "Вечер", "Ночь"];
//
//    order.forEach(label => {
//        const w = weather.find(x => x.label === label);
//        if (!w) return;
//
//        const el = document.createElement("div");
//        el.className = `weather-mini ${w.main?.toLowerCase() || ""}`;
//
//        el.title = w.description || w.main || "";
//
//        el.innerHTML = `
//            <div class="top d-flex align-items-center justify-content-between">
//
//                <span>${w.label}</span>
//
//                <div class="d-flex align-items-center gap-1">
//                    ${
//                        w.icon_url
//                            ? `<img src="${w.icon_url}" width="18">`
//                            : `<span>${w.icon || ""}</span>`
//                    }
//                    <span>${w.temp}°</span>
//                </div>
//
//            </div>
//
//            <div class="bottom">
//                ${w.description} •
//                ${w.humidity}% •
//                ${w.wind_speed} м/с (${w.wind_dir}) •
//                ${w.pressure}
//            </div>
//        `;
//
//        row.appendChild(el);
//    });
//}

function renderWeatherCompact(weather) {
  const row = document.getElementById("weather-row");
  row.innerHTML = "";

  const order = ["Утро", "День", "Вечер", "Ночь"];

  order.forEach((label) => {
    const w = weather.find((x) => x.label === label);
    if (!w) return;

    const el = document.createElement("div");
    el.className = `weather-mini ${w.main?.toLowerCase() || ""}`;

    el.title = w.description || w.main || "";

    el.innerHTML = `
            <div class="weather-head">

                <div class="left">
                    <div class="period">${w.label}</div>
                    <div class="desc">${w.description || ""}</div>
                </div>

                <div class="right">
                    <div class="clouds">
                        ${w.humidity ?? 0}%
                    </div>
                </div>

            </div>

            <div class="weather-meta">

                <div class="meta-item">
                    🌡 ${w.temp}°
                </div>

                <div class="meta-item">
                    💨 ${w.wind_speed} ${w.wind_dir}
                </div>

                <div class="meta-item">
                    ⏲ ${w.pressure}
                </div>

            </div>
        `;

    row.appendChild(el);
  });
}
/* --------------------------------------------------
BLOCK ID
-------------------------------------------------- */

const blockIdInput = document.getElementById("block-id");
const blockId = blockIdInput ? blockIdInput.value : null;

function formatDate(date) {
  const day = String(date.getDate()).padStart(2, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const year = String(date.getFullYear()).slice(-2); // последние 2 цифры

  return `${day}.${month}.${year}`;
}

// если поле пустое — подставляем дату
if (blockTitleInput && !blockTitleInput.value.trim()) {
  //    const today = formatDate(new Date());
  //    blockTitleInput.value = `${today}`;
  blockTitleInput.value = formatDate(new Date());
}
if (blockDateInput && !blockDateInput.value) {
  const today = new Date().toISOString().split("T")[0];
  blockDateInput.value = today;
}

/* --------------------------------------------------
CSRF
-------------------------------------------------- */

function getCookie(name) {
  let cookieValue = null;

  if (document.cookie) {
    const cookies = document.cookie.split(";");

    for (let cookie of cookies) {
      cookie = cookie.trim();

      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }

  return cookieValue;
}

const csrftoken = getCookie("csrftoken");

/* --------------------------------------------------
DESCRIPTION UI STATE
-------------------------------------------------- */
function renderDescriptionState(state) {
  /* -------------------------
    NOT ENCRYPTED
    ------------------------- */
  if (!state.is_encrypted) {
    encryptedLabel.style.display = "none";
    passwordContainer.style.display = "none";
    decryptBtn.style.display = "none";

    detailDescription.style.display = "block";
    detailDescription.disabled = false;

    passwordToggle.disabled = false;

    return;
  }

  /* -------------------------
    ENCRYPTED
    ------------------------- */

  encryptedLabel.style.display = "inline-flex";

  // 🔥 ВАЖНО: пароль показываем ТОЛЬКО если toggle включен
  if (passwordToggle.checked) {
    passwordContainer.style.display = "block";
  } else {
    passwordContainer.style.display = "none";
  }

  decryptBtn.style.display = "inline-flex";

  if (state.decrypted) {
    detailDescription.style.display = "block";
    detailDescription.disabled = false;

    decryptBtn.style.display = "none";
    encryptedLabel.textContent = "Расшифровано";

    passwordToggle.disabled = false;
  } else {
    detailDescription.style.display = "none";
    detailDescription.disabled = true;

    encryptedLabel.textContent = "Зашифровано";

    passwordToggle.disabled = true;

    // 🔥 при НЕ расшифрованном — пароль ОБЯЗАТЕЛЬНО показываем
    passwordContainer.style.display = "block";
  }
}

/* --------------------------------------------------
VISIBILITY EYE
-------------------------------------------------- */

visibilityEye.addEventListener("click", () => {
  const id = taskDetailCard.dataset.currentTaskId;

  if (!id) return;

  const state = taskState[id];

  state.is_hidden = !state.is_hidden;

  updateDetailEyeIcon(state.is_hidden);
  updateTaskVisibility(id);
});

function updateDetailEyeIcon(isHidden) {
  const icon = visibilityEye.querySelector("i");

  if (isHidden) {
    icon.classList.remove("bi-eye");
    icon.classList.add("bi-eye-slash");

    eyeLabel.textContent = "Показать";
  } else {
    icon.classList.remove("bi-eye-slash");
    icon.classList.add("bi-eye");

    eyeLabel.textContent = "Скрыть";
  }
}

function updateTaskVisibility(id) {
  const el = selectedContainer.querySelector(`[data-id="${id}"]`);

  if (!el) return;

  if (taskState[id].is_hidden) {
    el.classList.add("task-hidden");
  } else {
    el.classList.remove("task-hidden");
  }
}

/* --------------------------------------------------
ADD TASK
-------------------------------------------------- */

function addTask(taskData) {
  const id = taskData.id?.toString() || `new-${Math.random()}`;

  if (!selected.includes(id)) {
    selected.push(id);

    const el = document.createElement("div");

    el.className = "selected-task position-relative";
    el.dataset.id = id;

    el.innerHTML = `
            <div class="border rounded bg-light d-flex align-items-center justify-content-center w-100 h-100">
                ${taskData.icon ? `<img src="${MEDIA_URL + taskData.icon}" width="48" height="48">` : ""}
            </div>

            <button class="btn btn-danger btn-sm position-absolute top-0 start-100 translate-middle rounded-circle remove-task">
                ×
            </button>
        `;

    el.addEventListener("click", () => showTaskDetail(id));

    el.querySelector(".remove-task").addEventListener("click", (e) => {
      e.stopPropagation();
      removeTask(id);
    });

    selectedContainer.appendChild(el);

    taskState[id] = {
      id: id,
      template_id: taskData.template_id || taskData.id,
      title: taskData.title,
      description: taskData.description || "",

      amount: parseInt(taskData.amount) || 1,
      time: parseFloat(taskData.time) || 1,

      iconSrc: taskData.icon || "",

      is_encrypted: taskData.is_encrypted || false,
      password: "",
      is_hidden: taskData.is_hidden || false,

      decrypted: true,
      description_changed: true,
    };
  }

  showTaskDetail(id);
  toggleEmptyState();
}

/* --------------------------------------------------
REMOVE TASK
-------------------------------------------------- */

function removeTask(id) {
  delete taskState[id];

  const index = selected.indexOf(id);

  if (index > -1) selected.splice(index, 1);

  const el = selectedContainer.querySelector(`[data-id="${id}"]`);

  if (el) el.remove();

  taskDetailCard.style.display = "none";
  toggleEmptyState();
}

/* --------------------------------------------------
SHOW DETAIL
-------------------------------------------------- */

function showTaskDetail(id) {
  const state = taskState[id];

  if (!state) return;

  taskDetailCard.style.display = "block";

  detailIcon.src = state.iconSrc ? MEDIA_URL + state.iconSrc : "";
  detailTitle.textContent = state.title;

  detailAmount.value = state.amount;
  detailTime.value = state.time;

  if (state.is_encrypted) {
    detailDescription.value = state.decrypted ? state.description : "";
  } else {
    detailDescription.value = state.description;
  }

  passwordToggle.checked = state.is_encrypted;
  passwordInput.value = state.password;

  taskDetailCard.dataset.currentTaskId = id;

  updateTaskVisibility(id);
  updateDetailEyeIcon(state.is_hidden);

  renderDescriptionState(state);
}

/* --------------------------------------------------
INPUT HANDLERS
-------------------------------------------------- */

detailAmount.addEventListener("input", () => {
  const id = taskDetailCard.dataset.currentTaskId;

  if (id) taskState[id].amount = parseInt(detailAmount.value);
});

detailTime.addEventListener("input", () => {
  const id = taskDetailCard.dataset.currentTaskId;

  if (id) taskState[id].time = parseFloat(detailTime.value);
});

detailDescription.addEventListener("input", () => {
  const id = taskDetailCard.dataset.currentTaskId;

  const state = taskState[id];

  state.description = detailDescription.value;
  state.description_changed = true;
});

/* --------------------------------------------------
PASSWORD TOGGLE
-------------------------------------------------- */
passwordToggle.addEventListener("change", () => {
  const id = taskDetailCard.dataset.currentTaskId;
  if (!id) return;

  const state = taskState[id];

  state.is_encrypted = passwordToggle.checked;

  if (!state.is_encrypted) {
    state.password = "";
    state.decrypted = true;

    // 🔥 сразу скрываем пароль
    passwordContainer.style.display = "none";
  } else {
    if (state.description) {
      state.decrypted = true;
    }
  }

  renderDescriptionState(state);
});

/* --------------------------------------------------
PASSWORD INPUT
-------------------------------------------------- */

passwordInput.addEventListener("input", () => {
  const id = taskDetailCard.dataset.currentTaskId;

  if (!id) return;

  taskState[id].password = passwordInput.value;
});

/* --------------------------------------------------
SHOW / HIDE PASSWORD
-------------------------------------------------- */

passwordEye.addEventListener("click", () => {
  const icon = passwordEye.querySelector("i");

  if (passwordInput.type === "password") {
    passwordInput.type = "text";

    icon.classList.remove("bi-eye");
    icon.classList.add("bi-eye-slash");
  } else {
    passwordInput.type = "password";

    icon.classList.remove("bi-eye-slash");
    icon.classList.add("bi-eye");
  }
});

/* --------------------------------------------------
DECRYPT
-------------------------------------------------- */

decryptBtn.addEventListener("click", async () => {
  const id = taskDetailCard.dataset.currentTaskId;

  const state = taskState[id];

  const password = passwordInput.value;

  const res = await fetch(`/decrypt-task/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },

    body: JSON.stringify({
      task_id: id,
      password: password,
    }),
  });

  const data = await res.json();

  if (data.status !== "ok") {
    alert("Неверный пароль");
    return;
  }

  state.description = data.description;
  state.password = password;
  state.decrypted = true;

  detailDescription.value = data.description;

  renderDescriptionState(state);
});

/* --------------------------------------------------
TASK PICKER
-------------------------------------------------- */

document.querySelectorAll(".task-picker .task-icon").forEach((icon) => {
  icon.addEventListener("click", () => {
    const templateId = icon.dataset.id;

    const taskData = {
      id: templateId,
      template_id: templateId,
      title: icon.dataset.title,
      description: icon.dataset.description,
      amount: icon.dataset.amount,
      time: icon.dataset.time,

      icon: icon.querySelector("img")
        ? icon.querySelector("img").dataset.icon
        : "",
    };

    fetch(`/api/templates/${templateId}/select/`, {
      method: "POST",
      headers: { "X-CSRFToken": csrftoken },
    });

    addTask(taskData);
  });
});

/* --------------------------------------------------
SORTABLE
-------------------------------------------------- */

new Sortable(selectedContainer, {
  animation: 150,
  onEnd() {
    const ids = Array.from(selectedContainer.children)
      .map((el) => el.dataset.id)
      .filter((id) => taskState[id]); // <-- фильтруем лишние
    selected.length = 0;
    ids.forEach((id) => selected.push(id));
  },
});

/* --------------------------------------------------
CLEAR BLOCK
-------------------------------------------------- */

document.getElementById("clear-block-btn").onclick = () => {
  selected.length = 0;

  selectedContainer.innerHTML = "";

  for (let key in taskState) delete taskState[key];

  taskDetailCard.style.display = "none";
  toggleEmptyState();
};

/* --------------------------------------------------
SAVE BLOCK
-------------------------------------------------- */

document.getElementById("save-block-btn").onclick = async () => {
  if (!blockTitleInput.value.trim()) {
    alert("Введите название блока");
    return;
  }

  const tasksData = selected
    .map((id) => taskState[id])
    .filter(Boolean) // убираем undefined
    .map((state) => ({
      id: state.id?.toString().startsWith("new-") ? null : parseInt(state.id),
      template_id: state.template_id,
      title: state.title,
      description: state.description,
      decrypted: state.decrypted,
      is_encrypted: state.is_encrypted,
      is_hidden: state.is_hidden,
      password: state.password || "",
      amount: state.amount,
      time: state.time,
      icon: state.iconSrc,
    }));

  const url = window.location.href;

  const formData = new FormData();

  formData.append("title", blockTitleInput.value);
  formData.append("target_date", blockDateInput.value);
  formData.append("with_weather", weatherSwitch.checked);
  formData.append("weather_city", "Москва"); // или select
  formData.append("tasks", JSON.stringify(tasksData));
  if (weatherSwitch.checked && currentWeatherData) {
    formData.append("weather_data", JSON.stringify(currentWeatherData));
  }
  formData.append("csrfmiddlewaretoken", csrftoken);

  const response = await fetch(url, {
    method: "POST",
    body: formData,
  });

  if (response.redirected) {
    window.location.href = response.url;
  } else {
    alert("Ошибка при сохранении блока");
  }
};

/* --------------------------------------------------
LOAD BLOCK (EDIT)
-------------------------------------------------- */

function loadBlock() {
  if (!block_json) return;

  blockTitleInput.value = block_json.title;

  block_json.tasks.forEach((task) => {
    addTask(task);

    const id = task.id.toString();
    taskState[id].amount = task.amount;
    taskState[id].time = task.time;

    taskState[id].is_encrypted = task.is_encrypted;
    taskState[id].is_hidden = task.is_hidden;
    taskState[id].template_id = task.template_id;

    if (task.is_encrypted) {
      taskState[id].description = task.description || "";
      taskState[id].decrypted = false;
    } else {
      taskState[id].description = task.description || "";
      taskState[id].decrypted = true;
    }
    if (block_json.target_date && blockDateInput) {
      blockDateInput.value = block_json.target_date;
    }

    updateTaskVisibility(id);
    toggleEmptyState();
  });
  if (block_json?.weather) {
    weatherSwitch.checked = true;
    weatherContainer.style.display = "block";
    currentWeatherData = block_json.weather;

    renderWeatherCompact(block_json.weather);
  }
}

loadBlock();

/* --------------------------------------------------
HORIZONTAL SCROLL
-------------------------------------------------- */
const taskPicker = document.querySelector(".task-picker-list");
if (taskPicker) {
  taskPicker.addEventListener("wheel", (e) => {
    e.preventDefault();
    taskPicker.scrollLeft += e.deltaY;
  });
}

const searchInput = document.getElementById("task-search-input");

searchInput.addEventListener("input", () => {
  const value = searchInput.value.toLowerCase();

  document.querySelectorAll(".task-picker .task-icon").forEach((icon) => {
    const title = icon.dataset.title || "";

    if (title.includes(value)) {
      icon.style.display = "flex";
    } else {
      icon.style.display = "none";
    }
  });
});

function toggleEmptyState() {
  const label = document.getElementById("no-tasks-label");

  if (selected.length === 0) {
    label.style.display = "block";
  } else {
    label.style.display = "none";
  }
}

/* --------------------------------------------------
GROUP CLICK
-------------------------------------------------- */
document.querySelectorAll(".group-icon").forEach((icon) => {
  icon.onclick = async () => {
    const groupId = icon.dataset.id;

    const res = await fetch(`/api/groups/${groupId}/`);
    if (!res.ok) return;

    const data = await res.json();

    data.tasks.forEach((t) => {
      t.template_id = t.id; // ⚡ фикс
      addTask(t);
    });
  };
});

/* --------------------------------------------------
GROUP TOOLTIP
-------------------------------------------------- */
const gTooltip = document.getElementById("group-tooltip");

const gTitle = document.getElementById("group-tooltip-title");
const gDesc = document.getElementById("group-tooltip-description");
const gCount = document.getElementById("group-tooltip-count");
const gIcons = document.getElementById("group-tooltip-icons");

document.querySelectorAll(".group-icon").forEach((icon) => {
  icon.addEventListener("mouseenter", async () => {
    gTooltip.style.display = "block";

    gTitle.textContent = icon.dataset.title;
    gDesc.textContent = icon.dataset.description;
    gCount.textContent = icon.dataset.count;

    gIcons.innerHTML = "";

    const res = await fetch(`/api/groups/${icon.dataset.id}/`);

    if (res.ok) {
      const data = await res.json();

      data.tasks.forEach((t) => {
        if (t.icon) {
          const img = document.createElement("img");
          img.src = MEDIA_URL + t.icon;

          gIcons.appendChild(img);
        }
      });
    }
  });

  icon.addEventListener("mousemove", (e) => {
    gTooltip.style.left = e.clientX + 15 + "px";
    gTooltip.style.top = e.clientY + 15 + "px";
  });

  icon.addEventListener("mouseleave", () => {
    gTooltip.style.display = "none";
  });
});

/* --------------------------------------------------
TASK TOOLTIP
-------------------------------------------------- */
const taskTooltip = document.getElementById("task-tooltip");
const tooltipTitle = document.getElementById("tooltip-title");
const tooltipDescription = document.getElementById("tooltip-description");
const tooltipAmountTime = document.getElementById("tooltip-amount-time");

document.querySelectorAll(".task-picker .task-icon").forEach((icon) => {
  icon.addEventListener("mouseenter", () => {
    tooltipTitle.textContent = icon.dataset.title.trim() || "Без названия";
    let description = icon.dataset.description || "";

    description = description.trim().replace(/\n+$/g, ""); // убрать переносы в конце

    tooltipDescription.textContent = description;
    tooltipAmountTime.textContent = `Количество: ${icon.dataset.amount || 1}, Время: ${icon.dataset.time || 1}`;

    taskTooltip.style.display = "block";

    const rect = icon.getBoundingClientRect();
    const tooltipHeight = taskTooltip.offsetHeight || 80;

    const topPos = rect.top + window.scrollY - tooltipHeight - 8;
    const leftPos = rect.left + window.scrollX + rect.width / 2 - 110;

    taskTooltip.style.top = `${topPos}px`;
    taskTooltip.style.left = `${leftPos}px`;
  });

  icon.addEventListener("mouseleave", () => {
    taskTooltip.style.display = "none";
  });
});

const groupPanel = document.getElementById("group-panel");
const groupToggle = document.getElementById("group-toggle");

const taskPanel = document.getElementById("task-panel");
const taskToggle = document.getElementById("task-toggle");

/* INIT */

function initPanels() {
  const groupClosed = localStorage.getItem("groupClosed") === "true";
  const taskClosed = localStorage.getItem("taskClosed") === "true";

  if (groupClosed) {
    groupPanel.classList.add("closed");
    setGroupIcon(true);
  }

  if (taskClosed) {
    taskPanel.classList.add("closed");
    setTaskIcon(true);
  }
}

/* ICONS */

function setGroupIcon(closed) {
  const icon = groupToggle.querySelector("i");
  icon.className = closed ? "bi bi-chevron-right" : "bi bi-chevron-left";
}

function setTaskIcon(closed) {
  const icon = taskToggle.querySelector("i");
  icon.className = closed ? "bi bi-chevron-up" : "bi bi-chevron-down";
}

/* TOGGLES */

groupToggle.onclick = () => {
  groupPanel.classList.toggle("closed");

  const closed = groupPanel.classList.contains("closed");

  localStorage.setItem("groupClosed", closed);
  setGroupIcon(closed);
};

taskToggle.onclick = () => {
  taskPanel.classList.toggle("closed");

  const closed = taskPanel.classList.contains("closed");

  localStorage.setItem("taskClosed", closed);
  setTaskIcon(closed);
};

document.addEventListener("keydown", (e) => {
  // Ctrl+S (Windows/Linux) или Cmd+S (Mac)
  const isSaveHotkey = (e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s";

  if (!isSaveHotkey) return;

  e.preventDefault(); // важно: отключает стандартное "сохранить страницу"

  const saveBtn = document.getElementById("save-block-btn");

  if (saveBtn) {
    saveBtn.click(); // переиспользуем уже существующую логику
  }
});

/* INIT */
initPanels();