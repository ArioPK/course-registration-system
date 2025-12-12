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
      prerequisites: [], 
      coursesMap: {},    
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
      // Fetch courses and prerequisites in parallel
      const [courses, prerequisites] = await Promise.all([
        this.api.getCourses(),
        this.api.getPrerequisites(), 
      ]);

      this.state.courses = courses || [];
      this.state.prerequisites = prerequisites || []; 

      // Build map for fast course lookup by ID
      this.state.coursesMap = this.state.courses.reduce((acc, course) => {
        acc[course.id] = course;
        return acc;
      }, {}); // <<< ساخت نقشه

      const departments = [
        ...new Set(this.state.courses.map((c) => c.department).filter(Boolean)),
      ];
      const semesters = [
        ...new Set(this.state.courses.map((c) => c.semester).filter(Boolean)),
      ].sort();

      this.view.populateFilters(departments, semesters);
      this.view.populateCourseDropdowns(this.state.courses); 

      this._refreshCourseList();
      this._refreshPrerequisitesList(); 
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

  
  _refreshPrerequisitesList() {
    this.view.renderPrerequisites(this.state.prerequisites, this.state.coursesMap);
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

   
    this.view.bindOpenPrereqModal(() => this.view.openPrereqModal());

    this.view.bindPrerequisiteFormSubmit((formData) =>
      this._handlePrerequisiteFormSubmit(formData)
    );

    this.view.bindPrerequisiteTableActions(
      (id) => this._handleDeletePrerequisiteClick(id)
    );
  
    
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
  
  
  async _handlePrerequisiteFormSubmit(formData) {
    if (formData.target_course_id === formData.prerequisite_course_id) {
        this.view.showError("درس هدف و درس پیش‌نیاز نمی‌توانند یکسان باشند.");
        return;
    }

    // Optional: Frontend validation for duplicate (though backend should enforce it)
    const isDuplicate = this.state.prerequisites.some(
        (p) =>
            p.target_course_id === formData.target_course_id &&
            p.prerequisite_course_id === formData.prerequisite_course_id
    );
    
    if (isDuplicate) {
         this.view.showError("این پیش‌نیاز قبلاً تعریف شده است.");
         return;
    }


    this.view.setPrereqFormSubmitting(true);

    try {
      await this.api.addPrerequisite(formData);
      
      this.view.closePrereqModal();
      await this.loadInitialData(); // Reload all data to refresh tables
      this.view.showSuccess("پیش‌نیاز با موفقیت تعریف شد.");
    } catch (error) {
      console.error(error);
      this.view.showError(`خطا در تعریف پیش‌نیاز: ${error.message}`);
    } finally {
      this.view.setPrereqFormSubmitting(false);
    }
  }

  _handleDeletePrerequisiteClick(id) {
    const prereq = this.state.prerequisites.find((p) => p.id === id);
    if (!prereq) return;

    // Use coursesMap for user-friendly confirmation message
    const targetCourse = this.state.coursesMap[prereq.target_course_id]?.name || `ID ${prereq.target_course_id}`;
    const prereqCourse = this.state.coursesMap[prereq.prerequisite_course_id]?.name || `ID ${prereq.prerequisite_course_id}`;

    this.view.showConfirmation(
      `آیا از حذف پیش‌نیاز "${prereqCourse}" برای درس "${targetCourse}" مطمئن هستید؟`,
      async () => {
        try {
          await this.api.deletePrerequisite(id);

          this.view.showSuccess("پیش‌نیاز با موفقیت حذف شد.");
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