import {
  escapeHtml,
  clockIconIndex,
  buildPopover,
  resolveMedia,
} from "./ui-render-utils.js";

export function renderBlock(block) {
  const tasksHtml = (block.tasks || []).map((t) => {
    const icon = resolveMedia(t.icon);
    const clock = clockIconIndex(t.time);

    return `
      <button type="button"
        class="btn position-relative task-icon-btn ${t.is_hidden ? "task-hidden" : ""}"
        data-bs-toggle="popover"
        data-bs-html="true"
        data-bs-content="${buildPopover(t)}"
      >
        ${
          icon
            ? `<img src="${icon}" width="64" height="64" class="rounded">`
            : `<div class="placeholder-icon"></div>`
        }

        <div class="clock-overlay">
          <img src="/static/img/clocks_1_12/clock-${clock}.svg"
               class="clock-icon">
        </div>
      </button>
    `;
  }).join("");

  return `
    <div class="task-block card mb-3 p-0 d-flex flex-row"
         data-block-id="${block.id}">

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

          <a href="/block/${block.id}/edit/"
             class="btn btn-sm btn-primary">
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
}