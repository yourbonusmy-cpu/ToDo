document.addEventListener("DOMContentLoaded", () => {
  // -------------------------------
  // ELEMENTS
  // -------------------------------
  const blocksContainer = document.getElementById("blocks-container");
  const scrollTrigger = document.getElementById("scroll-trigger");

  const searchInput = document.getElementById("search-input");
  const resetBtn = document.getElementById("reset-filters");
  const tasksDropdownLabel = document.getElementById("tasks-dropdown-label");

  const deleteModal = new bootstrap.Modal(
    document.getElementById("deleteBlockModal"),
  );
  const deletePasswordInput = document.getElementById("delete-block-password");
  const deleteError = document.getElementById("delete-block-error");
  const confirmDeleteBtn = document.getElementById("confirm-delete-block");
  const blockNameElement = document.getElementById("block-name");

  const tasksSearchInput = document.getElementById("tasks-search-input");
  const tasksList = document.getElementById("tasks-list");
  const dropdown = document.querySelector(".filters-dropdown");

  // -------------------------------
  // STATE
  // -------------------------------
  let nextCursor = null;
  let loading = false;
  let hasNext = true;
  let currentDeleteBlockId = null;
  let searchTimeout = null;

  // -------------------------------
  // API FETCH
  // -------------------------------
  function apiFetch(url, options = {}) {
    const token = localStorage.getItem("access_token");

    const headers = {
      ...(options.headers || {}),
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    return fetch(url, {
      ...options,
      headers,
      credentials: "same-origin",
    }).then(async (res) => {
      if (!res.ok) return null;
      return res.json();
    });
  }

  // -------------------------------
  // UTILS
  // -------------------------------
  function escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function getCookie(name) {
    return (
      document.cookie
        .split(";")
        .map((c) => c.trim())
        .find((c) => c.startsWith(name + "="))
        ?.split("=")[1] || null
    );
  }

  function getClockIndex(time) {
    if (!time) return 12;
    const hour = parseInt(time.split(":")[0], 10);
    return hour % 12 || 12;
  }

  // -------------------------------
  // FILTERS
  // -------------------------------
  function getSelectedTasks() {
    return Array.from(document.querySelectorAll(".task-toggle:checked")).map(
      (cb) => cb.value,
    );
  }

  function buildParams() {
    const params = new URLSearchParams();

    if (searchInput.value.trim()) {
      params.append("q", searchInput.value.trim());
    }

    getSelectedTasks().forEach((id) => params.append("tasks", id));

    return params;
  }

  // -------------------------------
  // RENDER (ТОЧНО КАК DJANGO TEMPLATE)
  // -------------------------------
  function renderBlocks(blocks) {
    blocks.forEach((block) => {
      const tasksHtml = block.tasks.map((t) => {
        const idx = getClockIndex(t.time);

        return `
          <button type="button"
            class="btn position-relative task-icon-btn ${t.is_hidden ? "task-hidden" : ""}"
            data-bs-toggle="popover"
            data-bs-html="true"
            data-bs-content="
              <strong>${escapeHtml(t.title)}</strong><br>
              ${t.is_encrypted ? "<em>Зашифровано</em><br>" : escapeHtml(t.description || "—") + "<br>"}
              Кол-во: ${t.amount || 0}<br>
              Время: ${t.time || ""}
            "
          >
            ${
              t.icon
                ? `<img src="${t.icon}" width="64" height="64" class="rounded">`
                : `<div class="placeholder-icon"></div>`
            }

            <div class="clock-overlay">
              <img src="/static/img/clocks_1_12/clock-${idx}.svg"
                   class="clock-icon">
            </div>
          </button>
        `;
      }).join("");

      const html = `
        <div class="task-block card mb-3 p-0 d-flex flex-row" data-block-id="${block.id}">

          <!-- LEFT -->
          <div class="block-title-vertical">
            <a href="/block/${block.id}/view/" class="block-title-link">
              <span>${escapeHtml(block.title)}</span>
            </a>
          </div>

          <!-- CENTER -->
          <div class="block-tasks flex-grow-1 d-flex gap-3 p-3">
            ${tasksHtml}
          </div>

          <!-- RIGHT -->
          <div class="block-actions d-flex flex-column p-2">
            <div class="d-flex flex-column gap-2">

              <button class="btn btn-sm btn-outline-secondary btn-block-hide"
                      data-block-id="${block.id}">
                <i class="bi bi-eye-slash"></i>
              </button>

              <a href="/block/${block.id}/edit/" class="btn btn-sm btn-primary">
                <i class="bi bi-pencil"></i>
              </a>

              <button class="btn btn-sm btn-outline-danger btn-block-delete"
                      data-block-id="${block.id}"
                      data-block-title="${escapeHtml(block.title)}">
                <i class="bi bi-trash"></i>
              </button>

            </div>
          </div>

        </div>
      `;

      blocksContainer.insertAdjacentHTML("beforeend", html);
    });

    initPopovers();
  }

  // -------------------------------
  // LOAD BLOCKS (CURSOR)
  // -------------------------------
  async function loadBlocks(reset = false) {
    if (loading) return;
    if (!hasNext && !reset) return;

    loading = true;

    if (reset) {
      nextCursor = null;
      hasNext = true;
      blocksContainer.innerHTML = "";
    }

    const params = buildParams();

    if (nextCursor && !reset) {
      params.append("cursor", nextCursor);
    }

    const data = await apiFetch(`/api/blocks/?${params}`);

    if (!data) {
      loading = false;
      return;
    }

    renderBlocks(data.results || []);

    nextCursor = data.next
      ? new URL(data.next).searchParams.get("cursor")
      : null;

    hasNext = !!data.next;

    loading = false;
  }

  // -------------------------------
  // POPOVERS
  // -------------------------------
  function initPopovers() {
    document.querySelectorAll(".task-icon-btn").forEach((el) => {
      if (!el._bsPopover) {
        el._bsPopover = new bootstrap.Popover(el, {
          trigger: "hover",
          placement: "top",
        });
      }
    });
  }

  // -------------------------------
  // EVENTS
  // -------------------------------
  searchInput.addEventListener("input", () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => loadBlocks(true), 300);
  });

  resetBtn.addEventListener("click", () => {
    searchInput.value = "";
    document.querySelectorAll(".task-toggle").forEach(cb => cb.checked = false);
    loadBlocks(true);
  });

  // -------------------------------
  // ACTIONS
  // -------------------------------
  blocksContainer.addEventListener("click", async (e) => {
    const hideBtn = e.target.closest(".btn-block-hide");
    if (hideBtn) {
      const id = hideBtn.dataset.blockId;

      const res = await apiFetch(`/api/block/${id}/hide/`, {
        method: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
      });

      if (res?.status === "ok") {
        const el = document.querySelector(`[data-block-id="${id}"]`);
        el?.classList.toggle("d-none", res.is_hidden);
      }
      return;
    }

    const delBtn = e.target.closest(".btn-block-delete");
    if (delBtn) {
      currentDeleteBlockId = delBtn.dataset.blockId;
      blockNameElement.textContent = delBtn.dataset.blockTitle;
      deleteModal.show();
      return;
    }

    const title = e.target.closest(".block-title-link");
    if (title) {
      // normal link
    }
  });

  // -------------------------------
  // DELETE
  // -------------------------------
  confirmDeleteBtn.addEventListener("click", async () => {
    const password = deletePasswordInput.value.trim();
    if (!password) return;

    const formData = new FormData();
    formData.append("password", password);

    const res = await apiFetch(`/api/block/${currentDeleteBlockId}/delete/`, {
      method: "POST",
      headers: { "X-CSRFToken": getCookie("csrftoken") },
      body: formData,
    });

    if (res?.status === "ok") {
      document.querySelector(`[data-block-id="${currentDeleteBlockId}"]`)?.remove();
      deleteModal.hide();
    } else {
      deleteError.textContent = res?.message || "Ошибка";
      deleteError.style.display = "block";
    }
  });

    const deletePasswordEye = document.getElementById("delete-password-eye");

if (deletePasswordEye) {
  deletePasswordEye.addEventListener("click", () => {
    const input = deletePasswordInput;

    const isPassword = input.type === "password";
    input.type = isPassword ? "text" : "password";

    deletePasswordEye.innerHTML = isPassword
      ? '<i class="bi bi-eye-slash"></i>'
      : '<i class="bi bi-eye"></i>';
  });
}

  // -------------------------------
  // INIT
  // -------------------------------
  loadBlocks(true);
});