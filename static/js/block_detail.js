document.addEventListener("DOMContentLoaded", function () {

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie) {
            const cookies = document.cookie.split(";");
            for (let c of cookies) {
                c = c.trim();
                if (c.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(
                        c.substring(name.length + 1)
                    );
                    break;
                }
            }
        }
        return cookieValue;
    }

    document.querySelectorAll(".encrypted-wrapper").forEach(function (wrapper) {

        const lockBtn = wrapper.querySelector(".lock-toggle");
        const placeholder = wrapper.querySelector(".encrypted-placeholder");
        const passwordField = wrapper.querySelector(".password-field");
        const passwordInput = wrapper.querySelector(".password-input");
        const toggleVisibility = wrapper.querySelector(".toggle-visibility");
        const decryptBtn = wrapper.querySelector(".decrypt-btn");
        const encryptedText = wrapper.querySelector(".encrypted-text");

        let isDecrypted = false;

        // 🔒 Основной переключатель
        lockBtn.addEventListener("click", function () {

            // ЕСЛИ текст расшифрован — сброс
            if (isDecrypted) {

                encryptedText.textContent = "";
                encryptedText.classList.add("d-none");

                placeholder.classList.remove("d-none");

                isDecrypted = false;
            }

            // Переключение видимости полей
            const isHidden = passwordField.classList.contains("d-none");

            if (isHidden) {

                passwordField.classList.remove("d-none");
                decryptBtn.classList.remove("d-none");
                placeholder.classList.add("d-none");

            } else {

                passwordField.classList.add("d-none");
                decryptBtn.classList.add("d-none");

                if (!isDecrypted) {
                    placeholder.classList.remove("d-none");
                }
            }

        });

        // 👁 показать пароль
        if (toggleVisibility) {
            toggleVisibility.addEventListener("click", function () {
                passwordInput.type =
                    passwordInput.type === "password"
                        ? "text"
                        : "password";
            });
        }

        // 🔓 Получить расшифровку
        decryptBtn.addEventListener("click", async function () {

            const password = passwordInput.value;

            if (!password) return;

            const response = await fetch("/decrypt-task/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({
                    task_id: wrapper.dataset.taskId,
                    password: password
                })
            });

            const data = await response.json();

            if (data.status === "ok") {

                encryptedText.textContent = data.description;
                encryptedText.classList.remove("d-none");

                passwordField.classList.add("d-none");
                decryptBtn.classList.add("d-none");
                placeholder.classList.add("d-none");

                isDecrypted = true;

            } else {
                alert("Неверный пароль");
            }

        });

    });

});