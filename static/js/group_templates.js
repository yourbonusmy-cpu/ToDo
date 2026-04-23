document.addEventListener("DOMContentLoaded", () => {
  const grid = document.querySelector(".group-grid");

  let page = 1;
  let loading = false;
  let hasNext = true;

  /* ------------------------
   JWT API FETCH
  ------------------------ */

  function apiFetch(url, options = {}) {
    const token = localStorage.getItem("access_token");

    return fetch(url, {
      ...options,
      headers: {
        ...(options.headers || {}),
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }).then(async (res) => {
      if (res.status === 401) {
        console.warn("JWT expired or invalid");
        window.location.reload();
        return null;
      }

      return res.json();
    });
  }

  /* ------------------------
   RENDER GROUP CARD
  ------------------------ */

  function createGroupCard(g) {
    const div = document.createElement("div");
    div.className = "group-card col-md-4";
    div.dataset.id = g.id;

    div.innerHTML = `
      <div class="card shadow-sm">
        <div class="card-body d-flex flex-column">

          <div class="d-flex justify-content-between align-items-center mb-2">
            <div class="fw-semibold">${g.title}</div>

            <div class="group-actions d-flex gap-2">
              <button class="btn btn-sm btn-outline-secondary edit-group" data-id="${g.id}">
                ✏
              </button>

              <button class="btn btn-sm btn-outline-danger delete-group" data-id="${g.id}">
                🗑
              </button>
            </div>
          </div>

          <div class="group-description text-muted small mb-2">
            ${g.description || ""}
          </div>

          <div class="group-task-icons d-flex flex-wrap gap-2 mb-2">
            ${g.tasks
              .map(
                (t) => `
              <div class="task-icon tooltip-task"
                data-title="${t.title}"
                data-description="${t.description || ""}"
                data-amount="${t.amount}"
                data-period="${t.period}"
                data-schedule="${t.schedule}"
                data-icon="${t.icon || ""}">

                ${
                  t.icon
                    ? `<img src="${t.icon}" width="32" height="32" />`
                    : `<div class="placeholder-icon"></div>`
                }
              </div>
            `
              )
              .join("")}
          </div>

          <div class="group-dates d-flex justify-content-between mt-auto small text-muted">
            <span>${g.updated_at}</span>
            <span>${g.created_at}</span>
          </div>

        </div>
      </div>
    `;

    grid.appendChild(div);
  }

  /* ------------------------
   LOAD GROUPS (PAGINATION)
  ------------------------ */

  function loadGroups() {
    if (loading || !hasNext) return;

    loading = true;

    apiFetch(`/api/group-templates/?page=${page}`)
      .then((data) => {
        if (!data) return;

        data.groups.forEach(createGroupCard);

        hasNext = data.has_next;
        page++;
      })
      .finally(() => {
        loading = false;
      });
  }

  /* ------------------------
   DELETE GROUP (API)
  ------------------------ */

  document.addEventListener("click", (e) => {
    const deleteBtn = e.target.closest(".delete-group");

    if (deleteBtn) {
      const id = deleteBtn.dataset.id;
      const card = deleteBtn.closest(".group-card");

      if (!confirm("Удалить группу?")) return;

      apiFetch(`/api/group-templates/${id}/delete/`, {
        method: "POST",
      }).then((data) => {
        if (data?.success) {
          card.remove();
        }
      });
    }

    /* EDIT GROUP */
    const editBtn = e.target.closest(".edit-group");

    if (editBtn) {
      const id = editBtn.dataset.id;
      window.location.href = `/group-templates/${id}/edit/`;
    }
  });

  /* ------------------------
   TOOLTIP (unchanged logic)
  ------------------------ */

  const tooltip = document.getElementById("task-tooltip");

  const tooltipTitle = document.getElementById("tooltip-title");
  const tooltipDescription = document.getElementById("tooltip-description");
  const tooltipAmount = document.getElementById("tooltip-amount");
  const tooltipPeriod = document.getElementById("tooltip-period");
  const tooltipSchedule = document.getElementById("tooltip-schedule");
  const tooltipIcon = document.getElementById("tooltip-icon");

  document.addEventListener("mouseover", (e) => {
    const icon = e.target.closest(".tooltip-task");

    if (!icon) return;

    tooltip.style.display = "block";

    tooltipTitle.textContent = icon.dataset.title;
    tooltipDescription.textContent = icon.dataset.description;
    tooltipAmount.textContent = icon.dataset.amount;
    tooltipPeriod.textContent = icon.dataset.period;
    tooltipSchedule.textContent = icon.dataset.schedule;

    if (icon.dataset.icon) {
      tooltipIcon.src = icon.dataset.icon;
      tooltipIcon.style.display = "block";
    } else {
      tooltipIcon.style.display = "none";
    }
  });

  document.addEventListener("mousemove", (e) => {
    if (tooltip.style.display === "block") {
      tooltip.style.left = e.clientX + 18 + "px";
      tooltip.style.top = e.clientY + 18 + "px";
    }
  });

  document.addEventListener("mouseout", (e) => {
    if (e.target.closest(".tooltip-task")) {
      tooltip.style.display = "none";
    }
  });

  /* ------------------------
   INFINITE SCROLL
  ------------------------ */

  window.addEventListener("scroll", () => {
    if (!hasNext || loading) return;

    const scrollBottom = window.innerHeight + window.scrollY;
    const pageHeight = document.body.offsetHeight;

    if (scrollBottom > pageHeight - 200) {
      loadGroups();
    }
  });

  /* ------------------------
   INIT
  ------------------------ */

  loadGroups();
});