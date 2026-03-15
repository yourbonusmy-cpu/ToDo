/* --------------------------------------------------
STATE
-------------------------------------------------- */
const visibilityEye = document.getElementById("visibility-eye");
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

const selected = [];
const taskState = {};

/* --------------------------------------------------
BLOCK ID (edit mode)
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

visibilityEye.addEventListener("click", () => {

    const id = taskDetailCard.dataset.currentTaskId;
    if (!id) return;

    const state = taskState[id];

    state.is_hidden = !state.is_hidden;

    updateDetailEyeIcon(state.is_hidden);

});

function updateDetailEyeIcon(isHidden) {

    const icon = visibilityEye.querySelector("i");

    if (isHidden) {
        icon.classList.remove("bi-eye");
        icon.classList.add("bi-eye-slash");
    } else {
        icon.classList.remove("bi-eye-slash");
        icon.classList.add("bi-eye");
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

            <button
                class="btn btn-danger btn-sm position-absolute top-0 start-100 translate-middle rounded-circle remove-task"
            >
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
        };
    }

    showTaskDetail(id);
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
    detailDescription.value = state.description;

    taskDetailCard.dataset.currentTaskId = id;

    /* PASSWORD STATE */

    passwordToggle.checked = state.is_encrypted;
    updateDetailEyeIcon(state.is_hidden);

    if (state.is_encrypted) {

        passwordContainer.style.display = "block";
        passwordInput.value = state.password;

    } else {

        passwordContainer.style.display = "none";
        passwordInput.value = "";

    }
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
    if (id) taskState[id].description = detailDescription.value;
});

/* --------------------------------------------------
PASSWORD TOGGLE
-------------------------------------------------- */
passwordToggle.addEventListener("change", () => {

    const id = taskDetailCard.dataset.currentTaskId;
    if (!id) return;

    const state = taskState[id];

    state.is_encrypted = passwordToggle.checked;

    if (state.is_encrypted) {

        passwordContainer.style.display = "block";

    } else {

        passwordContainer.style.display = "none";
        passwordInput.value = "";
        state.password = "";

    }

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

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
    } else {
        passwordInput.type = "password";
    }

});

/* --------------------------------------------------
TASK PICKER CLICK
-------------------------------------------------- */
document.querySelectorAll(".task-picker .task-icon").forEach(icon => {

    icon.addEventListener("click", () => {

        const taskData = {
            id: icon.dataset.id,
            title: icon.dataset.title,
            description: icon.dataset.description,
            amount: icon.dataset.amount,
            icon: icon.querySelector("img") ? icon.querySelector("img").src : "",
        };

        addTask(taskData);

    });

});

/* --------------------------------------------------
SORTABLE
-------------------------------------------------- */
new Sortable(selectedContainer, {
    animation: 150,
    onEnd() {
        const ids = Array.from(selectedContainer.children).map(el => el.dataset.id);
        selected.length = 0;
        ids.forEach(id => selected.push(id));
    }
});

/* --------------------------------------------------
CLEAR BLOCK
-------------------------------------------------- */
document.getElementById("clear-block-btn").onclick = () => {

    selected.length = 0;
    selectedContainer.innerHTML = "";

    for (let key in taskState) delete taskState[key];

    taskDetailCard.style.display = "none";
};

/* --------------------------------------------------
SAVE BLOCK
-------------------------------------------------- */
document.getElementById("save-block-btn").onclick = async () => {

    if (!blockTitleInput.value.trim()) {
        alert("Введите название блока");
        return;
    }

    const tasksData = selected.map(id => {
        const state = taskState[id];
        let password = "";
        if (state.is_encrypted && state.password) {
            password = state.password;
        }

        return {
            id: id.startsWith("new-") ? null : parseInt(id),
            title: state.title,
            description: state.description,
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
        body: formData
    });

    if (response.redirected) {
        window.location.href = response.url;
    } else {
        alert("Ошибка при сохранении блока");
    }
};

/* --------------------------------------------------
LOAD BLOCK (edit)
-------------------------------------------------- */
function loadBlock() {

    if (!block_json) return;

    blockTitleInput.value = block_json.title;

    block_json.tasks.forEach(task => {

        addTask(task);

        const id = task.id.toString();

        taskState[id].amount = task.amount;
        taskState[id].time = task.time;
        taskState[id].description = task.description;
        taskState[id].is_hidden = task.is_hidden;

    });
}

loadBlock();



/* --------------------------------------------------
HORIZONTAL SCROLL
-------------------------------------------------- */
const taskPicker = document.querySelector(".task-picker");

if (taskPicker) {

    taskPicker.addEventListener("wheel", (e) => {

        e.preventDefault();
        taskPicker.scrollLeft += e.deltaY;

    });

}

/* --------------------------------------------------
GROUP CLICK
-------------------------------------------------- */
document.querySelectorAll(".group-icon").forEach(icon => {

    icon.onclick = async () => {

        const groupId = icon.dataset.id;

        const res = await fetch(`/api/groups/${groupId}/`);
        if (!res.ok) return;

        const data = await res.json();

        data.tasks.forEach(t => addTask(t));

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

document.querySelectorAll(".group-icon").forEach(icon => {

    icon.addEventListener("mouseenter", async () => {

        gTooltip.style.display = "block";

        gTitle.textContent = icon.dataset.title;
        gDesc.textContent = icon.dataset.description;
        gCount.textContent = icon.dataset.count;

        gIcons.innerHTML = "";

        const res = await fetch(`/api/groups/${icon.dataset.id}/`);

        if (res.ok) {

            const data = await res.json();

            data.tasks.forEach(t => {

                if (t.icon) {

                    const img = document.createElement("img");
                    img.src = t.icon;

                    gIcons.appendChild(img);

                }

            });

        }

    });

    icon.addEventListener("mousemove", (e) => {

        gTooltip.style.left = (e.clientX + 15) + "px";
        gTooltip.style.top = (e.clientY + 15) + "px";

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

document.querySelectorAll(".task-picker .task-icon").forEach(icon => {

    icon.addEventListener("mouseenter", () => {

        tooltipTitle.textContent = icon.dataset.title.trim() || "Без названия";
        let description = icon.dataset.description || "";

        description = description
            .trim()
            .replace(/\n+$/g, "")     // убрать переносы в конце

        tooltipDescription.textContent = description;
        tooltipAmountTime.textContent =
            `Количество: ${icon.dataset.amount || 1}, Время: ${icon.dataset.time || 1}`;

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
