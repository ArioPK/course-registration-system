/**
 * js/controllers/course.controller.js
 * Responsibility: Orchestrates the application logic.
 */

export class CourseController {
  /**
   * @param {ApiService} apiService
   * @param {AuthService} authService
   * @param {CourseValidator} validator
   * @param {CourseView} view
   */
  constructor(apiService, authService, validator, view) {
    this.api = apiService;
    this.auth = authService;
    this.validator = validator;
    this.view = view;

    this.state = {
      courses: [],
      currentEditId: null,
      searchQuery: "",
      filterDepartment: "",
      filterSemester: "",
    };
  }

  async init() {
    // 1. Check Auth (Redundant if handled in main.js, but good for safety)
    // if (!this.auth.isAuthenticated()) {
    //   this.auth.logout();
    //  return;
    //}
    this._bindEvents();
    await this.loadInitialData();
  }

  async loadInitialData() {
    try {
      const courses = await this.api.getCourses();
      this.state.courses = courses || [];

      const departments = [
        ...new Set(this.state.courses.map((c) => c.department).filter(Boolean)),
      ];
      const semesters = [
        ...new Set(this.state.courses.map((c) => c.semester).filter(Boolean)),
      ].sort();

      this.view.populateFilters(departments, semesters);
      this._refreshCourseList();
      this._updateSummary();
    } catch (error) {
      console.error(error);

      this.view.showError(error.message || "خطا در بارگیری اطلاعات.");
    }
  }

  _getFilteredCourses() {
    let filtered = [...this.state.courses];

    if (this.state.searchQuery) {
      const query = this.state.searchQuery.toLowerCase();
      filtered = filtered.filter(
        (c) =>
          c.name.toLowerCase().includes(query) ||
          c.code.toLowerCase().includes(query) ||
          c.department.toLowerCase().includes(query)
      );
    }

    if (this.state.filterDepartment) {
      filtered = filtered.filter(
        (c) => c.department === this.state.filterDepartment
      );
    }

    if (this.state.filterSemester) {
      filtered = filtered.filter(
        (c) => c.semester === this.state.filterSemester
      );
    }

    return filtered;
  }

  _refreshCourseList() {
    const filteredCourses = this._getFilteredCourses();
    this.view.renderCourses(filteredCourses);
  }

  _updateSummary() {
    const totalCourses = this.state.courses.length;
    const totalCapacity = this.state.courses.reduce(
      (sum, c) => sum + (c.capacity || 0),
      0
    );
    const totalEnrolled = this.state.courses.reduce(
      (sum, c) => sum + (c.enrolled || 0),
      0
    );

    this.view.updateSummary({
      totalCourses,
      totalCapacity,
      totalEnrolled,
    });
  }

  _bindEvents() {
    this.view.bindSearch((query) => {
      this.state.searchQuery = query;
      this._refreshCourseList();
    });

    this.view.bindFilterDepartment((value) => {
      this.state.filterDepartment = value;
      this._refreshCourseList();
    });

    this.view.bindFilterSemester((value) => {
      this.state.filterSemester = value;
      this._refreshCourseList();
    });

    this.view.bindAddCourseBtn(() => this._handleAddCourseClick());
    this.view.bindCancelCourseBtn(() => this.view.closeCourseModal());

    this.view.bindCourseFormSubmit((formData) =>
      this._handleFormSubmit(formData)
    );

    this.view.bindTableActions(
      (id) => this._handleEditCourseClick(id),
      (id) => this._handleDeleteCourseClick(id)
    );

    this.view.bindModalCloseBtns((modal) => {
      this.view.closeModal(modal);
      this.view.resetForm();
    });

    this.view.bindNavLinks((targetId) => {
      localStorage.setItem("activeAdminSection", targetId);
      this.view.setActiveSection(targetId);
    });

    this.view.bindLogout(() => this.auth.logout());

    const activeSection =
      localStorage.getItem("activeAdminSection") || "course-management";
    this.view.setActiveSection(activeSection);
  }

  _handleAddCourseClick() {
    this.state.currentEditId = null;
    this.view.resetForm();
    this.view.setModalTitle("افزودن درس جدید");
    this.view.clearValidationErrors();
    this.view.openCourseModal();
  }

  _handleEditCourseClick(id) {
    const course = this.state.courses.find((c) => c.id === id);
    if (!course) return;

    this.state.currentEditId = id;
    this.view.fillForm(course);
    this.view.setModalTitle("ویرایش درس");
    this.view.clearValidationErrors();
    this.view.openCourseModal();
  }

  _handleDeleteCourseClick(id) {
    const course = this.state.courses.find((c) => c.id === id);
    if (!course) return;

    this.view.showConfirmation(
      `آیا از حذف درس "${course.name}" (${course.code}) مطمئن هستید؟`,
      async () => {
        try {
          await this.api.deleteCourse(id);

          this.view.showSuccess("درس با موفقیت حذف شد.");
          await this.loadInitialData();
        } catch (error) {
          this.view.showError(error.message);
        }
      }
    );
  }

  async _handleFormSubmit(formData) {
    this.view.clearValidationErrors();

    const validationResult = this.validator.validate(
      formData,
      this.state.courses,
      this.state.currentEditId
    );

    if (!validationResult.isValid) {
      this.view.showValidationErrors(validationResult.errors);
      return;
    }

    this.view.setFormSubmitting(true);

    try {
      if (this.state.currentEditId) {
        await this.api.updateCourse(this.state.currentEditId, formData);
      } else {
        await this.api.addCourse(formData);
      }

      this.view.resetForm();
      this.view.closeCourseModal();
      this.state.currentEditId = null;

      await this.loadInitialData();

      this.view.showSuccess("درس با موفقیت ذخیره شد.");
    } catch (error) {
      console.error(error);

      this.view.showError(`خطا: ${error.message}`);
    } finally {
      this.view.setFormSubmitting(false);
    }
  }
}
