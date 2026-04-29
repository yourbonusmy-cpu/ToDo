document.addEventListener("DOMContentLoaded", () => {
  // -------------------------------
  // PIN LOCK
  // -------------------------------
  let pinValue = "";
  let pinAttempts = 0;
  let isSubmitting = false;
  const lockTimeoutMs = 5 * 60 * 1000; // 5 минут
  const lockCooldownMs = 30 * 1000; // 30 секунд после 3 ошибок
  let cooldown = false;

  const dots = document.querySelectorAll(".pin-dot");
  const pinScreen = document.getElementById("pin-lock-screen");
  const appWrapper = document.getElementById("app-wrapper");

  // Контейнер для сообщений об ошибках
  let pinErrorMsg = document.createElement("div");
  pinErrorMsg.style.color = "red";
  pinErrorMsg.style.fontSize = "0.9rem";
  pinErrorMsg.style.textAlign = "center";
  pinErrorMsg.style.marginTop = "5px";
  pinErrorMsg.style.minHeight = "1em";
  pinScreen.querySelector(".pin-container").appendChild(pinErrorMsg);

  function getCSRF() {
    const name = "csrftoken=";
    const cookies = document.cookie.split(";");
    for (let c of cookies) {
      c = c.trim();
      if (c.startsWith(name)) return c.substring(name.length);
    }
    return "";
  }

  function updateDots() {
    dots.forEach((d, i) => d.classList.toggle("active", i < pinValue.length));
  }

  function showPinScreen() {
    appWrapper.style.display = "none";
    pinScreen.style.display = "flex";
  }

  function hidePinScreen() {
    appWrapper.style.display = "block";
    pinScreen.style.display = "none";
  }

  // -------------------------------
  // SHOW ERROR
  // -------------------------------
  function showPinError(msg) {
    pinErrorMsg.textContent = msg;
    pinScreen.classList.add("shake");
    setTimeout(() => {
      pinScreen.classList.remove("shake");
      pinErrorMsg.textContent = "";
    }, 2000);
  }

  // -------------------------------
  // SUBMIT PIN
  // -------------------------------
  let cooldownTimeoutId = null;
  async function submitPin() {
    if (isSubmitting || cooldown) return;
    if (pinValue.length < 4) return;

    isSubmitting = true;

    const response = await fetch("/unlock-pin/", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCSRF(),
      },
      body: "pin=" + pinValue,
    });

    const data = await response.json();
    isSubmitting = false;

    if (data.success) {
      pinValue = "";
      updateDots();
      pinAttempts = 0;
      hidePinScreen();
      startIdleTimer();
    } else if (data.cooldown) {
      cooldown = true;
      showPinError(
        `Слишком много попыток! Попробовать через ${data.cooldown} сек.`,
      );
      setTimeout(() => {
        cooldown = false;
        pinAttempts = 0;
        pinErrorMsg.textContent = "";
      }, lockCooldownMs);
    } else {
      pinAttempts++;
      pinValue = "";
      updateDots();
      showPinError(`Неверный PIN (${pinAttempts}/3)`);

      if (pinAttempts >= 3) {
        cooldown = true;
        showPinError("3 неверные попытки! Подождите 30 секунд.");
        if (cooldownTimeoutId) clearTimeout(cooldownTimeoutId);
        setTimeout(() => {
          cooldown = false;
          pinAttempts = 0;
          pinErrorMsg.textContent = "";
        }, lockCooldownMs);
      }
    }
  }

  // -------------------------------
  // LOCK NOW
  // -------------------------------
  function lockNow() {
    fetch("/lock-pin/", {
      method: "POST",
      headers: { "X-CSRFToken": getCSRF() },
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) showPinScreen();
      });
  }

  document.querySelectorAll(".lock-btn").forEach((btn) => {
    btn.addEventListener("click", lockNow);
  });

  if (!window.PIN_ENABLED) {
    document.querySelectorAll(".lock-btn").forEach((btn) => btn.remove());
  }

  // -------------------------------
  // LOGOUT FROM PIN SCREEN
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
  // PIN PAD BUTTONS
  // -------------------------------
  document.querySelectorAll(".pin-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const num = btn.dataset.num;
      if (num && pinValue.length < 4) {
        pinValue += num;
        updateDots();
        if (pinValue.length === 4) submitPin();
      }
      if (btn.classList.contains("pin-del")) {
        pinValue = pinValue.slice(0, -1);
        updateDots();
      }
      if (btn.classList.contains("pin-ok")) submitPin();
    });
  });

  // -------------------------------
  // KEYBOARD INPUT
  // -------------------------------
  document.addEventListener("keydown", (e) => {
    if (pinScreen.style.display !== "flex") return;
    if (e.key >= "0" && e.key <= "9" && pinValue.length < 4) {
      pinValue += e.key;
      updateDots();
      if (pinValue.length === 4) submitPin();
    }
    if (e.key === "Backspace") {
      pinValue = pinValue.slice(0, -1);
      updateDots();
    }
    if (e.key === "Enter") submitPin();
  });

  // -------------------------------
  // IDLE TIMER
  // -------------------------------
  let idleTimer;
  function startIdleTimer() {
    clearTimeout(idleTimer);
    idleTimer = setTimeout(() => lockNow(), lockTimeoutMs);
  }

  ["mousemove", "keydown", "click", "scroll"].forEach((ev) => {
    document.addEventListener(ev, () => {
      if (pinScreen.style.display !== "flex") startIdleTimer();
    });
  });

  startIdleTimer();

  // -------------------------------
  // TOGGLE PASSWORD ICONS
  // -------------------------------
  document.querySelectorAll(".toggle-password").forEach((icon) => {
    icon.addEventListener("click", () => {
      const input = icon.previousElementSibling;
      if (!input) return;
      if (input.type === "password") {
        input.type = "text";
        icon.classList.replace("bi-eye", "bi-eye-slash");
      } else {
        input.type = "password";
        icon.classList.replace("bi-eye-slash", "bi-eye");
      }
    });
  });

  // -------------------------------
  // AUTH FORMS (LOGIN/REGISTER)
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
    errorBox.innerHTML = "";
    const response = await fetch(url, {
      method: "POST",
      body: formData,
      headers: { "X-Requested-With": "XMLHttpRequest" },
    });
    const data = await response.json();
    if (data.success) {
      bootstrap.Modal.getInstance(document.getElementById("authModal")).hide();
      location.reload();
    } else {
      showErrors(errorBox, data.errors);
    }
  }

  const tabs = document.querySelectorAll(".auth-tab");
  const forms = document.querySelectorAll(".auth-form");

  forms.forEach((form) =>
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      handleAuthForm(form);
    }),
  );

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const target = tab.dataset.tab;
      tabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      forms.forEach((f) => f.classList.remove("active"));
      document.getElementById(target + "Form").classList.add("active");
    });
  });

  const authModal = document.getElementById("authModal");
  if (authModal) {
    authModal.addEventListener("show.bs.modal", (event) => {
      const button = event.relatedTarget;
      const tab = button ? button.getAttribute("data-auth-tab") : "login";
      tabs.forEach((t) => t.classList.remove("active"));
      forms.forEach((f) => f.classList.remove("active"));
      document.querySelector(`[data-tab="${tab}"]`).classList.add("active");
      document.getElementById(tab + "Form").classList.add("active");
    });
  }
});
