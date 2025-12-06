/**
 * js/services/api.service.js
 * Handles HTTP communication and Mock Data.
 */
export class ApiService {
  constructor(baseUrl = "http://localhost:8000") {
    this.baseUrl = baseUrl;
    this.timeout = 10000;
    this.USE_MOCK = true; // 🔴 Toggle this for Real/Mock

    // Mock Data
    this._mockDB = {
        courses: [
          {
            id: 1,
            code: "CS101",
            name: "مبانی کامپیوتر",
            units: 3,
            department: "کامپیوتر",
            semester: "1403-1",
            professor_name: "دکتر رضایی",
            day_of_week: "SAT",
            start_time: "08:00",
            end_time: "09:30",
            location: "کلاس 101",
            capacity: 40,
            enrolled: 35,
          },
          {
            id: 2,
            code: "CS102",
            name: "برنامه‌نویسی پیشرفته",
            units: 3,
            department: "کامپیوتر",
            semester: "1403-1",
            professor_name: "دکتر احمدی",
            day_of_week: "MON",
            start_time: "10:00",
            end_time: "11:30",
            location: "سایت کامپیوتر",
            capacity: 30,
            enrolled: 28,
          },
          {
            id: 3,
            code: "MATH101",
            name: "ریاضی عمومی ۱",
            units: 3,
            department: "ریاضی",
            semester: "1403-1",
            professor_name: "دکتر مریمی",
            day_of_week: "SUN",
            start_time: "14:00",
            end_time: "16:00",
            location: "تالار ۱",
            capacity: 50,
            enrolled: 12,
          },
          {
            id: 4,
            code: "PHYS101",
            name: "فیزیک ۱",
            units: 3,
            department: "فیزیک",
            semester: "1403-1",
            professor_name: "دکتر کمالی",
            day_of_week: "WED",
            start_time: "08:00",
            end_time: "10:00",
            location: "آزمایشگاه فیزیک",
            capacity: 35,
            enrolled: 35,
          },
        ],
      };
  }

  // --- Helpers ---
  _getAuthToken() {
    return sessionStorage.getItem("authToken");
  }

  _getHeaders() {
    const headers = { "Content-Type": "application/json" };
    const token = this._getAuthToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
    return headers;
  }

  async _request(endpoint, options = {}) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers: { ...this._getHeaders(), ...options.headers },
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      const data = await response.json().catch(() => ({})); // Safe JSON parse

      if (!response.ok) {
        // Handle FastAPI errors
        const msg = data.detail
          ? Array.isArray(data.detail)
            ? data.detail.map((e) => e.msg).join(", ")
            : data.detail
          : data.message || `HTTP ${response.status}`;
        throw new Error(msg);
      }
      return data;
    } catch (error) {
      clearTimeout(timeoutId);
      throw error.name === "AbortError" ? new Error("Time out") : error;
    }
  }

  // --- Auth Methods ---
  async login(username, password) {
    if (this.USE_MOCK) {
      console.warn("⚠️ API: Login (MOCK)");
      await new Promise((r) => setTimeout(r, 1000));
      if (username === "admin" && password === "1234") {
        return {
          success: true,
          access_token: "mock_token_" + Date.now(),
          user: { username: "admin", role: "admin" },
        };
      }
      throw new Error("نام کاربری یا رمز عبور اشتباه است (Mock: admin/1234)");
    }
    return await this._request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
  }

  // --- Course Methods ---
  async getCourses() {
    if (this.USE_MOCK) {
      await new Promise((r) => setTimeout(r, 300));
      return [...this._mockDB.courses];
    }
    const res = await this._request("/api/courses", { method: "GET" });
    return Array.isArray(res) ? res : res.data || res.courses || [];
  }

  async addCourse(data) {
    if (this.USE_MOCK) {
      await new Promise((r) => setTimeout(r, 500));
      const newC = { id: Date.now(), ...data, enrolled: 0 };
      this._mockDB.courses.push(newC);
      return newC;
    }
    return await this._request("/api/courses", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateCourse(id, data) {
    if (this.USE_MOCK) {
      const idx = this._mockDB.courses.findIndex((c) => c.id == id);
      if (idx > -1)
        this._mockDB.courses[idx] = { ...this._mockDB.courses[idx], ...data };
      return this._mockDB.courses[idx];
    }
    return await this._request(`/api/courses/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteCourse(id) {
    if (this.USE_MOCK) {
      this._mockDB.courses = this._mockDB.courses.filter((c) => c.id != id);
      return { success: true };
    }
    return await this._request(`/api/courses/${id}`, { method: "DELETE" });
  }
}
