import { renderBlock } from "./blockRenderer.js";

// -------------------------------
// STATE
// -------------------------------
let cursor = null;
let loading = false;
let hasNext = true;
let searchTimeout = null;
let currentDeleteBlockId = null;

// -------------------------------
// ELEMENTS
// -------------------------------
const container = document.getElementById("blocks-container");
const searchInput = document.getElementById("search-input");
const resetBtn = document.getElementById("reset-filters");

const dropdown = document.querySelector(".filters-dropdown");
const tasksSearchInput = document.getElementById("tasks-search-input");
const tasksList = document.getElementById("tasks-list");
const resetTasksBtn = document.getElementById("reset-tasks-filter");

const weekdayCheckboxes = document.querySelectorAll(".weekday-toggle");

const eye = document.getElementById("delete-password-eye");
const passwordInput = document.getElementById("delete-block-password");

const scrollTrigger = document.getElementById("scroll-trigger");

// -------------------------------
// API FETCH
// -------------------------------
function apiFetch(url, options = {}) {
  const token = localStorage.getItem("access_token");

  return fetch(url, {
    ...options,
    headers: {
      ...(options.headers || {}),
      "Content-Type": "application/json",
      Authorization: token ? `Bearer ${token}` : "",
    },
  }).then(async (res) => {
    const data = await res.json().catch(() => null);

    if (!res.ok) {
      console.error("API ERROR:", data);
      return null;
    }

    return data;
  });
}

// -------------------------------
// FILTER HELPERS
// -------------------------------
function getWeekdays() {
  return Array.from(document.querySelectorAll(".weekday-toggle:checked"))
    .map(cb => cb.dataset.day);
}

function resetState() {
  cursor = null;
  hasNext = true;
}

function buildParams() {
  const params = new URLSearchParams();

  if (searchInput?.value?.trim()) {
    params.append("q", searchInput.value.trim());
  }

  document.querySelectorAll(".task-toggle:checked").forEach(cb => {
    params.append("tasks", cb.value);
  });

  getWeekdays().forEach(day => {
    params.append("weekdays", day);
  });

  if (cursor) {
    params.append("cursor", cursor);
  }

  return params;
}

// -------------------------------
// LOAD BLOCKS
// -------------------------------
async function load(reset = false) {
  if (loading) return;
  if (!hasNext && !reset) return;

  loading = true;

  if (reset) {
    container.innerHTML = "";
    cursor = null;
    hasNext = true;
  }

  const data = await apiFetch(`/api/blocks/?${buildParams()}`);

  if (!data) {
    loading = false;
    return;
  }

  (data.results || []).forEach(block => {
    container.insertAdjacentHTML("beforeend", renderBlock(block));
  });

  cursor = data.next
    ? new URL(data.next).searchParams.get("cursor")
    : null;

  hasNext = !!data.next;

  initPopovers();
  enableHorizontalScroll(); // 👈 важно
  loading = false;
}

// -------------------------------
// POPOVERS
// -------------------------------
function initPopovers() {
  document.querySelectorAll(".task-icon-btn").forEach(el => {
    if (!el._popover) {
      el._popover = new bootstrap.Popover(el, {
        trigger: "hover",
        html: true,
      });
    }
  });
}

// -------------------------------
// SEARCH
// -------------------------------
searchInput?.addEventListener("input", () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => load(true), 300);
});

// -------------------------------
// TASK FILTER
// -------------------------------
document.querySelectorAll(".task-toggle").forEach(cb => {
  cb.addEventListener("change", () => load(true));
});

// -------------------------------
// WEEKDAY FILTER
// -------------------------------
weekdayCheckboxes.forEach(cb => {
  cb.addEventListener("change", () => {
    updateWeekdayLabel();
    load(true);
  });
});

function updateWeekdayLabel() {
  const selected = getWeekdays();
  const label = document.getElementById("weekday-dropdown-label");

  if (!label) return;

  if (!selected.length) {
    label.textContent = "Дни недели";
  } else {
    label.textContent = `Дни (${selected.length})`;
  }
}

