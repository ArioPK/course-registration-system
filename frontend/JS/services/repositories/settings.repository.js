import { BaseApiService } from "../core/api.base.js";
import { mockStore } from "../core/mock.store.js";

export class SettingsRepository extends BaseApiService {
  
  async getUnitConfiguration() {
    // --- MOCK MODE ---
    if (this.USE_MOCK) {
      console.warn("⚠️ API: Fetching unit configuration (MOCK mode)");
      await new Promise((r) => setTimeout(r, 200));
      return structuredClone(mockStore.unitConfig);
    }

    // --- REAL MODE ---
    try {
      const response = await this._request("/api/settings/units", {
        method: "GET",
      });
      return response || { min_units: 12, max_units: 20 };
    } catch (error) {
      throw new Error(`خطا در دریافت تنظیمات واحد: ${error.message}`);
    }
  }

  async saveUnitConfiguration(configData) {
    // --- MOCK MODE ---
    if (this.USE_MOCK) {
      console.warn("⚠️ API: Saving unit configuration (MOCK mode)", configData);
      await new Promise((r) => setTimeout(r, 500));
      
      mockStore.unitConfig = { ...configData };
      return structuredClone(mockStore.unitConfig);
    }

    // --- REAL MODE ---
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
}