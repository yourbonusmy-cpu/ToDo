document.addEventListener("DOMContentLoaded", () => {

  function csrf() {
    return document.cookie
      .split(";")
      .find((c) => c.trim().startsWith("csrftoken="))
      ?.split("=")[1];
  }

  // ======================
  // TOGGLE PASSWORD (глаз)
  // ======================
  document.querySelectorAll(".toggle-password").forEach(btn => {
    btn.addEventListener("click", () => {
      const input = btn.previousElementSibling;
      const icon = btn.querySelector("i");

      if (input.type === "password") {
        input.type = "text";
        icon.classList.remove("bi-eye");
        icon.classList.add("bi-eye-slash");
      } else {
        input.type = "password";
        icon.classList.remove("bi-eye-slash");
        icon.classList.add("bi-eye");
      }
    });
  });

  // ======================
  // CHANGE PASSWORD
  // ======================
  const form = document.getElementById("changePasswordForm");

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const current = document.getElementById("currentPassword").value;
      const next = document.getElementById("newPassword").value;
      const confirm = document.getElementById("confirmPassword").value;
      const error = document.getElementById("changePasswordError");

      error.classList.add("d-none");

      // проверка совпадения паролей
      if (next !== confirm) {
        error.textContent = "Пароли не совпадают";
        error.classList.remove("d-none");
        return;
      }

      try {
        const res = await fetch("/profile/change-password/", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrf(),
          },
          body: `current=${encodeURIComponent(current)}&new=${encodeURIComponent(next)}`,
        });

        const data = await res.json();

        if (data.success) {
          // очищаем форму
          form.reset();

          // закрываем модалку
          const modalEl = document.getElementById("changePasswordModal");
          const modal = bootstrap.Modal.getInstance(modalEl);
          modal.hide();

        } else {
          error.textContent = data.error || "Ошибка";
          error.classList.remove("d-none");
        }

      } catch (err) {
        error.textContent = "Ошибка сети";
        error.classList.remove("d-none");
      }
    });
  }

  // ======================
  // DELETE ACCOUNT
  // ======================
  const del = document.getElementById("deleteAccountForm");

  if (del) {
    del.addEventListener("submit", async (e) => {
      e.preventDefault();

      const pass = document.getElementById("deleteAccountPassword").value;
      const error = document.getElementById("deleteAccountError");

      error.classList.add("d-none");

      try {
        const res = await fetch("/profile/delete/", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrf(),
          },
          body: "password=" + encodeURIComponent(pass),
        });

        const data = await res.json();

        if (data.success) {
          window.location = "/";
        } else {
          error.textContent = data.error;
          error.classList.remove("d-none");
        }

      } catch (err) {
        error.textContent = "Ошибка сети";
        error.classList.remove("d-none");
      }
    });
  }

});