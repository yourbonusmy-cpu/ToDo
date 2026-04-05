document.addEventListener("DOMContentLoaded", () => {

    function csrf() {
        return document.cookie.split(';')
            .find(c => c.trim().startsWith('csrftoken='))
            ?.split('=')[1];
    }

    // смена пароля
    const form = document.getElementById("changePasswordForm");

    if (form) {
        form.addEventListener("submit", async e => {
            e.preventDefault();

            const current = document.getElementById("currentPassword").value;
            const next = document.getElementById("newPassword").value;
            const error = document.getElementById("changePasswordError");

            const res = await fetch("/profile/change-password/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": csrf()
                },
                body: `current=${current}&new=${next}`
            });

            const data = await res.json();

            if (data.success) {
                location.reload();
            } else {
                error.textContent = data.error;
                error.classList.remove("d-none");
            }
        });
    }

    // удаление аккаунта
    const del = document.getElementById("deleteAccountForm");

    if (del) {
        del.addEventListener("submit", async e => {
            e.preventDefault();

            const pass = document.getElementById("deleteAccountPassword").value;
            const error = document.getElementById("deleteAccountError");

            const res = await fetch("/profile/delete-account/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": csrf()
                },
                body: "password=" + pass
            });

            const data = await res.json();

            if (data.success) {
                window.location = "/";
            } else {
                error.textContent = data.error;
                error.classList.remove("d-none");
            }
        });
    }

});