// -------------------------------
// TASK DROPDOWN SEARCH
// -------------------------------
if (dropdown) {
  dropdown.addEventListener("show.bs.dropdown", () => {
    tasksSearchInput?.classList.remove("d-none");
    setTimeout(() => tasksSearchInput?.focus(), 100);
  });

  dropdown.addEventListener("hide.bs.dropdown", () => {
    if (tasksSearchInput) {
      tasksSearchInput.value = "";
      tasksSearchInput.classList.add("d-none");
    }

    tasksList?.querySelectorAll(".task-item").forEach(el => {
      el.style.display = "";
    });
  });
}

tasksSearchInput?.addEventListener("input", () => {
  const q = tasksSearchInput.value.toLowerCase();

  tasksList?.querySelectorAll(".task-item").forEach(item => {
    item.style.display =
      item.innerText.toLowerCase().includes(q) ? "" : "none";
  });
});

tasksSearchInput?.addEventListener("click", e => e.stopPropagation());

// -------------------------------
// RESET FILTERS (ALL)
// -------------------------------
resetBtn?.addEventListener("click", () => {
  searchInput.value = "";

  document.querySelectorAll(".task-toggle").forEach(cb => cb.checked = false);
  document.querySelectorAll(".weekday-toggle").forEach(cb => cb.checked = false);

  updateWeekdayLabel();

  resetState();
  load(true);
});

// -------------------------------
// RESET TASKS ONLY
// -------------------------------
resetTasksBtn?.addEventListener("click", (e) => {
  e.preventDefault();
  e.stopPropagation();

  document.querySelectorAll(".task-toggle").forEach(cb => cb.checked = false);

  if (tasksSearchInput) tasksSearchInput.value = "";

  tasksList?.querySelectorAll(".task-item").forEach(el => {
    el.style.display = "";
  });

  load(true);
});

// -------------------------------
// CLICK EVENTS
// -------------------------------
if (eye && passwordInput) {
  eye.addEventListener("click", () => {
    const isHidden = passwordInput.type === "password";

    passwordInput.type = isHidden ? "text" : "password";

    eye.innerHTML = isHidden
      ? '<i class="bi bi-eye-slash"></i>'
      : '<i class="bi bi-eye"></i>';
  });
}

document.addEventListener("click", async (e) => {
  const delBtn = e.target.closest(".btn-block-delete");

  if (delBtn) {
    currentDeleteBlockId = delBtn.dataset.blockId;

    document.getElementById("block-name").textContent =
      delBtn.dataset.blockTitle;

    document.getElementById("delete-block-password").value = "";
    document.getElementById("delete-block-error").style.display = "none";

    new bootstrap.Modal(
      document.getElementById("deleteBlockModal")
    ).show();

    return;
  }

  const hideBtn = e.target.closest(".btn-block-hide");

  if (hideBtn) {
    const blockId = hideBtn.dataset.blockId;

    const data = await apiFetch(`/api/block/${blockId}/hide/`, {
      method: "POST",
    });

    if (data?.status === "ok") {
      document
        .querySelector(`[data-block-id="${blockId}"]`)
        ?.classList.toggle("d-none", data.is_hidden);
    }
  }
});

function enableHorizontalScroll() {
  document.querySelectorAll(".block-tasks").forEach(container => {

    if (container._wheelBound) return;
    container._wheelBound = true;

    container.addEventListener("wheel", (e) => {
      if (container.scrollWidth > container.clientWidth) {
        e.preventDefault();
        container.scrollLeft += e.deltaY;
      }
    }, { passive: false });

  });
}


if (scrollTrigger) {
  const observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) {
      load(false); // 👈 ДОГРУЗКА
    }
  }, {
    rootMargin: "200px"
  });

  observer.observe(scrollTrigger);
}

// -------------------------------
// INIT
// -------------------------------
load(true);
updateWeekdayLabel();