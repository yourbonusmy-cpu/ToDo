document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("id_icon");
    const image = document.getElementById("iconImage");
    const removeBtn = document.getElementById("removeIcon");

    fileInput?.addEventListener("change", () => {
        const file = fileInput.files[0];
        if(!file || !file.type.startsWith("image/")) return;
        image.src = URL.createObjectURL(file);
        removeBtn.classList.remove("hidden");
    });

    removeBtn?.addEventListener("click", e => {
        e.stopPropagation();
        fileInput.value = "";
        image.src = "{% static 'img/plus-square-dotted.svg' %}";
        removeBtn.classList.add("hidden");
    });


    const month = document.getElementById("id_fixed_month_of_year");
    const day = document.getElementById("id_fixed_day_of_month");

    month.addEventListener("change", () => {

        const days = {
            1:31,2:29,3:31,4:30,5:31,6:30,
            7:31,8:31,9:30,10:31,11:30,12:31
        };

        day.max = days[month.value] || 31;

    });

    // drag & drop
    const preview = image.parentElement;
    ['dragover','dragleave','drop'].forEach(eventName => {
        preview?.addEventListener(eventName, e => {
            e.preventDefault(); e.stopPropagation();
            if(eventName==='dragover') preview.classList.add("dragover");
            if(eventName==='dragleave'||eventName==='drop') preview.classList.remove("dragover");
            if(eventName==='drop'){
                const file = e.dataTransfer.files[0];
                if(!file || !file.type.startsWith("image/")) return;
                fileInput.files = e.dataTransfer.files;
                fileInput.dispatchEvent(new Event('change'));
            }
        });
    });

    const period = document.getElementById("id_period_type");
    const schedule = document.getElementById("id_schedule_type");

    const weekdayField = document.getElementById("weekdayField");
    const dayField = document.getElementById("dayField");
    const monthField = document.getElementById("monthField");
    const fixedFields = document.getElementById("fixedFields");

    function updateFields() {

        const periodValue = period.value;
        const scheduleValue = schedule.value;

        weekdayField.style.display = "none";
        dayField.style.display = "none";
        monthField.style.display = "none";
        fixedFields.style.display = "none";

        if (scheduleValue !== "fixed") {
            return;
        }

        fixedFields.style.display = "flex";

        if (periodValue === "week") {
            weekdayField.style.display = "block";
        }

        if (periodValue === "month") {
            dayField.style.display = "block";
        }

        if (periodValue === "year") {
            monthField.style.display = "block";
            dayField.style.display = "block";
        }

        if (periodValue === "day") {
            // ничего показывать не нужно
        }
    }
    period.addEventListener("change", updateFields);
    schedule.addEventListener("change", updateFields);

    updateFields();
});