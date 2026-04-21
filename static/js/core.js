document.addEventListener("DOMContentLoaded", () => {
  // -------------------------------
  // CSRF
  // -------------------------------
  function getCSRF() {
    const name = "csrftoken=";
    const cookies = document.cookie.split(";");
    for (let c of cookies) {
      c = c.trim();
      if (c.startsWith(name)) return c.substring(name.length);
    }
    return "";
  }

  // -------------------------------
  // PIN LOCK (экран блокировки)
  // -------------------------------
  const pinScreen = document.getElementById("pin-lock-screen");
  const appWrapper = document.getElementById("app-wrapper");

  const lockTimeoutMs = 5 * 60 * 1000;
  let idleTimer;

  function showPinScreen() {
    if (!pinScreen) return;
    appWrapper.style.display = "none";
    pinScreen.style.display = "flex";
  }

  function hidePinScreen() {
    if (!pinScreen) return;
    appWrapper.style.display = "block";
    pinScreen.style.display = "none";
  }

  function lockNow() {
      fetch("/lock-pin/", {
        method: "POST",
        headers: { "X-CSRFToken": getCSRF() },
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.success && typeof window.openUnlockModal === "function") {
              window.openUnlockModal();
            }
        });
    }

  // кнопка lock
  document.querySelectorAll(".lock-btn").forEach((btn) => {
    btn.addEventListener("click", lockNow);
  });

  // если PIN выключен → убираем кнопку
  if (!window.PIN_ENABLED) {
    document.querySelectorAll(".lock-btn").forEach((btn) => btn.remove());
  }

  // -------------------------------
  // LOGOUT из lock screen
  // -------------------------------
  const pinLogoutBtn = document.getElementById("pin-logout-btn");

  if (pinLogoutBtn) {
    pinLogoutBtn.addEventListener("click", () => {
      fetch("/logout/", {
        method: "POST",
        headers: { "X-CSRFToken": getCSRF() },
      }).then(() => (window.location.href = "/"));
    });
  }

  // -------------------------------
  // IDLE TIMER
  // -------------------------------
  function startIdleTimer() {
    clearTimeout(idleTimer);
    idleTimer = setTimeout(() => lockNow(), lockTimeoutMs);
  }

  ["mousemove", "keydown", "click", "scroll"].forEach((ev) => {
    document.addEventListener(ev, () => {
      if (!pinScreen || pinScreen.style.display !== "flex") {
        startIdleTimer();
      }
    });
  });

  startIdleTimer();

  // -------------------------------
  // AUTH (LOGIN / REGISTER)
  // -------------------------------
  function showErrors(container, errors) {
    container.innerHTML = "";

    for (let key in errors) {
      const messages = Array.isArray(errors[key]) ? errors[key] : [errors[key]];

      messages.forEach((msg) => {
        const div = document.createElement("div");
        div.className = "auth-error";
        div.innerText = msg;
        container.appendChild(div);
      });
    }
  }

  async function handleAuthForm(form) {
    const url = form.action;
    const formData = new FormData(form);

    const errorBox = form.querySelector(".auth-errors");
    if (errorBox) errorBox.innerHTML = "";

    const response = await fetch(url, {
      method: "POST",
      body: formData,
      headers: { "X-Requested-With": "XMLHttpRequest" },
    });

    const data = await response.json();

    if (data.success) {
      if (!data.access) {
        console.error("JWT не пришёл с сервера");
        return;
      }
      // 🔥 СОХРАНЯЕМ JWT
      if (data.access && data.refresh) {
        localStorage.setItem("access_token", data.access);
        localStorage.setItem("refresh_token", data.refresh);
      }

      const modal = document.getElementById("authModal");
      if (modal) bootstrap.Modal.getInstance(modal)?.hide();

      location.reload();
    } else {
      if (errorBox) showErrors(errorBox, data.errors);
    }
  }

  const tabs = document.querySelectorAll(".auth-tab");
  const forms = document.querySelectorAll(".auth-form");

  forms.forEach((form) => {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      handleAuthForm(form);
    });
  });

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const target = tab.dataset.tab;

      tabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");

      forms.forEach((f) => f.classList.remove("active"));

      const targetForm = document.getElementById(target + "Form");
      if (targetForm) targetForm.classList.add("active");
    });
  });

  const authModal = document.getElementById("authModal");

  if (authModal) {
    authModal.addEventListener("show.bs.modal", (event) => {
      const button = event.relatedTarget;
      const tab = button ? button.getAttribute("data-auth-tab") : "login";

      tabs.forEach((t) => t.classList.remove("active"));
      forms.forEach((f) => f.classList.remove("active"));

      const activeTab = document.querySelector(`[data-tab="${tab}"]`);
      const activeForm = document.getElementById(tab + "Form");

      if (activeTab) activeTab.classList.add("active");
      if (activeForm) activeForm.classList.add("active");
    });
  }

  // -------------------------------
  // UNIVERSAL TOGGLE PASSWORD
  // -------------------------------
  document.querySelectorAll(".toggle-password").forEach((btn) => {
      btn.addEventListener("click", () => {
        const wrapper = btn.closest(".position-relative");
        if (!wrapper) return;

        const input = wrapper.querySelector("input");
        if (!input) return;

        if (input.type === "password") {
          input.type = "text";
          btn.classList.remove("bi-eye");
          btn.classList.add("bi-eye-slash");
        } else {
          input.type = "password";
          btn.classList.remove("bi-eye-slash");
          btn.classList.add("bi-eye");
        }
      });
    });
});
