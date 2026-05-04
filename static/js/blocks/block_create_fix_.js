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

const passwordToggle = document.getElementById("task-password-toggle");
const passwordContainer = document.getElementById("task-password-container");
const passwordInput = document.getElementById("task-password");
const passwordEye = document.getElementById("password-eye");
const decryptBtn = document.getElementById("decrypt-btn");
const encryptedLabel = document.getElementById("encrypted-label");

const selected = [];
const taskState = {};

/* --------------------------------------------------
BLOCK ID
-------------------------------------------------- */

const blockIdInput = document.getElementById("block-id");
const blockId = blockIdInput ? blockIdInput.value : null;

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
  if (!state.is_encrypted) {
    // Если описание не зашифровано
    encryptedLabel.style.display = "none";
    passwordContainer.style.display = "none";
    decryptBtn.style.display = "none";
    detailDescription.style.display = "block";
    detailDescription.disabled = false; // Разрешаем редактировать описание

    // Разрешаем использовать переключатель, если описание не зашифровано
    passwordToggle.disabled = false;

    return;
  }

  // Если описание зашифровано
  encryptedLabel.style.display = "inline-flex";
  passwordContainer.style.display = "flex";
  decryptBtn.style.display = "inline-flex";

  if (state.decrypted) {
    // Если описание расшифровано
    detailDescription.style.display = "block"; // Показываем поле для редактирования
    detailDescription.disabled = false; // Разрешаем редактировать описание
    decryptBtn.style.display = "none"; // Скрываем кнопку расшифровки
    encryptedLabel.textContent = "Расшифровано"; // Меняем метку на "Расшифровано"

    // Разрешаем использовать переключатель, если описание расшифровано
    passwordToggle.disabled = false; // Переключатель теперь активен
  } else {
    // Если описание не расшифровано
    detailDescription.style.display = "none"; // Скрываем поле для редактирования
    detailDescription.disabled = true; // Запрещаем редактировать описание
    encryptedLabel.textContent = "Зашифровано"; // Отображаем метку "Зашифровано"

    // Отключаем переключатель, если описание не расшифровано
    passwordToggle.disabled = true; // Переключатель отключен
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
                ${taskData.icon ? `<img src="${taskData.icon}" width="48" height="48">` : ""}
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
      title: taskData.title,
      description: taskData.description || "",

      amount: parseInt(taskData.amount) || 1,
      time: parseFloat(taskData.time) || 1,

      iconSrc: taskData.icon || "",

      is_encrypted: taskData.is_encrypted || false,
      password: "",
      is_hidden: taskData.is_hidden || false,

      decrypted: false,
      description_changed: false,
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

  detailIcon.src = state.iconSrc;
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
  } else {
    // если пользователь только что включил шифрование
    // текст уже находится в textarea → считаем его расшифрованным
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

  if (!password) {
    alert("Введите пароль");
    return;
  }

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
      title: icon.dataset.title,
      description: icon.dataset.description,
      amount: icon.dataset.amount,
      time: icon.dataset.time,

      icon: icon.querySelector("img") ? icon.querySelector("img").src : "",
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
    const ids = Array.from(selectedContainer.children).map(
      (el) => el.dataset.id,
    );

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

  const tasksData = selected.map((id) => {
    const state = taskState[id];

    let password = "";

    if (state.is_encrypted && state.password) {
      password = state.password;
    }

    return {
      id: id.startsWith("new-") ? null : parseInt(id),

      title: state.title,
      description: state.description,

      decrypted: state.decrypted,

      is_encrypted: state.is_encrypted,
      is_hidden: state.is_hidden,

      password: password,

      amount: state.amount,
      time: state.time,

      icon: state.iconSrc,
    };
  });

  const url = window.location.href;

  const formData = new FormData();

  formData.append("title", blockTitleInput.value);
  formData.append("tasks", JSON.stringify(tasksData));
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

    if (task.is_encrypted) {
      taskState[id].description = task.description || "";
      taskState[id].decrypted = false;
    } else {
      taskState[id].description = task.description || "";
      taskState[id].decrypted = true;
    }

    updateTaskVisibility(id);
    toggleEmptyState();
  });
}

loadBlock();

selectedContainer.addEventListener("wheel", (e) => {
  if (e.deltaY === 0) return;

  e.preventDefault();

  selectedContainer.scrollLeft += e.deltaY;
});

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
          img.src = t.icon;

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
