import { BaseApiService } from "../core/api.base.js";
import { mockStore } from "../core/mock.store.js";

export class CourseRepository extends BaseApiService {
  
  async getCourses() {
    // --- MOCK MODE ---
    if (this.USE_MOCK) {
      console.warn("⚠️ API: Fetching courses (MOCK mode)");
      await new Promise((r) => setTimeout(r, 300));
      return structuredClone(mockStore.courses);
    }

    // --- REAL MODE ---
    try {
      const response = await this._request("/api/courses", { method: "GET" });

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
      
      const newId = Math.max(0, ...mockStore.courses.map((c) => c.id)) + 1;
      const newCourse = { id: newId, ...courseData, enrolled: 0 };
      
      mockStore.courses.push(newCourse);
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
      const index = mockStore.courses.findIndex((c) => c.id == id);
      if (index !== -1) {
        mockStore.courses[index] = {
          ...mockStore.courses[index],
          ...courseData,
        };
        return mockStore.courses[index];
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
      mockStore.courses = mockStore.courses.filter((c) => c.id != id);
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