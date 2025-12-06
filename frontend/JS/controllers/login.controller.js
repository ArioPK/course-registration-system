/**
 * js/controllers/login.controller.js
 * Responsibility: Connects API, Auth, and View logic.
 */
export class LoginController {
  constructor(apiService, authService, validator, view) {
    this.api = apiService;
    this.auth = authService;
    this.validator = validator;
    this.view = view;
  }

  init() {
    // Auth Guard: If already logged in, redirect to panel
    if (this.auth.isAuthenticated()) {
      window.location.href = "../panel/index.html";
      return;
    }

    // 1. Bind Form Submit
    // We bind the handleLogin method to 'this' controller instance
    this.view.bindLogin(this.handleLogin.bind(this));

    // 2. Bind Real-time Validation (Blur/Input)
    // This allows the view to ask the validator for feedback as user types
    this.view.bindRealTimeValidation((fieldName, value) => {
      return this.validator.validateField(fieldName, value);
    });
  }

  /**
   * Handles the login form submission.
   * @param {Object} formData - { username, password }
   */
  async handleLogin(formData) {
    // 1. Clear previous states (errors and styles)
    this.view.clearGlobalError();
    this.view.clearAllValidation();

    // 2. Full Form Validation
    const validation = this.validator.validate(formData);
    if (!validation.isValid) {
      // If invalid, show errors on specific fields
      this.view.showFieldErrors(validation.errors);
      return;
    }

    // 3. Set Loading State
    this.view.setLoading(true);

    try {
      // 4. Call API (supports both Mock and Real based on api.service.js config)
      const response = await this.api.login(
        formData.username,
        formData.password
      );

      // 5. Handle Success
      // Check for token in various response formats
      const token = response.access_token || response.data?.token;
      const user = response.user || response.data?.user;

      if (token || response.success) {
        // Store auth data
        if (token) sessionStorage.setItem("authToken", token);
        sessionStorage.setItem("isAdminLoggedIn", "true");

        if (user) sessionStorage.setItem("userData", JSON.stringify(user));

        // Show success and redirect
        this.view.showSuccessMessage();

        // Wait a bit for user to see success message
        setTimeout(() => {
          window.location.href = "../panel/index.html";
        }, 1000);
      } else {
        // Handle logical failure (e.g. success: false in response)
        const msg =
          response.error?.message || response.message || "خطا در ورود به سیستم";
        this.view.showGlobalError(msg);
      }
    } catch (error) {
      console.error("Login Controller Error:", error);
      // Handle network errors or exceptions thrown by ApiService
      const msg = error.message || "خطای غیرمنتظره رخ داد.";
      this.view.showGlobalError(msg);
    } finally {
      // 6. Reset Loading State (always run this)
      this.view.setLoading(false);
    }
  }
}
