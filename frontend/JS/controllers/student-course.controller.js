/**
 * js/controllers/student-course.controller.js
 * Responsibility: Fetch data and coordinate between API and View.
 */
export class StudentCourseController {
  constructor(apiService, authService, view) {
    this.api = apiService;
    this.auth = authService;
    this.view = view;
  }

  async init() {
    // 1. Auth Guard
    if (!this.auth.isAuthenticated()) {
      this.auth.logout();
      return;
    }

    this._bindEvents();
    await this.loadCourses();
  }

  _bindEvents() {
    this.view.bindLogout(() => this.auth.logout());
  }

  async loadCourses() {
    this.view.setLoading(true);
    try {
      const [courses, prerequisites] = await Promise.all([
        this.api.getCourses(),
        this.api.getPrerequisites(),
      ]);

      const currentSemester = "1403-1";
      const currentCourses = courses.filter(
        (c) => c.semester === currentSemester
      );

      this.view.renderCourses(currentCourses, prerequisites);
    } catch (error) {
      console.error("StudentController Error:", error);
      this.view.showError(
        "خطا در دریافت لیست دروس. لطفاً اتصال خود را بررسی کنید."
      );
    } finally {
      this.view.setLoading(false);
    }
  }
}
