/**
 * js/ui/views/settings.view.js
 */
export class SettingsView {
  constructor(notificationService) {
    this.notifier = notificationService;
    this.elements = {
      form: document.getElementById("unit-configuration-form"),
      minUnits: document.getElementById("min-units"),
      maxUnits: document.getElementById("max-units"),
      saveBtn: document.getElementById("save-unit-settings-btn"),
    };
  }

  fillForm(settings) {
    if (this.elements.minUnits)
      this.elements.minUnits.value = settings.min_units || "";
    if (this.elements.maxUnits)
      this.elements.maxUnits.value = settings.max_units || "";
  }

  setSubmitting(isSubmitting) {
    const btn = this.elements.saveBtn;
    if (!btn) return;

    if (isSubmitting) {
      btn.dataset.originalText = btn.textContent;
      btn.disabled = true;
      btn.textContent = "در حال ذخیره...";
    } else {
      btn.disabled = false;
      if (btn.dataset.originalText) btn.textContent = btn.dataset.originalText;
    }
  }

  bindSubmit(handler) {
    if (this.elements.form) {
      this.elements.form.addEventListener("submit", (e) => {
        e.preventDefault();
        const data = {
          min_units: parseInt(this.elements.minUnits.value),
          max_units: parseInt(this.elements.maxUnits.value),
        };
        handler(data);
      });
    }
  }
}
