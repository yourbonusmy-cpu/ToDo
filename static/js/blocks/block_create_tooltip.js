
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