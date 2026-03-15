/* ----------------
CSRF
---------------- */

function getCookie(name){

let cookieValue=null;

if(document.cookie){

const cookies=document.cookie.split(";");

for(let cookie of cookies){

cookie=cookie.trim();

if(cookie.startsWith(name+"=")){

cookieValue=decodeURIComponent(cookie.substring(name.length+1));

break;

}

}

}

return cookieValue;

}

const csrftoken=getCookie("csrftoken");


/* ----------------
EDIT GROUP
---------------- */

document.querySelectorAll(".edit-group").forEach(btn=>{

btn.onclick=()=>{

const id=btn.dataset.id;

window.location.href=`/group-templates/${id}/edit/`;

};

});


/* ----------------
DELETE GROUP
---------------- */

document.querySelectorAll(".delete-group").forEach(btn=>{

btn.onclick=async()=>{

if(!confirm("Удалить группу?")) return;

const id=btn.dataset.id;

const card=btn.closest(".group-card");

const response=await fetch(`/group-templates/${id}/delete/`,{

method:"POST",

headers:{
"X-CSRFToken":csrftoken
}

});

if(response.ok){

card.remove();

}else{

alert("Ошибка удаления");

}

};

});


/* ----------------
TOOLTIP
---------------- */

const tooltip=document.getElementById("task-tooltip");

const tooltipTitle=document.getElementById("tooltip-title");
const tooltipDescription=document.getElementById("tooltip-description");
const tooltipAmount=document.getElementById("tooltip-amount");
const tooltipPeriod=document.getElementById("tooltip-period");
const tooltipSchedule=document.getElementById("tooltip-schedule");
const tooltipIcon=document.getElementById("tooltip-icon");


document.querySelectorAll(".tooltip-task").forEach(icon=>{


icon.addEventListener("mouseenter",()=>{

tooltip.style.display="block";

tooltipTitle.textContent=icon.dataset.title;

tooltipDescription.textContent=icon.dataset.description;

tooltipAmount.textContent=icon.dataset.amount;

tooltipPeriod.textContent=icon.dataset.period;

tooltipSchedule.textContent=icon.dataset.schedule;

if(icon.dataset.icon){

tooltipIcon.src=icon.dataset.icon;

tooltipIcon.style.display="block";

}else{

tooltipIcon.style.display="none";

}

});


icon.addEventListener("mousemove",(e)=>{

tooltip.style.left=(e.clientX+18)+"px";

tooltip.style.top=(e.clientY+18)+"px";

});


icon.addEventListener("mouseleave",()=>{

tooltip.style.display="none";

});

});