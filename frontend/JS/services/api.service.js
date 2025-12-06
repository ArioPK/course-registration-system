/**
 * js/services/api.service.js
 * Responsibility: Handles HTTP communication OR returns Mock Data for testing.
 * Includes full error handling and response parsing from the original panel.js.
 */

export class ApiService {
  /**
   * @param {string} baseUrl - The base URL of the API
   */
  constructor(baseUrl = "http://localhost:8000") {
    this.baseUrl = baseUrl;
    this.timeout = 10000; // 10 seconds timeout

    // 🔴 تنظیمات ماک: برای تست بدون بک‌ند روی true بگذارید
    this.USE_MOCK = true;

    // دیتابیس ساختگی (برای حالت Mock)
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

  // ============================================================
  // Internal Helpers (ارتباط واقعی با سرور)
  // ============================================================

  _getAuthToken() {
    return sessionStorage.getItem("authToken");
  }

  _getHeaders() {
    const headers = { "Content-Type": "application/json" };
    const token = this._getAuthToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  }

  /**
   * متد اصلی درخواست که تمام لاجیک‌های خطا و پارس کردن را دارد
   * (دقیقاً مشابه panel.js اصلی)
   */
  async _request(endpoint, options = {}) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const url = `${this.baseUrl}${endpoint}`;

      const response = await fetch(url, {
        ...options,
        headers: {
          ...this._getHeaders(),
          ...options.headers,
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // 1. مدیریت خطاهای HTTP
      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;

        try {
          const errorData = await response.json();
          // مدیریت خطاهای استاندارد FastAPI
          if (errorData.detail) {
            errorMessage = Array.isArray(errorData.detail)
              ? errorData.detail
                  .map((e) => e.msg || e.message || JSON.stringify(e))
                  .join(", ")
              : errorData.detail;
          } else if (errorData.message) {
            errorMessage = errorData.message;
          } else if (typeof errorData === "string") {
            errorMessage = errorData;
          }
        } catch (e) {
          // اگر JSON نبود متن خطا را می‌خوانیم
          try {
            const text = await response.text();
            if (text) errorMessage = text;
          } catch (e2) {}
        }

        throw new Error(errorMessage);
      }

      // 2. مدیریت پاسخ‌های خالی (204)
      if (
        response.status === 204 ||
        response.headers.get("content-length") === "0"
      ) {
        return { success: true };
      }

      // 3. پارس کردن پاسخ (JSON یا Text)
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        return await response.json();
      } else {
        const text = await response.text();
        return text ? JSON.parse(text) : { success: true };
      }
    } catch (error) {
      clearTimeout(timeoutId);
      if (error.name === "AbortError") {
        throw new Error("Request timeout. Please try again.");
      }
      // اگر خطا مسیج داشت خودش را بفرست، وگرنه خطای عمومی
      throw error.message
        ? error
        : new Error(`Network error: ${error.message || "Unknown error"}`);
    }
  }

  // ============================================================
  // Public API Methods (Mock + Real Support)
  // ============================================================

  async getCourses() {
    // --- MOCK MODE ---
    if (this.USE_MOCK) {
      console.warn("⚠️ API: Fetching courses (MOCK mode)");
      await new Promise((r) => setTimeout(r, 300));
      return structuredClone(this._mockDB.courses);
    }

    // --- REAL MODE ---
    try {
      const response = await this._request("/api/courses", { method: "GET" });

      // هندل کردن فرمت‌های مختلف پاسخ (مشابه panel.js)
      if (response && typeof response === "object") {
        if (Array.isArray(response)) return response;
        if (response.courses && Array.isArray(response.courses))
          return response.courses;
        if (response.data && Array.isArray(response.data)) return response.data;
        if (response.items && Array.isArray(response.items))
          return response.items;
        if (response.results && Array.isArray(response.results))
          return response.results;
      }

      console.warn("فرمت پاسخ API ناشناخته است:", response);
      return [];
    } catch (error) {
      console.error("Error fetching courses:", error);
      throw new Error(`خطا در دریافت دروس: ${error.message}`);
    }
  }

  async addCourse(courseData) {
    // --- MOCK MODE ---
    if (this.USE_MOCK) {
      console.warn("⚠️ API: Adding course (MOCK mode)", courseData);
      await new Promise((r) => setTimeout(r, 500));
      const newId = Math.max(0, ...this._mockDB.courses.map((c) => c.id)) + 1;
      const newCourse = { id: newId, ...courseData, enrolled: 0 };
      this._mockDB.courses.push(newCourse);
      return newCourse;
    }

    // --- REAL MODE ---
    try {
      const response = await this._request("/api/courses", {
        method: "POST",
        body: JSON.stringify(courseData),
      });

      // هندل کردن لفاف‌های پاسخ (Unwrapping)
      if (response && typeof response === "object") {
        if (response.course) return response.course;
        if (response.data) return response.data;
        return response;
      }
      return response;
    } catch (error) {
      console.error("Error adding course:", error);
      throw new Error(`خطا در افزودن درس: ${error.message}`);
    }
  }

  async updateCourse(id, courseData) {
    // --- MOCK MODE ---
    if (this.USE_MOCK) {
      console.warn("⚠️ API: Updating course (MOCK mode)", id);
      const index = this._mockDB.courses.findIndex((c) => c.id == id);
      if (index !== -1) {
        this._mockDB.courses[index] = {
          ...this._mockDB.courses[index],
          ...courseData,
        };
        return this._mockDB.courses[index];
      }
      return null;
    }

    // --- REAL MODE ---
    try {
      return await this._request(`/api/courses/${id}`, {
        method: "PUT",
        body: JSON.stringify(courseData),
      });
    } catch (error) {
      console.error(`Error updating course ${id}:`, error);
      throw new Error(`خطا در ویرایش درس: ${error.message}`);
    }
  }

  async deleteCourse(id) {
    // --- MOCK MODE ---
    if (this.USE_MOCK) {
      console.warn("⚠️ API: Deleting course (MOCK mode)", id);
      this._mockDB.courses = this._mockDB.courses.filter((c) => c.id != id);
      return { success: true };
    }

    // --- REAL MODE ---
    try {
      return await this._request(`/api/courses/${id}`, {
        method: "DELETE",
      });
    } catch (error) {
      console.error(`Error deleting course ${id}:`, error);
      throw new Error(`خطا در حذف درس: ${error.message}`);
    }
  }
}
