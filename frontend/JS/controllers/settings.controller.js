/**
 * js/controllers/settings.controller.js
 */
export class SettingsController {
  constructor(apiService, validator, view) {
    this.api = apiService;
    this.validator = validator;
    this.view = view;

    this.state = {
      unitConfiguration: { min_units: null, max_units: null },
    };
  }

  async init() {
    this._bindEvents();
    await this.loadSettings();
  }

  async loadSettings() {
    try {
      const config = await this.api.getUnitConfiguration();

      this.state.unitConfiguration = config || { min_units: 12, max_units: 20 };

      this.view.fillForm(this.state.unitConfiguration);
    } catch (error) {
      console.error(error);
      this.view.notifier.showError("خطا در بارگیری تنظیمات.");
    }
  }

  _bindEvents() {
    this.view.bindSubmit((formData) =>
      this._handleSaveUnitConfiguration(formData)
    );
  }

  async _handleSaveUnitConfiguration(formData) {
    this.view.notifier.clearValidationErrors(this.view.elements.form);

    const validationResult = this.validator.validateUnitConfiguration(formData);

    if (!validationResult.isValid) {
      this.view.notifier.showValidationErrors(validationResult.errors);
      return;
    }

    this.view.setSubmitting(true);

    try {
      const savedConfig = await this.api.saveUnitConfiguration(formData);

      this.state.unitConfiguration = savedConfig;
      this.view.fillForm(savedConfig);
      this.view.notifier.showSuccess("تنظیمات واحد با موفقیت ذخیره شد.");
    } catch (error) {
      console.error(error);
      this.view.notifier.showError(`خطا در ذخیره تنظیمات: ${error.message}`);
    } finally {
      this.view.setSubmitting(false);
    }
  }
}
