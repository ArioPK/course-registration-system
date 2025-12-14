/**
 * js/services/core/api.base.js
 */
export class BaseApiService {
  constructor(baseUrl = "http://localhost:8000") {
    this.baseUrl = baseUrl;
    this.timeout = 10000; // 10 seconds timeout
    this.USE_MOCK = true;
  }

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

      const response = await fetch(url, {
        ...options,
        headers: {
          ...this._getHeaders(),
          ...options.headers,
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;

        try {
          const errorData = await response.json();

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
            if (text) errorMessage = text;
          } catch (e2) {}
        }

        throw new Error(errorMessage);
      }

      if (
        response.status === 204 ||
        response.headers.get("content-length") === "0"
      ) {
        return { success: true };
      }

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

      throw error.message
        ? error
        : new Error(`Network error: ${error.message || "Unknown error"}`);
    }
  }
}
