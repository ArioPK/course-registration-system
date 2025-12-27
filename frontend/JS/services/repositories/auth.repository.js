import { BaseApiService } from "../core/api.base.js";

export class AuthRepository extends BaseApiService {
  /**
   * Logs in the user.
   */
  async login(username, password) {
    // --- MOCK MODE ---
    if (this.USE_MOCK) {
      console.warn("⚠️ API: Login (MOCK mode)");
      await new Promise((r) => setTimeout(r, 1000));

      if (username === "admin" && password === "admin123") {
        return {
          access_token: "mock_token_admin",
          token_type: "bearer",
          user: { username: "admin", role: "admin" },
        };
      }

      if (username === "std1" && password === "1234") {
        return {
          access_token: "mock_token_student",
          token_type: "bearer",
          user: { username: "std1", role: "student", id: 101 },
        };
      }

      if (username === "prof1" && password === "1234") {
        return {
          access_token: "mock_token_prof",
          token_type: "bearer",
          user: { username: "prof1", role: "professor", id: 201 },
        };
      }

      if (
        username === "admin" &&
        (password === "1234" || password === "admin123")
      ) {
        return {
          access_token: "mock_jwt_token_" + Date.now(),
          token_type: "bearer",
          user: { username: "admin", role: "admin" },
        };
      }
      throw new Error("نام کاربری یا رمز عبور اشتباه است.");
    }

    // --- REAL MODE ---
    return await this._request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
  }
}
