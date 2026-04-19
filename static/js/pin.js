document.addEventListener("DOMContentLoaded", () => {

  const modalEl = document.getElementById("pinModal");
  if (!modalEl) return;

 const modal = bootstrap.Modal.getOrCreateInstance(modalEl);

  const dots = modalEl.querySelectorAll(".pin-dot");
  const error = modalEl.querySelector("#pinError");
  const title = modalEl.querySelector("#pinModalTitle");

  const switchEl = document.getElementById("pinSwitch");

  let mode = null;
  let step = 1;
  let pin = "";
  let tempPin = null;

  function getCSRF() {
    return document.cookie
      .split(";")
      .find((c) => c.trim().startsWith("csrftoken="))
      ?.split("=")[1];
  }

  function reset() {
    pin = "";
    tempPin = null;
    step = 1;
    error.textContent = "";
    updateDots();
  }

  function updateDots() {
    dots.forEach((d, i) => {
      d.classList.toggle("active", i < pin.length);
    });
  }

  function openModal(m) {
    mode = m;
    reset();

    if (mode === "toggle-on") {
      title.innerText = "Создайте PIN";
    }

    if (mode === "toggle-off") {
      title.innerText = "Введите текущий PIN";
    }

    if (mode === "change") {
      title.innerText = "Введите текущий PIN";
    }

    modal.show();
  }

  // =========================
  // SWITCH (фикс UX)
  // =========================

    if (switchEl) {
      switchEl.addEventListener("click", (e) => {
        e.preventDefault();

        // 🔥 берём ИСТИННОЕ состояние с сервера
        const isEnabled = window.PIN_ENABLED;

        if (isEnabled) {
          openModal("toggle-off"); // выключение → нужен текущий PIN
        } else {
          openModal("toggle-on");  // включение → новый PIN
        }
      });
    }

  // =========================
  // CHANGE PIN
  // =========================
  document.querySelector('[data-action="change-pin"]')
    ?.addEventListener("click", () => openModal("change"));

  // =========================
  // KEYPAD (изоляция от core.js)
  // =========================
  modalEl.querySelectorAll(".pin-btn").forEach(btn => {
    btn.addEventListener("click", () => {

      if (btn.classList.contains("pin-del")) {
        pin = pin.slice(0, -1);
        updateDots();
        return;
      }

      if (btn.dataset.num && pin.length < 4) {
        pin += btn.dataset.num;
        updateDots();
        return;
      }

      if (btn.classList.contains("pin-ok") && pin.length === 4) {
        handleStep();
      }
    });
  });

  // =========================
  // MAIN LOGIC
  // =========================
  async function handleStep() {

    // ---------------------
    // ENABLE PIN
    // ---------------------
    if (mode === "toggle-on") {

      if (step === 1) {
        tempPin = pin;
        pin = "";
        step = 2;
        title.innerText = "Повторите PIN";
        updateDots();
        return;
      }

      if (step === 2) {
        if (pin !== tempPin) {
          error.textContent = "PIN не совпадает";
          pin = "";
          updateDots();
          return;
        }

        await fetch("/profile/set-pin/", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCSRF(),
          },
          body: "pin=" + pin,
        });

        switchEl.checked = true;
        modal.hide();
      }
    }

    // ---------------------
    // DISABLE PIN
    // ---------------------
    if (mode === "toggle-off") {

      const res = await fetch("/profile/disable-pin/", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": getCSRF(),
        },
        body: "pin=" + pin,
      });

      const data = await res.json();

      if (!data.success) {
        error.textContent = "Неверный PIN";
        pin = "";
        updateDots();
        return;
      }

      switchEl.checked = false;
      modal.hide();
    }

    // ---------------------
    // CHANGE PIN
    // ---------------------
    if (mode === "change") {

      // шаг 1 — проверка текущего
      if (step === 1) {
        const res = await fetch("/profile/verify-pin/", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCSRF(),
          },
          body: "pin=" + pin,
        });

        const data = await res.json();

        if (!data.success) {
          error.textContent = "Неверный PIN";
          pin = "";
          updateDots();
          return;
        }

        step = 2;
        pin = "";
        title.innerText = "Новый PIN";
        updateDots();
        return;
      }

      // шаг 2 — ввод нового
      if (step === 2) {
        tempPin = pin;
        pin = "";
        step = 3;
        title.innerText = "Повторите новый PIN";
        updateDots();
        return;
      }

      // шаг 3 — подтверждение
      if (step === 3) {
        if (pin !== tempPin) {
          error.textContent = "PIN не совпадает";
          pin = "";
          updateDots();
          return;
        }

        await fetch("/profile/set-pin/", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCSRF(),
          },
          body: "pin=" + pin,
        });

        modal.hide();
      }
    }
  }
});
window.openUnlockModal = function () {
  const modalEl = document.getElementById("pinModal");
  if (!modalEl) return;

  const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
  modal.show();
};