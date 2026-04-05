// ================= STATE =================
let currentDate = new Date();
let cache = {};

const popover = document.getElementById("popover");

// ================= DELETE MODAL =================
const deleteModalEl = document.getElementById("deleteBlockModal");

const deleteModal = deleteModalEl
    ? new bootstrap.Modal(deleteModalEl)
    : null;

const deletePasswordInput = document.getElementById("delete-block-password");
const deleteError = document.getElementById("delete-block-error");
const confirmDeleteBtn = document.getElementById("confirm-delete-block");
const blockNameElement = document.getElementById("block-name");

let currentDeleteBlockId = null;

// ================= CSRF =================
function getCookie(name) {
    return document.cookie.split(";")
        .map(c => c.trim())
        .find(c => c.startsWith(name + "="))
        ?.split("=")[1] || null;
}

// ================= API =================
async function loadData(year, month) {
    const key = `${year}-${month}`;
    if (cache[key]) return cache[key];

    const res = await fetch(`/api/calendar/?year=${year}&month=${month}`);
    const data = await res.json();

    cache[key] = data;
    return data;
}

// ================= TOOLTIP =================
function initTooltips(root = document) {
    root.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
        if (!el._tooltip) {
            el._tooltip = new bootstrap.Tooltip(el);
        }
    });
}

