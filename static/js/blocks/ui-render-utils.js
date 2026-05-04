// -------------------------------
// SAFE HTML
// -------------------------------
export function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// -------------------------------
// CLOCK FILTER (как Django clock_filters)
// -------------------------------
export function clockIconIndex(time) {
  if (time == null) return 12;

  if (typeof time === "number") {
    const hours = Math.floor(time); // 14.5 → 14
    const normalized = ((hours % 12) + 12) % 12;
    return normalized || 12;
  }

  if (typeof time === "string") {
    const parts = time.split(":");
    if (parts.length < 2) return 12;

    const hour = parseInt(parts[0], 10);
    if (isNaN(hour)) return 12;

    return ((hour % 12) + 12) % 12 || 12;
  }

  return 12;
}

// -------------------------------
// MEDIA RESOLVER
// -------------------------------
export function resolveMedia(url) {
  if (!url) return null;
  if (url.startsWith("http")) return url;
  return `/media/${url}`;
}

// -------------------------------
// POPOVER (1:1 Django logic)
// -------------------------------
export function buildPopover(task) {
  const title = escapeHtml(task.title || "");

  const description = task.is_encrypted
    ? "<em>Зашифровано</em>"
    : escapeHtml(task.description || "—");

  return `
    <strong>${title}</strong><br>
    ${description}<br>
    Кол-во: ${task.amount ?? "—"}<br>
    Время: ${task.time ?? "—"}
  `;
}