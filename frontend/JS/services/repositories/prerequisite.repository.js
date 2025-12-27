import { BaseApiService } from "../core/api.base.js";
import { mockStore } from "../core/mock.store.js";

export class PrerequisiteRepository extends BaseApiService {
  
  async getPrerequisites() {
    // --- MOCK MODE ---
    if (this.USE_MOCK) {
      console.warn("⚠️ API: Fetching prerequisites (MOCK mode)");
      await new Promise((r) => setTimeout(r, 300));
      return structuredClone(mockStore.prerequisites);
    }

    // --- REAL MODE ---
    try {
      const response = await this._request("/api/prerequisites", {
        method: "GET",
      });
      return response || [];
    } catch (error) {
      throw new Error(`خطا در دریافت پیش‌نیازها: ${error.message}`);
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
      const isDuplicate = mockStore.prerequisites.some(
        (p) =>
          p.target_course_id == data.target_course_id &&
          p.prerequisite_course_id == data.prerequisite_course_id
      );

      if (isDuplicate) {
        throw new Error("این پیش‌نیاز قبلاً تعریف شده است.");
      }

      const newId =
        Math.max(0, ...mockStore.prerequisites.map((p) => p.id)) + 1;
      const newPrereq = { id: newId, ...data };
      
      mockStore.prerequisites.push(newPrereq);
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
      mockStore.prerequisites = mockStore.prerequisites.filter(
        (p) => p.id != prerequisiteId
      );
      return { success: true };
    }

    // --- REAL MODE ---
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