/**
 * js/controllers/login.controller.js
 * Responsibility: Connects API, Auth, and View logic.
 * Orchestrates the login process and handles role-based redirection.
 */
export class LoginController {
  /**
   * @param {ApiService} apiService - Service for API communication.
   * @param {AuthService} authService - Service for authentication management.
   * @param {LoginValidator} validator - Utility for form validation.
   * @param {LoginView} view - The view component for the login page.
   */
  constructor(apiService, authService, validator, view) {
    this.api = apiService;
    this.auth = authService;
    this.validator = validator;
    this.view = view;
  }

  /**
   * Initializes the controller.
   * Sets up event listeners and checks initial authentication state.
   */
  init() {
    // Auth Guard: If already logged in, redirect to the appropriate dashboard
    if (this.auth.isAuthenticated()) {
      // Use the new service method to determine the correct dashboard URL based on role
      window.location.href = this.auth.getRedirectUrl();
      return;
    }

    // 1. Bind Form Submit
    // We bind the handleLogin method to 'this' controller instance to preserve context
    this.view.bindLogin(this.handleLogin.bind(this));

    // 2. Bind Real-time Validation (Blur/Input)
    // This allows the view to ask the validator for feedback as user types
    this.view.bindRealTimeValidation((fieldName, value) => {
      return this.validator.validateField(fieldName, value);
    });
  }

  /**
   * Handles the login form submission.
   * @param {Object} formData - The data from the form { username, password }.
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
      // Extract token and user object (assuming backend/mock returns { access_token, user: { role: ... } })
      const token = response.access_token || response.data?.token;
      const user = response.user || response.data?.user;

      // The original code checked for (token || response.success). We only proceed if we have both token and user object containing the role.
      if (token && user) {
        // Delegate storage logic (token and user data) to AuthService
        this.auth.login(token, user);

        // Show success message
        this.view.showSuccessMessage();

        // Redirect to the appropriate dashboard based on user role using AuthService
        setTimeout(() => {
          const redirectUrl = this.auth.getRedirectUrl();
          window.location.href = redirectUrl;
        }, 1000);
      } else {
        // Handle logical failure (e.g., credentials incorrect, but server returned 200 with error message)
        const msg =
          response.error?.message ||
          response.message ||
          "Login failed: Invalid credentials or incomplete data.";
        this.view.showGlobalError(msg);
      }
    } catch (error) {
      console.error("Login Controller Error:", error);
      // Handle network errors or exceptions thrown by ApiService
      const msg = error.message || "An unexpected network error occurred.";
      this.view.showGlobalError(msg);
    } finally {
      // 6. Reset Loading State (always run this)
      this.view.setLoading(false);
    }
  }
}
