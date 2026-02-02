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

    // Mock Mode
    this.USE_MOCK = false;

    // Mock Database
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

      prerequisites: [
        {
          id: 1,
          target_course_id: 2,
          prerequisite_course_id: 1,
        },
        {
          id: 2,
          target_course_id: 4,
          prerequisite_course_id: 3,
        },
      ],

      unitConfig: {
        min_units: 12,
        max_units: 20,
      },
    };
  }

  // ============================================================
  // Private Method
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

  async _request(endpoint, options = {}) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const url = `${this.baseUrl}${endpoint}`;
      console.log(`[API Request] ${options.method || "GET"} ${url}`);

      const response = await fetch(url, {
        ...options,
        headers: {
          ...this._getHeaders(),
          ...options.headers,
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      console.log(`[API Response] ${response.status} ${response.statusText} for ${url}`);

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;

        try {
          const errorData = await response.json();
          console.error(`[API Error] ${url}:`, errorData);

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
          try {
            const text = await response.text();
            if (text) {
              errorMessage = text;
              console.error(`[API Error Text] ${url}:`, text);
            }
          } catch (e2) {
            console.error(`[API Error] Failed to read error response:`, e2);
          }
        }

        throw new Error(errorMessage);
      }

      if (
        response.status === 204 ||
        response.headers.get("content-length") === "0"
      ) {
        console.log(`[API Success] ${url} - No content (204)`);
        return { success: true };
      }

      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        const data = await response.json();
        console.log(`[API Success] ${url} - JSON response:`, data);
        return data;
      } else {
        const text = await response.text();
        const parsed = text ? JSON.parse(text) : { success: true };
        console.log(`[API Success] ${url} - Text response parsed:`, parsed);
        return parsed;
      }
    } catch (error) {
      clearTimeout(timeoutId);
      console.error(`[API Request Failed] ${endpoint}:`, error);
      
      if (error.name === "AbortError") {
        throw new Error("Request timeout. Please try again.");
      }

      if (error.message) {
        throw error;
      }
      
      throw new Error(`Network error: ${error.message || "Unknown error"}`);
    }
  }
  // ============================================================
  // Auth Methods (Login)
  // ============================================================

  /**
   * Logs in the user.
   * POST /auth/login
   * @param {string} username
   * @param {string} password
   * @returns {Promise<Object>} Login response with token.
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

      if (username === "stu_1001" && password === "1234") {
        return {
          access_token: "mock_token_student_1001",
          token_type: "bearer",
          user: { username: "stu_1001", role: "student", id: 1001 },
        };
      }

      if (username === "prof1" && password === "1234") {
        return {
          access_token: "mock_token_prof",
          token_type: "bearer",
          user: { username: "prof1", role: "professor", id: 201 },
        };
      }

      if (username === "p123456" && password === "1234") {
        return {
          access_token: "mock_token_prof_123456",
          token_type: "bearer",
          user: { username: "p123456", role: "professor", id: 123456 },
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
  // ============================================================
  // Public API Methods (Mock + Real Support)
  // ============================================================
  /**
   * Gets all courses from the API.
   * @returns {Promise<Array<Object>>} - An array of course objects.
   */

  // --- Enrollment Methods ---

  /**
   */
  async enrollCourse(courseId) {
    try {
      return await this._request("/api/student/enrollments", {
        method: "POST",
        body: JSON.stringify({ course_id: courseId }),
      });
    } catch (error) {
      console.error("Error enrolling course:", error);
      throw error;
    }
  }

  /**
   */
  async getMyEnrollments() {
    // --- MOCK MODE ---
    if (this.USE_MOCK) {
      console.warn("⚠️ API: Fetching enrollments (MOCK mode)");
      await new Promise((r) => setTimeout(r, 300));
      // Return empty array for mock mode (no enrollments by default)
      return [];
    }

    // --- REAL MODE ---
    try {
      console.log("Fetching enrollments from /api/student/enrollments");
      const response = await this._request("/api/student/enrollments", { method: "GET" });
      console.log("Enrollments response:", response);
      
      // Backend returns array of StudentEnrollmentItemRead
      if (Array.isArray(response)) {
        return response;
      }
      
      // Fallback if wrapped in object
      if (response && Array.isArray(response.enrollments)) {
        return response.enrollments;
      }
      
      return [];
    } catch (error) {
      console.error("Error fetching enrollments:", error);
      // Don't throw, return empty array so UI can still work
      console.warn("Returning empty enrollments array due to error");
      return [];
    }
  }

  /**
   */
  async dropCourse(courseId) {
    try {
      return await this._request(`/api/student/enrollments/${courseId}`, {
        method: "DELETE",
      });
    } catch (error) {
      console.error("Error dropping course:", error);
      throw error;
    }
  }
  async getStudentSchedule() {
    // --- MOCK MODE ---
    if (this.USE_MOCK) {
      console.warn("⚠️ API: Fetching student schedule (MOCK mode)");
      await new Promise((r) => setTimeout(r, 300));
      // Return empty schedule for mock mode
      return { days: [] };
    }

    // --- REAL MODE ---
    try {
      return await this._request("/api/student/schedule", { method: "GET" });
    } catch (error) {
      console.error("Error fetching student schedule:", error);
      throw error;
    }
  }

  // --- Professor Methods ---

  async getProfessorCourses() {
    // --- MOCK MODE ---
    if (this.USE_MOCK) {
      console.warn("⚠️ API: Fetching professor courses (MOCK mode)");
      await new Promise((r) => setTimeout(r, 300));
      // Return all courses for professor in mock mode
      // In real mode, backend would filter by professor
      return structuredClone(this._mockDB.courses);
    }

    // --- REAL MODE ---
    try {
      return await this._request("/api/professor/courses", { method: "GET" });
    } catch (error) {
      console.error("Error fetching professor courses:", error);
      throw error;
    }
  }

  async getCourseStudents(courseId) {
    // --- MOCK MODE ---
    if (this.USE_MOCK) {
      console.warn("⚠️ API: Fetching course students (MOCK mode)", courseId);
      await new Promise((r) => setTimeout(r, 300));
      // Return empty array for mock mode (no students enrolled by default)
      return [];
    }

    // --- REAL MODE ---
    try {
      const response = await this._request(
        `/api/professor/courses/${courseId}/students`,
        {
          method: "GET",
        }
      );

      // Backend returns ProfessorCourseStudentsRead with students array
      if (response && response.students && Array.isArray(response.students)) {
        return response.students;
      }
      // Fallback if response is already an array
      if (Array.isArray(response)) {
        return response;
      }
      return [];
    } catch (error) {
      console.error(`Error fetching students for course ${courseId}:`, error);
      throw error;
    }
  }

  async removeStudentFromCourse(courseId, studentId) {
    try {
      return await this._request(
        `/api/professor/courses/${courseId}/students/${studentId}`,
        {
          method: "DELETE",
        }
      );
    } catch (error) {
      console.error(
        `Error removing student ${studentId} from course ${courseId}:`,
        error
      );
      throw error;
    }
  }

  /**
   * Gets all courses - used by ADMIN panel
   * @returns {Promise<Array<Object>>} - An array of course objects.
   */
  async getCourses() {
    // --- MOCK MODE ---
    if (this.USE_MOCK) {
      console.warn("⚠️ API: Fetching courses (MOCK mode)");
      await new Promise((r) => setTimeout(r, 300));
      return structuredClone(this._mockDB.courses);
    }

    // --- REAL MODE ---
    // Admin endpoint - returns all courses
    try {
      console.log("Fetching courses from /api/courses (admin endpoint)");
      const response = await this._request("/api/courses", { method: "GET" });

      if (response && typeof response === "object") {
        if (Array.isArray(response)) {
          console.log(`Received ${response.length} courses`);
          return response;
        }
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
      throw new Error(`خطا در دریافت دروس: ${error.message || "Unknown error"}`);
    }
  }

  /**
   * Gets student courses - used by STUDENT panel
   * @returns {Promise<Array<Object>>} - An array of course objects available for enrollment.
   */
  async getStudentCourses() {
    // --- MOCK MODE ---
    if (this.USE_MOCK) {
      console.warn("⚠️ API: Fetching student courses (MOCK mode)");
      await new Promise((r) => setTimeout(r, 300));
      return structuredClone(this._mockDB.courses);
    }

    // --- REAL MODE ---
    // Student endpoint - returns courses available for enrollment
    try {
      console.log("Fetching courses from /api/student/courses");
      const response = await this._request("/api/student/courses", { method: "GET" });
      console.log("Student courses response:", response);

      if (response && typeof response === "object") {
        if (Array.isArray(response)) {
          console.log(`Received ${response.length} student courses`);
          return response;
        }
        if (response.courses && Array.isArray(response.courses)) {
          console.log(`Received ${response.courses.length} courses from courses field`);
          return response.courses;
        }
        if (response.data && Array.isArray(response.data)) {
          console.log(`Received ${response.data.length} courses from data field`);
          return response.data;
        }
        if (response.items && Array.isArray(response.items)) {
          console.log(`Received ${response.items.length} courses from items field`);
          return response.items;
        }
        if (response.results && Array.isArray(response.results)) {
          console.log(`Received ${response.results.length} courses from results field`);
          return response.results;
        }
      }

      console.warn("فرمت پاسخ API ناشناخته است:", response);
      return [];
    } catch (error) {
      console.error("Error fetching student courses:", error);
      // Re-throw with more context
      if (error.message) {
        throw error;
      }
      throw new Error(`خطا در دریافت دروس: ${error.message || "Unknown error"}`);
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

  // ============================================================
  // Unit Configuration Methods (Mock + Real Support)
  // ============================================================

  /**
   * Gets the current unit configuration settings.
   * @returns {Promise<Object>} - The current min/max unit settings.
   */
  async getUnitConfiguration() {
    // --- MOCK MODE ---
    if (this.USE_MOCK) {
      console.warn("⚠️ API: Fetching unit configuration (MOCK mode)");
      await new Promise((r) => setTimeout(r, 200));
      return structuredClone(this._mockDB.unitConfig);
    }

    // --- REAL MODE (Assuming backend route is /api/settings/units) ---
    try {
      console.log("Fetching unit configuration from /api/settings/units");
      const response = await this._request("/api/settings/units", {
        method: "GET",
      });
      console.log("Unit config response:", response);
      
      // Provide a default if backend returns empty/null
      return response || { min_units: 12, max_units: 20 };
    } catch (error) {
      console.error("Error fetching unit configuration:", error);
      // Don't throw, return default config so UI can still work
      console.warn("Returning default unit config due to error");
      return { min_units: 12, max_units: 20 };
    }
  }

  /**
   * Saves the new unit configuration settings.
   * @param {Object} configData - { min_units, max_units }
   * @returns {Promise<Object>} - The saved configuration object.
   */
  async saveUnitConfiguration(configData) {
    // --- MOCK MODE ---
    if (this.USE_MOCK) {
      console.warn("⚠️ API: Saving unit configuration (MOCK mode)", configData);
      await new Promise((r) => setTimeout(r, 500));
      this._mockDB.unitConfig = { ...configData };
      return structuredClone(this._mockDB.unitConfig);
    }

    // --- REAL MODE (Assuming backend route is /api/settings/units) ---
    try {
      return await this._request("/api/settings/units", {
        method: "PUT",
        body: JSON.stringify(configData),
      });
    } catch (error) {
      console.error("Error saving unit configuration:", error);
      throw new Error(`خطا در ذخیره تنظیمات واحد: ${error.message}`);
    }
  }

  // ============================================================
  // Prerequisite Methods (Mock + Real Support)
  // ============================================================

  async getPrerequisites() {
    // --- MOCK MODE ---
    if (this.USE_MOCK) {
      console.warn("⚠️ API: Fetching prerequisites (MOCK mode)");
      await new Promise((r) => setTimeout(r, 300));
      return structuredClone(this._mockDB.prerequisites);
    }

    // --- REAL MODE (Assuming backend route is /api/prerequisites) ---
    try {
      console.log("Fetching prerequisites from /api/prerequisites");
      const response = await this._request("/api/prerequisites", {
        method: "GET",
      });
      console.log("Prerequisites response:", response);
      
      if (Array.isArray(response)) {
        return response;
      }
      
      return response || [];
    } catch (error) {
      console.error("Error fetching prerequisites:", error);
      // Don't throw, return empty array so UI can still work
      console.warn("Returning empty prerequisites array due to error");
      return [];
    }
  }

  async addPrerequisite(data) {
    // --- MOCK MODE ---
    if (this.USE_MOCK) {
      console.warn("⚠️ API: Adding prerequisite (MOCK mode)", data);
      await new Promise((r) => setTimeout(r, 500));

      if (data.target_course_id == data.prerequisite_course_id) {
        throw new Error("درس هدف و پیش‌نیاز نمی‌توانند یکسان باشند.");
      }

      // Mock uniqueness check
      const isDuplicate = this._mockDB.prerequisites.some(
        (p) =>
          p.target_course_id == data.target_course_id &&
          p.prerequisite_course_id == data.prerequisite_course_id
      );

      if (isDuplicate) {
        throw new Error("این پیش‌نیاز قبلاً تعریف شده است.");
      }

      const newId =
        Math.max(0, ...this._mockDB.prerequisites.map((p) => p.id)) + 1;
      const newPrereq = { id: newId, ...data };
      this._mockDB.prerequisites.push(newPrereq);
      return newPrereq;
    }

    // --- REAL MODE ---
    try {
      return await this._request("/api/prerequisites", {
        method: "POST",
        body: JSON.stringify(data),
      });
    } catch (error) {
      console.error("Error adding prerequisite:", error);
      throw new Error(`خطا در افزودن پیش‌نیاز: ${error.message}`);
    }
  }

  async deletePrerequisite(prerequisiteId) {
    // --- MOCK MODE ---
    if (this.USE_MOCK) {
      console.warn("⚠️ API: Deleting prerequisite (MOCK mode)", prerequisiteId);
      this._mockDB.prerequisites = this._mockDB.prerequisites.filter(
        (p) => p.id != prerequisiteId
      );
      return { success: true };
    }

    // --- REAL MODE (Assuming backend route is /api/prerequisites/{id}) ---
    try {
      return await this._request(`/api/prerequisites/${prerequisiteId}`, {
        method: "DELETE",
      });
    } catch (error) {
      console.error(`Error deleting prerequisite ${prerequisiteId}:`, error);
      throw new Error(`خطا در حذف پیش‌نیاز: ${error.message}`);
    }
  }
}
