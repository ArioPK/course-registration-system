/**
 * frontend/JS/controllers/professor-course.controller.js
 */
export class ProfessorCourseController {
  constructor(apiService, authService, view) {
    this.apiService = apiService;
    this.authService = authService;
    this.view = view;
    this.currentCourseId = null;
  }

  async init() {
    await this.loadCourses();
  }

  async loadCourses() {
    try {
      this.view.showLoading(true);
      const courses = await this.apiService.getProfessorCourses();

      this.view.renderCourses(courses, (course) => {
        this.handleManageStudents(course);
      });
    } catch (error) {
      console.error(error);
      this.view.showError("خطا در دریافت لیست دروس.");
    } finally {
      this.view.showLoading(false);
    }
  }

  async handleManageStudents(course) {
    this.currentCourseId = course.id;
    try {
      this.view.showLoading(true);
      const students = await this.apiService.getCourseStudents(course.id);

      this.view.renderStudents(course.name, students, (studentId) =>
        this.handleRemoveStudent(studentId)
      );
    } catch (error) {
      console.error(error);
      this.view.showError("خطا در دریافت لیست دانشجویان.");
    } finally {
      this.view.showLoading(false);
    }
  }

  async handleRemoveStudent(studentId) {
    if (!this.currentCourseId) return;

    try {
      this.view.showLoading(true);
      await this.apiService.removeStudentFromCourse(
        this.currentCourseId,
        studentId
      );

      const updatedStudents = await this.apiService.getCourseStudents(
        this.currentCourseId
      );

      const courseName = document.getElementById(
        "selected-course-name"
      ).textContent;

      this.view.renderStudents(courseName, updatedStudents, (sId) =>
        this.handleRemoveStudent(sId)
      );
    } catch (error) {
      console.error(error);

      let msg = "خطا در حذف دانشجو.";
      if (error.message && error.message.includes("409")) {
        msg = "امکان حذف دانشجو در ترم جاری وجود ندارد.";
      }
      this.view.showError(msg);
    } finally {
      this.view.showLoading(false);
    }
  }
}
