window.PinModal = (function () {
  let modal, dots, buttons, errorBox;
  let pin = "";
  let resolveFn;

  function init() {
    modal = new bootstrap.Modal(document.getElementById("pinModal"));
    dots = document.querySelectorAll("#pinModal .pin-dot");
    buttons = document.querySelectorAll("#pinModal .pin-btn");
    errorBox = document.getElementById("pinError");

    buttons.forEach((btn) => {
      btn.addEventListener("click", handleClick);
    });
  }

  function open(title = "Введите PIN") {
    document.getElementById("pinTitle").innerText = title;

    pin = "";
    updateDots();
    errorBox.innerText = "";

    modal.show();

    return new Promise((resolve) => {
      resolveFn = resolve;
    });
  }

  function handleClick(e) {
    const btn = e.currentTarget;

    if (btn.dataset.num && pin.length < 4) {
      pin += btn.dataset.num;
      updateDots();
    }

    if (btn.classList.contains("pin-del")) {
      pin = pin.slice(0, -1);
      updateDots();
    }

    if (btn.classList.contains("pin-ok") || pin.length === 4) {
      if (pin.length !== 4) {
        showError("Введите 4 цифры");
        return;
      }

      resolveFn(pin);
      modal.hide();
    }
  }

  function updateDots() {
    dots.forEach((d, i) => {
      d.classList.toggle("active", i < pin.length);
    });
  }

  function showError(msg) {
    errorBox.innerText = msg;
  }

  return {
    init,
    open,
    showError,
  };
})();
