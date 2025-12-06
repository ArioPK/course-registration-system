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
      IS_LOGGED_IN: "isAdminLoggedIn",
      USER_DATA: "userData",
    };

    // Redirect URLs
    this.URLS = {
      LOGIN: "../Login/index.html",
    };
  }

  /**
   * Checks if the user is currently authenticated.
   * Based on the 'isAdminLoggedIn' flag in sessionStorage.
   * @returns {boolean} True if logged in, false otherwise.
   */
  isAuthenticated() {
    return sessionStorage.getItem(this.KEYS.IS_LOGGED_IN) === "true";
  }

  /**
   * Retrieves the current access token.
   * @returns {string|null} The JWT token or null.
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
   * Enforces the authentication guard.
   * If the user is not logged in, redirects them to the login page immediately.
   * Use this at the start of protected pages (like the admin panel).
   */
  enforceAuth() {
    if (!this.isAuthenticated()) {
      window.location.href = this.URLS.LOGIN;
    }
  }

  /**
   * Logs out the user.
   * Clears all auth-related data from storage and redirects to the login page.
   */
  logout() {
    sessionStorage.removeItem(this.KEYS.IS_LOGGED_IN);
    sessionStorage.removeItem(this.KEYS.TOKEN);
    sessionStorage.removeItem(this.KEYS.USER_DATA);

    // Optional: Clear any other app-specific state if needed
    localStorage.removeItem("activeAdminSection");

    window.location.href = this.URLS.LOGIN;
  }
}
