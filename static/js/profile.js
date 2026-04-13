document.addEventListener("DOMContentLoaded", () => {
  PinModal.init();

  const pinToggle = document.getElementById("pinToggle");
  const changePasswordBtn = document.getElementById("changePasswordBtn");
  const deleteAccountBtn = document.getElementById("deleteAccountBtn");

  // -----------------------------
  // 🔢 PIN TOGGLE
  // -----------------------------
  if (pinToggle) {
    pinToggle.addEventListener("change", async function () {
      // 🔴 отключение
      if (!this.checked) {
        const pin = await PinModal.open("Введите текущий PIN");

        const res = await fetch("/profile/toggle-pin/", {
          method: "POST",
          headers: headers(),
          body: form({ pin }),
        });

        const data = await res.json();

        if (!data.success) {
          PinModal.showError(data.error);
          this.checked = true;
        }
      } else {
        // 🟢 включение
        const pin = await PinModal.open("Создайте PIN");

        const res = await fetch("/profile/toggle-pin/", {
          method: "POST",
          headers: headers(),
          body: form({ pin }),
        });

        const data = await res.json();

        if (!data.success) {
          PinModal.showError(data.error);
          this.checked = false;
        }
      }
    });
  }

  // -----------------------------
  // 🔁 СМЕНА PIN
  // -----------------------------
  const changePinBtn = document.getElementById("changePinBtn");

  if (changePinBtn) {
    changePinBtn.addEventListener("click", async () => {
      const oldPin = await PinModal.open("Введите старый PIN");

      const newPin = await PinModal.open("Введите новый PIN");

      const res = await fetch("/profile/toggle-pin/", {
        method: "POST",
        headers: headers(),
        body: form({ pin: oldPin }), // сначала проверка
      });

      const data = await res.json();

      if (!data.success) {
        PinModal.showError("Старый PIN неверный");
        return;
      }

      // установить новый
      await fetch("/profile/toggle-pin/", {
        method: "POST",
        headers: headers(),
        body: form({ pin: newPin }),
      });

      alert("PIN обновлён");
    });
  }

  // -----------------------------
  // 🔐 СМЕНА ПАРОЛЯ
  // -----------------------------
  if (changePasswordBtn) {
    changePasswordBtn.addEventListener("click", async () => {
      const current = prompt("Текущий пароль");
      const newPass = prompt("Новый пароль");

      const res = await fetch("/profile/change-password/", {
        method: "POST",
        headers: headers(),
        body: form({
          current: current,
          new: newPass,
        }),
      });

      const data = await res.json();

      if (!data.success) {
        alert(data.error);
      } else {
        alert("Пароль изменён");
      }
    });
  }

  // -----------------------------
  // ❌ УДАЛЕНИЕ АККАУНТА
  // -----------------------------
  if (deleteAccountBtn) {
    deleteAccountBtn.addEventListener("click", async () => {
      const password = prompt("Введите пароль для удаления");

      const res = await fetch("/profile/delete/", {
        method: "POST",
        headers: headers(),
        body: form({ password }),
      });

      const data = await res.json();

      if (!data.success) {
        alert(data.error);
      } else {
        window.location.href = "/";
      }
    });
  }

  // -----------------------------
  // UTILS
  // -----------------------------
  function getCSRF() {
    return document.cookie
      .split(";")
      .map((c) => c.trim())
      .find((c) => c.startsWith("csrftoken="))
      ?.split("=")[1];
  }

  function headers() {
    return {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-CSRFToken": getCSRF(),
    };
  }

  function form(data) {
    return new URLSearchParams(data).toString();
  }
});
