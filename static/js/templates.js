document.addEventListener("DOMContentLoaded", () => {

const systemPanel = document.querySelector(".system-scroll");
const templatesGrid = document.querySelector(".templates-grid");
const searchInput = document.getElementById("template-search");

const systemPanelEl = document.getElementById("system-panel");
const toggleBtn = document.getElementById("system-toggle");

let activePopover = null;

let currentPage = 1;
let currentQuery = "";
let isLoading = false;
let hasNext = true;

/* -------------------
CSRF
------------------- */

function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {
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


function initSystemPanel(){

    const hasTemplates = document.querySelectorAll(".system-icon-wrapper").length > 0;

    // если нет шаблонов → скрыть полностью
    if(!hasTemplates){
        systemPanelEl.closest(".system-panel-wrapper").classList.add("hidden");
        return;
    }

    const saved = localStorage.getItem("systemPanelClosed");

    const icon = toggleBtn?.querySelector("i");

    if(saved === "true"){
        systemPanelEl.classList.add("closed");
        toggleBtn.classList.add("closed");

        if(icon){
            icon.className = "bi bi-chevron-right";
        }
    } else {
        if(icon){
            icon.className = "bi bi-chevron-left";
        }
    }
}

toggleBtn?.addEventListener("click", () => {

    systemPanelEl.classList.toggle("closed");

    const isClosed = systemPanelEl.classList.contains("closed");

    // сохраняем состояние
    localStorage.setItem("systemPanelClosed", isClosed);

    // синхронизация кнопки
    toggleBtn.classList.toggle("closed", isClosed);

    // 🔥 меняем иконку
    const icon = toggleBtn.querySelector("i");

    if(icon){
        icon.className = isClosed
            ? "bi bi-chevron-right"
            : "bi bi-chevron-left";
    }

});

/* -------------------
API LOAD
------------------- */

function loadTemplates({ reset = false } = {}) {

    if(isLoading || !hasNext) return;

    isLoading = true;

    fetch(`/api/templates/?q=${encodeURIComponent(currentQuery)}&page=${currentPage}`, {
        headers: {
            "X-Requested-With": "XMLHttpRequest"
        }
    })
    .then(r => r.json())
    .then(data => {

        if(reset){
            templatesGrid.innerHTML = "";
        }

        data.results.forEach(t => createTemplateCard(t));

        hasNext = data.has_next;
        currentPage++;

    })
    .finally(() => {
        isLoading = false;
    });

}


/* -------------------
CREATE TEMPLATE CARD
------------------- */

function createTemplateCard(t){

    const card = document.createElement("div");

    card.className = "template-card card shadow-sm";
    card.dataset.id = t.id;

    if(t.system_id){
        card.dataset.systemId = t.system_id;
    }

    card.innerHTML = `
    <div class="card-body d-flex gap-3 position-relative">

        ${t.selected_count > 0 ? `
            <div class="template-badge">
                ${t.selected_count}
            </div>
        ` : ""}

        <div class="template-left d-flex flex-column align-items-center">

            ${t.icon
                ? `<img src="${t.icon}" class="template-icon rounded mb-1">`
                : `<div class="placeholder rounded mb-1"></div>`
            }

            <div class="template-meta text-center small text-muted">
                Кол-во: ${t.amount}<br>
                P${t.priority} | ${t.period} | ${t.schedule}
            </div>

        </div>

        <div class="template-content d-flex flex-column flex-grow-1">

            <div class="d-flex justify-content-between align-items-center">

                <div class="template-title fw-semibold">
                    ${t.title}
                </div>

                <div class="template-actions d-flex gap-2">

                    <button class="btn btn-sm btn-outline-secondary edit-template">
                        <i class="bi bi-pencil-square"></i>
                    </button>

                    <button class="btn btn-sm btn-outline-danger delete-template">
                        <i class="bi bi-trash"></i>
                    </button>

                </div>

            </div>

            <div class="template-description text-muted small">
                ${t.description || ""}
            </div>

            <div class="template-dates d-flex justify-content-between mt-auto small text-muted">
                <span>${t.updated_at}</span>
                <span>${t.created_at}</span>
            </div>
        </div>

    </div>
    `;

    templatesGrid.appendChild(card);
}


/* -------------------
POPOVER
------------------- */

function attachPopover(wrapper){

    wrapper.addEventListener("mouseenter", () => {

        if(activePopover){
            activePopover.dispose();
        }

        const content = `
            <div class="small">
                <div class="fw-semibold mb-1">${wrapper.dataset.title}</div>
                <div class="text-muted mb-2">${wrapper.dataset.description}</div>
                <div class="text-muted">
                    Кол-во: ${wrapper.dataset.amount}<br>
                    ${wrapper.dataset.period} | ${wrapper.dataset.schedule}
                </div>
            </div>
        `;

        activePopover = new bootstrap.Popover(wrapper, {
            content: content,
            html: true,
            trigger: "manual",
            placement: "right",
            customClass: "modern-popover"
        });

        activePopover.show();

    });

    wrapper.addEventListener("mouseleave", () => {
        if(activePopover){
            activePopover.dispose();
            activePopover = null;
        }
    });

}


/* -------------------
INIT POPOVERS
------------------- */

document.querySelectorAll(".system-icon-wrapper")
    .forEach(attachPopover);


/* -------------------
CREATE SYSTEM ICON
------------------- */

function createSystemIcon(data){

    const wrapper = document.createElement("div");

    wrapper.className = "system-icon-wrapper";

    wrapper.dataset.id = data.system_id;
    wrapper.dataset.title = data.title;
    wrapper.dataset.description = data.description;
    wrapper.dataset.amount = data.amount;
    wrapper.dataset.period = data.period;
    wrapper.dataset.schedule = data.schedule;

    wrapper.innerHTML = `
        ${data.icon ? `<img src="${data.icon}" class="system-icon">` : ""}
        <button class="system-add">+</button>
    `;

    systemPanel.appendChild(wrapper);

    attachPopover(wrapper);

    // показать panel если была скрыта
    systemPanelEl.closest(".system-panel-wrapper").classList.remove("hidden");
}


/* -------------------
CLICK EVENTS
------------------- */

document.addEventListener("click", e => {


/* ADD SYSTEM TEMPLATE */

if(e.target.closest(".system-add")){

    const wrapper = e.target.closest(".system-icon-wrapper");
    const id = wrapper.dataset.id;

    if(activePopover){
        activePopover.dispose();
        activePopover = null;
    }

    fetch(`/templates/system/${id}/add/`,{
        method:"POST",
        headers:{
            "X-CSRFToken":csrftoken,
            "X-Requested-With":"XMLHttpRequest"
        }
    })
    .then(r=>r.json())
    .then(data=>{

        if(data.id){
            createTemplateCard(data);
            wrapper.remove();
            if(systemPanel.children.length === 0){
                systemPanelEl.closest(".system-panel-wrapper").classList.add("hidden");
            }
        }

    });

}


/* DELETE TEMPLATE */

if(e.target.closest(".delete-template")){

    const card = e.target.closest(".template-card");
    const id = card.dataset.id;

    fetch(`/templates/${id}/delete/`,{
        method:"POST",
        headers:{
            "X-CSRFToken":csrftoken,
            "X-Requested-With":"XMLHttpRequest"
        }
    })
    .then(r=>r.json())
    .then(data=>{

        if(data.status==="ok"){

            if(data.system_id){
                createSystemIcon({
                    system_id:data.system_id,
                    title:card.querySelector(".template-title").textContent,
                    description:card.querySelector(".template-description").textContent,
                    icon:card.querySelector(".template-icon")?.src,
                    amount:"?",
                    period:"?",
                    schedule:"?"
                });
            }

            card.remove();

        }

    });

}


/* EDIT TEMPLATE */

if(e.target.closest(".edit-template")){

    const card = e.target.closest(".template-card");
    window.location.href = `/templates/${card.dataset.id}/edit/`;

}

});


/* -------------------
ADD ALL
------------------- */

document.querySelector(".system-show-all")?.addEventListener("click", () => {

    if(activePopover){
        activePopover.dispose();
        activePopover = null;
    }

    fetch("/templates/system/add_all/",{
        method:"POST",
        headers:{
            "X-CSRFToken":csrftoken,
            "X-Requested-With":"XMLHttpRequest"
        }
    })
    .then(r=>r.json())
    .then(data=>{

        if(data.added){

            data.added.forEach(t=>{

                createTemplateCard(t);

                const icon = document.querySelector(
                    `.system-icon-wrapper[data-id="${t.system_id}"]`
                );

                if(icon){
                    icon.remove();
                }

            });

        }

    });

});


/* -------------------
SEARCH (debounce)
------------------- */

let searchTimeout;

searchInput?.addEventListener("input", () => {

    clearTimeout(searchTimeout);

    searchTimeout = setTimeout(() => {

        currentQuery = searchInput.value;
        currentPage = 1;
        hasNext = true;

        loadTemplates({ reset: true });

    }, 300);

});

window.addEventListener("scroll", () => {

    if(!hasNext || isLoading) return;

    const scrollBottom = window.innerHeight + window.scrollY;
    const pageHeight = document.body.offsetHeight;

    if(scrollBottom > pageHeight - 200){
        loadTemplates();
    }

});

/* -------------------
INIT LOAD
------------------- */

loadTemplates({ reset: true });
initSystemPanel();

});