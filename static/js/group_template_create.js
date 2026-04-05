const selectedContainer = document.getElementById("selected-tasks");

const groupTitle = document.getElementById("group-title");
const groupDescription = document.getElementById("group-description");

const selected = [];


/* --------------------------
CSRF
--------------------------- */

function getCookie(name){

    let cookieValue = null;

    if(document.cookie){

        const cookies = document.cookie.split(";");

        for(let cookie of cookies){

            cookie = cookie.trim();

            if(cookie.startsWith(name + "=")){

                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );

                break;

            }

        }

    }

    return cookieValue;
}

const csrftoken = getCookie("csrftoken");


/* --------------------------
ADD TASK
--------------------------- */

function addTask(taskData){

    const id = taskData.id.toString();

    if(selected.includes(id)) return;

    selected.push(id);

    const el = document.createElement("div");

    el.className = "selected-task position-relative";
    el.dataset.id = id;

    el.innerHTML = `

        <div class="border rounded bg-light d-flex align-items-center justify-content-center w-100 h-100">

            ${taskData.icon ? `<img src="${taskData.icon}" width="48" height="48">` : ""}

        </div>

        <button
        class="btn btn-danger btn-sm position-absolute top-0 start-100 translate-middle rounded-circle remove-task"
        >
        ×
        </button>

    `;

    el.querySelector(".remove-task").onclick = (e)=>{

        e.stopPropagation();

        removeTask(id);

    };

    selectedContainer.appendChild(el);

}


/* --------------------------
REMOVE TASK
--------------------------- */

function removeTask(id){

    const index = selected.indexOf(id);

    if(index > -1){

        selected.splice(index,1);

    }

    const el = selectedContainer.querySelector(`[data-id="${id}"]`);

    if(el) el.remove();

}


/* --------------------------
TASK PICKER CLICK
--------------------------- */

document.querySelectorAll(".task-picker .task-icon").forEach(icon=>{

    icon.addEventListener("click", ()=>{

        const taskData = {

            id: icon.dataset.id,
            title: icon.dataset.title,
            icon: icon.querySelector("img") ? icon.querySelector("img").src : ""

        };

        addTask(taskData);

    });

});
const taskList = document.querySelector(".task-picker-list");

taskList.addEventListener("wheel", (e) => {

    if (e.deltaY === 0) return;

    e.preventDefault();

    taskList.scrollLeft += e.deltaY;

});


/* --------------------------
SORTABLE
--------------------------- */

new Sortable(selectedContainer,{

    animation:150,

    onEnd(){

        const ids = Array.from(
            selectedContainer.children
        ).map(el=>el.dataset.id);

        selected.length = 0;

        ids.forEach(id=>selected.push(id));

    }

});


/* --------------------------
CLEAR GROUP
--------------------------- */

document.getElementById("clear-group-btn").onclick = ()=>{

    selected.length = 0;

    selectedContainer.innerHTML = "";

};


/* --------------------------
SAVE GROUP
--------------------------- */

document.getElementById("save-group-btn").onclick = async ()=>{

    if(!groupTitle.value.trim()){

        alert("Введите название группы");

        return;

    }

    const formData = new FormData();

    formData.append("title", groupTitle.value);

    formData.append("description", groupDescription.value);

    formData.append("tasks", JSON.stringify(selected));

    formData.append("csrfmiddlewaretoken", csrftoken);

    const response = await fetch(

        window.location.href,
        {
            method:"POST",
            body:formData
        }

    );

    if(response.redirected){

        window.location.href = response.url;

    }else{

        alert("Ошибка сохранения");

    }

};


/* --------------------------
LOAD GROUP DATA (EDIT MODE)
--------------------------- */

if(window.groupData){

    groupTitle.value = window.groupData.title || "";

    groupDescription.value = window.groupData.description || "";

    window.groupData.tasks.forEach(task=>{

        addTask(task);

    });

}

/* --------------------------
TASK SEARCH
--------------------------- */

const searchInput = document.getElementById("task-search-input");

if(searchInput){

    const icons = document.querySelectorAll(".task-picker .task-icon");

    searchInput.addEventListener("input", ()=>{

        const query = searchInput.value.toLowerCase().trim();

        icons.forEach(icon=>{

            const title = icon.dataset.title || "";

            if(title.includes(query)){

                icon.style.display = "";

            }else{

                icon.style.display = "none";

            }

        });

    });

}