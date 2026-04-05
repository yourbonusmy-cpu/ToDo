document.addEventListener("DOMContentLoaded", () => {

    const modal = document.getElementById("pinActionModal");
    if (!modal) return;

    const input = document.getElementById("pinInput");
    const btn = document.getElementById("pinSubmitBtn");
    const error = document.getElementById("pinError");

    let action = null;

    function csrf() {
        return document.cookie.split(';')
            .find(c => c.trim().startsWith('csrftoken='))
            ?.split('=')[1];
    }

    modal.addEventListener("show.bs.modal", e => {
        action = e.relatedTarget?.dataset.action;

        input.value = "";
        error.classList.add("d-none");

        if (action === "toggle-pin") {
            document.getElementById("pinModalTitle").innerText = "Введите PIN";
        }

        if (action === "change-pin") {
            document.getElementById("pinModalTitle").innerText = "Новый PIN";
        }
    });

    btn.addEventListener("click", async () => {

        const pin = input.value;

        if (!/^\d{4}$/.test(pin)) return;

        let url = "/toggle-pin/";

        if (action === "change-pin") {
            url = "/toggle-pin/"; // можно сделать отдельный endpoint
        }

        const res = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": csrf()
            },
            body: "pin=" + pin
        });

        const data = await res.json();

        if (data.success) {
            location.reload();
        } else {
            error.textContent = data.error || "Ошибка";
            error.classList.remove("d-none");
        }
    });

});