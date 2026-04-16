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
  const resetTasksBtn = document.getElementById("reset-tasks-filter");



  // -------------------------------
  // STATE
  // -------------------------------
  let page = 1;
  let loading = false;
  let hasNext = true;
  let currentDeleteBlockId = null;
  let searchTimeout = null;

  // -------------------------------
  // CSRF
  // -------------------------------
  function getCookie(name) {
    return (
      document.cookie
        .split(";")
        .map((c) => c.trim())
        .find((c) => c.startsWith(name + "="))
        ?.split("=")[1] || null
    );
  }

  dropdown.addEventListener("show.bs.dropdown", () => {
    tasksSearchInput.classList.remove("d-none");

    // автофокус
    setTimeout(() => tasksSearchInput.focus(), 100);
  });

  dropdown.addEventListener("hide.bs.dropdown", () => {
    tasksSearchInput.value = "";
    tasksSearchInput.classList.add("d-none");

    // показать все задачи обратно
    tasksList.querySelectorAll(".task-item").forEach((el) => {
      el.style.display = "";
    });
  });

  tasksSearchInput.addEventListener("input", () => {
    const query = tasksSearchInput.value.toLowerCase();

    tasksList.querySelectorAll(".task-item").forEach((item) => {
      const text = item.innerText.toLowerCase();

      if (text.includes(query)) {
        item.style.display = "";
      } else {
        item.style.display = "none";
      }
    });
  });
  tasksSearchInput.addEventListener("click", (e) => {
    e.stopPropagation();
  });

  // -------------------------------
  // FILTER STATE
  // -------------------------------
  function getSelectedTasks() {
    return Array.from(document.querySelectorAll(".task-toggle:checked")).map(
      (cb) => cb.value,
    );
  }

  function updateTasksLabel() {
    const selected = getSelectedTasks();

    if (!selected.length) {
      tasksDropdownLabel.textContent = "Задачи";
    } else if (selected.length === 1) {
      const cb = document.querySelector(`.task-toggle[value="${selected[0]}"]`);
      tasksDropdownLabel.textContent =
        cb?.closest(".form-check")?.innerText.trim() || "1 задача";
    } else {
      tasksDropdownLabel.textContent = `Задачи (${selected.length})`;
    }
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
  // LOAD BLOCKS
  // -------------------------------
  async function loadBlocks(reset = false) {
    if (loading) return;
    if (!hasNext && !reset) return;

    loading = true;

    if (reset) {
      page = 1;
      hasNext = true;
      blocksContainer.innerHTML = "";
    }

    const params = buildParams();
    params.append("page", page);

    const response = await fetch(`/api/blocks/?${params}`);
    if (!response.ok) {
      loading = false;
      return;
    }

    const data = await response.json();

    if (data.html && data.html.trim()) {
      blocksContainer.insertAdjacentHTML("beforeend", data.html);

      initPopovers(blocksContainer);

      page += 1;
      hasNext = data.has_next;
    } else {
      hasNext = false;
    }

    loading = false;
  }

  // -------------------------------
  // POPOVERS
  // -------------------------------
  function initPopovers(root) {
    root.querySelectorAll(".task-icon-btn").forEach((el) => {
      if (!el._bsPopover) {
        new bootstrap.Popover(el, {
          trigger: "hover",
          placement: "top",
        });
      }
    });
  }

  // -------------------------------
  // EVENT DELEGATION (CORE)
  // -------------------------------
  blocksContainer.addEventListener("click", async (e) => {
    // DELETE
    const deleteBtn = e.target.closest(".btn-block-delete");
    if (deleteBtn) {
      currentDeleteBlockId = deleteBtn.dataset.blockId;
      blockNameElement.textContent = deleteBtn.dataset.blockTitle;
      deletePasswordInput.value = "";
      deleteError.style.display = "none";
      deleteModal.show();
      return;
    }

    // HIDE
    const hideBtn = e.target.closest(".btn-block-hide");
    if (hideBtn) {
      const blockId = hideBtn.dataset.blockId;
      const blockEl = document.querySelector(`[data-block-id="${blockId}"]`);

      const response = await fetch(`/api/block/${blockId}/hide/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();

      if (data.status === "ok") {
        blockEl.classList.toggle("d-none", data.is_hidden);
      }
      return;
    }

    // OPEN BLOCK
    const title = e.target.closest(".block-title-clickable");
    if (title) {
      const blockId = title.closest(".task-block").dataset.blockId;
      window.location.href = `/block/${blockId}/view/`;
    }
  });

  // -------------------------------
  // FILTER EVENTS
  // -------------------------------
  searchInput.addEventListener("input", () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => loadBlocks(true), 400);
  });

  document.querySelectorAll(".task-toggle").forEach((cb) => {
    cb.addEventListener("click", (e) => {
      e.stopPropagation();
      updateTasksLabel();
      loadBlocks(true);
    });
  });

  document.querySelectorAll(".form-check-label").forEach((label) => {
    label.addEventListener("click", (e) => e.stopPropagation());
  });

  // -------------------------------
  // RESET
  // -------------------------------
  resetBtn.addEventListener("click", () => {
    searchInput.value = "";

    document
      .querySelectorAll(".task-toggle")
      .forEach((cb) => (cb.checked = false));

    updateTasksLabel();
    loadBlocks(true);
  });

  // -------------------------------
  // DELETE CONFIRM
  // -------------------------------
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
      body: formData,
    });

    const data = await response.json();

    if (data.status === "ok") {
      deleteModal.hide();

      const blockEl = document.querySelector(
        `[data-block-id="${currentDeleteBlockId}"]`,
      );

      if (blockEl) blockEl.remove();
    } else {
      deleteError.textContent = data.message || "Ошибка";
      deleteError.style.display = "block";
    }
  });

  // -------------------------------
  // INFINITE SCROLL
  // -------------------------------
  if (scrollTrigger) {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          loadBlocks();
        }
      },
      { rootMargin: "200px" },
    );

    observer.observe(scrollTrigger);
  }
  // -------------------------------
  // TOGGLE PASSWORD VISIBILITY
  // -------------------------------
  const deletePasswordEye = document.getElementById("delete-password-eye");

  if (deletePasswordEye) {
    deletePasswordEye.addEventListener("click", () => {
      const input = deletePasswordInput;

      if (input.type === "password") {
        input.type = "text";
        deletePasswordEye.innerHTML = '<i class="bi bi-eye-slash"></i>';
      } else {
        input.type = "password";
        deletePasswordEye.innerHTML = '<i class="bi bi-eye"></i>';
      }
    });
  }

  if (resetTasksBtn) {
      resetTasksBtn.addEventListener("click", (e) => {
        e.stopPropagation(); // важно: чтобы dropdown не схлопнулся раньше времени


        document
          .querySelectorAll(".task-toggle")
          .forEach((cb) => (cb.checked = false));

        updateTasksLabel();
        loadBlocks(true);
        e.preventDefault();
      });
    }

  // -------------------------------
  // INIT
  // -------------------------------
  updateTasksLabel();
  initPopovers(document);
  loadBlocks(true);
});
