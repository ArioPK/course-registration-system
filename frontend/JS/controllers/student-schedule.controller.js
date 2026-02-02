/**
 * frontend/JS/controllers/student-schedule.controller.js
 */
export class StudentScheduleController {
  constructor(apiService, view) {
    this.apiService = apiService;
    this.view = view;

    this.viewScheduleBtn = document.getElementById("view-schedule-btn");
    this.backToCatalogBtn = document.getElementById("back-to-catalog-btn");

    this._bindEvents();
  }

  _bindEvents() {
    if (this.viewScheduleBtn) {
      this.viewScheduleBtn.addEventListener("click", () =>
        this.loadAndShowSchedule()
      );
    }

    if (this.backToCatalogBtn) {
      this.backToCatalogBtn.addEventListener("click", () => {
        this.view.toggleView(false);
      });
    }
  }

  async loadAndShowSchedule() {
    this.view.toggleView(true);

    const spinner = document.getElementById("loading-spinner");
    if (spinner) spinner.classList.remove("hidden");
    document.getElementById("schedule-container").innerHTML = "";

    try {
      const scheduleData = await this.apiService.getStudentSchedule();
      this.view.renderSchedule(scheduleData);
    } catch (error) {
      console.error(error);

      const container = document.getElementById("schedule-container");
      container.innerHTML = `<p style="color:var(--danger); text-align:center; padding:20px;">خطا در دریافت برنامه هفتگی.</p>`;
    } finally {
      if (spinner) spinner.classList.add("hidden");
    }
  }
}
