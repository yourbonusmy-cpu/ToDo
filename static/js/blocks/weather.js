document.addEventListener("DOMContentLoaded", () => {
  const select = document.querySelector("select[name='city']");
  if (!select) return;

  select.addEventListener("change", () => {
    select.form.submit();
  });
});
