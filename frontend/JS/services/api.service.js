/**
 * js/services/api.service.js
 * Responsibility: Handles all HTTP communication with the backend.
 * Includes: Token management, global error handling, and CRUD methods.
 */

export class ApiService {
    /**
     * @param {string} baseUrl - The base URL of the API (e.g., http://localhost:8000)
     */
    constructor(baseUrl = "http://localhost:8000") {
      this.baseUrl = baseUrl;
      this.timeout = 10000; // 10 seconds timeout
    }
  
    // ============================================================
    // Internal Helpers
    // ============================================================
  
    /**
     * Retrieves the authentication token from session storage.
     * @returns {string|null} The JWT token or null if not found.
     * @private
     */
    _getAuthToken() {
      return sessionStorage.getItem("authToken");
    }
  
    /**
     * Constructs the headers required for the request.
     * Automatically adds the Authorization header if a token exists.
     * @returns {Object} The headers object.
     * @private
     */
    _getHeaders() {
      const headers = {
        "Content-Type": "application/json",
      };
      const token = this._getAuthToken();
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }
      return headers;
    }
  
    /**
     * The core request method that handles fetch configuration, timeouts,
     * error parsing, and response formatting.
     * * @param {string} endpoint - The API endpoint (e.g., '/api/courses')
     * @param {Object} options - Fetch options (method, body, etc.)
     * @returns {Promise<any>} The parsed JSON response or success object.
     * @private
     */
    async _request(endpoint, options = {}) {
      // 1. Setup Timeout using AbortController
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
  
        // 2. Handle HTTP Errors (status codes outside 200-299)
        if (!response.ok) {
          let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
  
          try {
            const errorData = await response.json();
            // Handle FastAPI standard error format (detail field)
            if (errorData.detail) {
              // FastAPI sometimes returns an array of errors or a single string
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
            // Fallback if response is not JSON
            try {
              const text = await response.text();
              if (text) errorMessage = text;
            } catch (e2) {
              // Keep default HTTP status message
            }
          }
  
          throw new Error(errorMessage);
        }
  
        // 3. Handle Empty Responses (e.g., 204 No Content)
        if (
          response.status === 204 ||
          response.headers.get("content-length") === "0"
        ) {
          return { success: true };
        }
  
        // 4. Parse Response (JSON or Text)
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
        
        // Propagate the specific error message if available
        throw error.message ? error : new Error(`Network error: ${error.message || "Unknown error"}`);
      }
    }
  
    // ============================================================
    // Public API Methods (Used by Controllers)
    // ============================================================
  
    /**
     * Fetches the list of all courses.
     * GET /api/courses
     * @returns {Promise<Array>} List of courses.
     */
    async getCourses() {
      try {
        const response = await this._request("/api/courses", { method: "GET" });
  
        // Handle various response wrappers often found in backends (FastAPI)
        if (response && typeof response === "object") {
          if (Array.isArray(response)) {
            return response; // Direct array: [ ... ]
          } else if (response.courses && Array.isArray(response.courses)) {
            return response.courses; // Wrapped: { courses: [ ... ] }
          } else if (response.data && Array.isArray(response.data)) {
            return response.data; // Wrapped: { data: [ ... ] }
          } else if (response.items && Array.isArray(response.items)) {
            return response.items; // Wrapped: { items: [ ... ] }
          } else if (response.results && Array.isArray(response.results)) {
            return response.results; // Paginated: { results: [ ... ] }
          }
        }
  
        console.warn("Unknown API response format for courses:", response);
        return []; // Fallback to empty array
      } catch (error) {
        console.error("Error fetching courses:", error);
        throw new Error(`Error fetching courses: ${error.message}`);
      }
    }
  
    /**
     * Adds a new course.
     * POST /api/courses
     * @param {Object} courseData - The course data object.
     * @returns {Promise<Object>} The created course object.
     */
    async addCourse(courseData) {
      try {
        const response = await this._request("/api/courses", {
          method: "POST",
          body: JSON.stringify(courseData),
        });
  
        // Unwrap the response if necessary
        if (response && typeof response === "object") {
          if (response.course) return response.course;
          if (response.data) return response.data;
          return response;
        }
        return response;
      } catch (error) {
        console.error("Error adding course:", error);
        throw new Error(`Error adding course: ${error.message}`);
      }
    }
  
    /**
     * Updates an existing course.
     * PUT /api/courses/{id}
     * @param {number|string} id - The course ID.
     * @param {Object} courseData - The updated course data.
     * @returns {Promise<Object>} The updated course object.
     */
    async updateCourse(id, courseData) {
      try {
        return await this._request(`/api/courses/${id}`, {
          method: "PUT",
          body: JSON.stringify(courseData),
        });
      } catch (error) {
        console.error(`Error updating course ${id}:`, error);
        throw new Error(`Error updating course: ${error.message}`);
      }
    }
  
    /**
     * Deletes a course.
     * DELETE /api/courses/{id}
     * @param {number|string} id - The course ID.
     * @returns {Promise<Object>} Success response.
     */
    async deleteCourse(id) {
      try {
        return await this._request(`/api/courses/${id}`, {
          method: "DELETE",
        });
      } catch (error) {
        console.error(`Error deleting course ${id}:`, error);
        throw new Error(`Error deleting course: ${error.message}`);
      }
    }
  }