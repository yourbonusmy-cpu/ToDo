document.addEventListener("DOMContentLoaded", () => {

const systemPanel = document.querySelector(".system-scroll");
const templatesGrid = document.querySelector(".templates-grid");
const tooltip = document.getElementById("system-tooltip");

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



/* -------------------
TOOLTIP
------------------- */

function showTooltip(wrapper){

    tooltip.innerHTML = `
        <h6>${wrapper.dataset.title}</h6>
        <p class="small text-muted">
            ${wrapper.dataset.description}
        </p>
        <div class="small text-muted">
            <div>Количество: ${wrapper.dataset.amount}</div>
            <div>Повторение: ${wrapper.dataset.period}</div>
            <div>Расписание: ${wrapper.dataset.schedule}</div>
        </div>
    `;

    const rect = wrapper.getBoundingClientRect();

    tooltip.style.top = rect.top + window.scrollY + "px";
    tooltip.style.left = rect.right + 10 + "px";

    tooltip.style.opacity = 1;
}

function hideTooltip(){
    tooltip.style.opacity = 0;
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

    <div class="card-body d-flex gap-3">

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
                ${t.description}
            </div>

        </div>

    </div>

    `;

    templatesGrid.appendChild(card);
}



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
}



/* -------------------
CLICK EVENTS
------------------- */

document.addEventListener("click", e => {


/* ADD SYSTEM TEMPLATE */

if(e.target.closest(".system-add")){

    const wrapper = e.target.closest(".system-icon-wrapper");

    const id = wrapper.dataset.id;

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
HOVER TOOLTIP
------------------- */

document.addEventListener("mouseover", e => {

    const wrapper = e.target.closest(".system-icon-wrapper");

    if(wrapper){
        showTooltip(wrapper);
    }

});

document.addEventListener("mouseout", e => {

    if(e.target.closest(".system-icon-wrapper")){
        hideTooltip();
    }

});



/* -------------------
ADD ALL
------------------- */

document.querySelector(".system-show-all")?.addEventListener("click", () => {

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

});