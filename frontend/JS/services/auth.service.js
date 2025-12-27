/**
 * js/services/auth.service.js
 * Responsibility: Manages user authentication state, token storage, and logout functionality.
 * Acts as a centralized place for all auth-related logic.
 */

export class AuthService {
  constructor() {
    // Keys used in sessionStorage
    this.KEYS = {
      TOKEN: "authToken",
      USER_DATA: "userData", // Stores the full user object including role and id
    };

    // Redirect URLs for different user roles
    this.URLS = {
      LOGIN: "../Login/index.html",
      ADMIN_DASHBOARD: "../panel/index.html",
      STUDENT_DASHBOARD: "../student-panel/index.html", // URL for the Student Dashboard
      PROFESSOR_DASHBOARD: "../professor-panel/index.html", // URL for the Professor Dashboard
    };
  }

  /**
   * Stores user authentication details upon successful login.
   * @param {string} token - The JWT access token received from the API.
   * @param {Object} user - The user object containing role and other details.
   */
  login(token, user) {
    if (token) {
      sessionStorage.setItem(this.KEYS.TOKEN, token);
    }
    if (user) {
      sessionStorage.setItem(this.KEYS.USER_DATA, JSON.stringify(user));
    }
  }

  /**
   * Checks if the user is currently authenticated.
   * Determines status based on the presence of a valid token in storage.
   * @returns {boolean} True if a token exists, false otherwise.
   */
  isAuthenticated() {
    // Direct token check is more secure than relying on a manual 'isLoggedIn' flag
    return !!sessionStorage.getItem(this.KEYS.TOKEN);
  }

  /**
   * Retrieves the current access token.
   * @returns {string|null} The JWT token or null if not found.
   */
  getToken() {
    return sessionStorage.getItem(this.KEYS.TOKEN);
  }

  /**
   * Retrieves the stored user data.
   * @returns {Object|null} The user object or null if parsing fails.
   */
  getUserData() {
    const data = sessionStorage.getItem(this.KEYS.USER_DATA);
    try {
      return data ? JSON.parse(data) : null;
    } catch (e) {
      console.error("Error parsing user data:", e);
      return null;
    }
  }

  /**
   * Extracts the role from the stored user data.
   * Used for access control and routing decisions.
   * @returns {string|null} The user's role (e.g., 'admin', 'student', 'professor') or null.
   */
  getRole() {
    const user = this.getUserData();
    return user ? user.role : null;
  }

  /**
   * Determines the appropriate dashboard URL based on the user's role.
   * Centralizes routing logic to adhere to the Single Responsibility Principle (SRP).
   * @returns {string} The URL of the dashboard corresponding to the user's role.
   */
  getRedirectUrl() {
    const role = this.getRole();

    switch (role) {
      case "admin":
        return this.URLS.ADMIN_DASHBOARD;
      case "student":
        return this.URLS.STUDENT_DASHBOARD;
      case "professor":
        return this.URLS.PROFESSOR_DASHBOARD;
      default:
        // Fallback to login if role is unknown or user is not authenticated
        return this.URLS.LOGIN;
    }
  }

  /**
   * Enforces the authentication guard.
   * If the user is not authenticated, redirects them to the login page immediately.
   * Should be called at the initialization of protected pages.
   */
  enforceAuth() {
    if (!this.isAuthenticated()) {
      window.location.href = this.URLS.LOGIN;
    }
  }

  /**
   * Logs out the user.
   * Clears all authentication-related data from storage and redirects to the login page.
   */
  logout() {
    // Clear session storage
    sessionStorage.removeItem(this.KEYS.TOKEN);
    sessionStorage.removeItem(this.KEYS.USER_DATA);

    // Clean up legacy items (if any exist from previous versions)
    sessionStorage.removeItem("isAdminLoggedIn");

    // Clear app-specific state from local storage
    localStorage.removeItem("activeAdminSection");

    // Redirect to login page
    window.location.href = this.URLS.LOGIN;
  }
}