// ================= RENDER =================
async function renderCalendar() {
    const grid = document.getElementById("calendarGrid");
    grid.innerHTML = "";

    const year = currentDate.getFullYear();
    const month = currentDate.getMonth() + 1;

    const data = await loadData(year, month);

    document.getElementById("monthTitle").innerText =
        currentDate.toLocaleString('ru', { month: 'long', year: 'numeric' });

    let firstDay = new Date(year, month - 1, 1).getDay();
    if (firstDay === 0) firstDay = 7;

    const daysInMonth = new Date(year, month, 0).getDate();

    // пустые клетки
    for (let i = 1; i < firstDay; i++) {
        grid.appendChild(createEmpty());
    }

    // дни
    for (let day = 1; day <= daysInMonth; day++) {
        const dateStr = `${year}-${String(month).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
        const blocks = data[dateStr];

        grid.appendChild(createDay(day, blocks));
    }

    // 🔥 активируем tooltip после рендера
    initTooltips(grid);
}

// ================= CREATE DAY =================
function createDay(day, blocks) {
    const el = document.createElement("div");
    el.className = "calendar-day";

    const today = new Date();
    if (
        today.getDate() === day &&
        today.getMonth() === currentDate.getMonth() &&
        today.getFullYear() === currentDate.getFullYear()
    ) {
        el.classList.add("today");
    }

    // добавим атрибут для дня (берем первый блок)
    if (blocks && blocks.length) {
        el.dataset.firstBlockId = blocks[0].id;
    }

    el.innerHTML = `
        <div class="day-header">
            <div class="day-number">${day}</div>

            ${blocks && blocks.length ? `
            <div class="day-actions">
                ${blocks.map(b => `
                    <div class="day-action-group"
                         data-block-id="${b.id}"
                         data-block-title="${b.title}">

                        <i class="bi bi-eye-slash action-hide"
                           data-bs-toggle="tooltip"
                           title="Скрыть"></i>

                        <i class="bi bi-pencil action-edit"
                           data-bs-toggle="tooltip"
                           title="Редактировать"></i>

                        <i class="bi bi-trash action-delete"
                           data-bs-toggle="tooltip"
                           title="Удалить"></i>

                    </div>
                `).join('')}
            </div>
            ` : ''}
        </div>

        <div class="day-icons">
            ${blocks ? blocks.flatMap(b =>
                b.tasks.map(t =>
                    t.icon ? `<img src="/media/${t.icon}">` : ''
                )
            ).join('') : ''}
        </div>
    `;

    if (blocks) {
        el.addEventListener("mouseenter", (e) => showPopover(e, blocks));
        el.addEventListener("mouseleave", hidePopover);

        // 🔥 клик на день открывает первый блок
        el.addEventListener("click", (e) => {
            // не обрабатываем клики по кнопкам
            if (e.target.closest(".day-action-group")) return;

            const blockId = el.dataset.firstBlockId;
            if (blockId) {
                window.location.href = `/block/${blockId}/view/`;
            }
        });
    }

    return el;
}

// ================= EMPTY =================
function createEmpty() {
    const el = document.createElement("div");
    el.className = "calendar-day empty";
    return el;
}

// ================= POPOVER =================
function showPopover(e, blocks) {
    popover.innerHTML = blocks.map(b => `
        <div class="mb-2">
            <b>${b.title}</b>
            <div class="small text-muted">задач: ${b.tasks_count}</div>
            <div class="d-flex flex-wrap gap-1 mt-1">
                ${b.tasks.map(t =>
                    t.icon ? `<img src="/media/${t.icon}" class="pop-icon">` : ''
                ).join('')}
            </div>
        </div>
    `).join('');

    const rect = e.target.getBoundingClientRect();

    const popWidth = 220;
    const offset = 10;

    let left = rect.right + offset;
    let top = rect.top + window.scrollY;

    if (left + popWidth > window.innerWidth) {
        left = rect.left - popWidth - offset;
    }

    const popHeight = 200;
    if (top + popHeight > window.innerHeight + window.scrollY) {
        top = window.innerHeight + window.scrollY - popHeight - 10;
    }

    popover.style.left = left + "px";
    popover.style.top = top + "px";

    popover.classList.remove("d-none");
}

function hidePopover() {
    popover.classList.add("d-none");
}

// ================= ACTIONS =================
document.getElementById("calendarGrid").addEventListener("click", async (e) => {

    const group = e.target.closest(".day-action-group");
    if (!group) return;

    const blockId = group.dataset.blockId;
    const blockTitle = group.dataset.blockTitle;

    // DELETE (modal)
    if (e.target.classList.contains("action-delete")) {
        if (!deleteModal) return;

        currentDeleteBlockId = blockId;

        blockNameElement.textContent = blockTitle;
        deletePasswordInput.value = "";
        deleteError.style.display = "none";

        deleteModal.show();
        return;
    }

    // HIDE
    if (e.target.classList.contains("action-hide")) {

        const res = await fetch(`/api/block/${blockId}/hide/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Content-Type": "application/json"
            }
        });

        const data = await res.json();

        if (data.status === "ok") {
            cache = {}; // 🔥 сбрасываем кэш
            renderCalendar();
        }

        return;
    }

    // EDIT
    if (e.target.classList.contains("action-edit")) {
        window.location.href = `/block/${blockId}/edit/`;
    }

});

// ================= CONFIRM DELETE =================
if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener("click", async () => {

        const password = deletePasswordInput.value.trim();

        if (!password) {
            deleteError.textContent = "Введите пароль";
            deleteError.style.display = "block";
            return;
        }

        const formData = new FormData();
        formData.append("password", password);

        const response = await fetch(`/api/block/${currentDeleteBlockId}/delete/`, {
            method: "POST",
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            body: formData
        });

        const data = await response.json();

        if (data.status === "ok") {
            deleteModal.hide();
            cache = {}; // 🔥 сброс кеша
            renderCalendar();
        } else {
            deleteError.textContent = data.message || "Ошибка";
            deleteError.style.display = "block";
        }

    });
}

// ================= NAV =================
document.getElementById("prevBtn").onclick = () => {
    currentDate.setMonth(currentDate.getMonth() - 1);
    renderCalendar();
};

document.getElementById("nextBtn").onclick = () => {
    currentDate.setMonth(currentDate.getMonth() + 1);
    renderCalendar();
};

// ================= INIT =================
renderCalendar();