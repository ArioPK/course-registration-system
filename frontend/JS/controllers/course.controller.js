/**
 * js/controllers/course.controller.js
 * Responsibility: Orchestrates the application logic.
 * It connects the API, Auth, Validator, and View layers.
 * Handles user interactions and state management.
 */

export class CourseController {
  /**
   * @param {ApiService} apiService - Service for API calls
   * @param {AuthService} authService - Service for authentication
   * @param {CourseValidator} validator - Service for validation
   * @param {CourseView} view - Service for UI rendering and DOM manipulation
   */
  constructor(apiService, authService, validator, view) {
    this.api = apiService;
    this.auth = authService;
    this.validator = validator;
    this.view = view;

    // App State (Similar to 'state' and 'data' objects in panel.js)
    this.state = {
      courses: [], // All loaded courses
      currentEditId: null, // ID of the course being edited (null for add mode)
      searchQuery: "",
      filterDepartment: "",
      filterSemester: "",
    };
  }

  /**
   * Initializes the application.
   * Loads initial data and binds UI events.
   */
  async init() {
    // 1. Check Auth (Redundant if handled in main.js, but good for safety)
    // if (!this.auth.isAuthenticated()) {
    //   this.auth.logout();
    //  return;
    //}

    // 2. Bind View Events (Delegating event handling to controller methods)
    this._bindEvents();

    // 3. Load Initial Data
    await this.loadInitialData();
  }

  /**
   * Fetches courses from API and updates the UI.
   * Maps to 'loadInitialData' in panel.js
   */
  async loadInitialData() {
    try {
      // Show loading state (optional, can be handled by view)
      const courses = await this.api.getCourses();

      this.state.courses = courses || [];

      // Extract unique departments and semesters for filters
      const departments = [
        ...new Set(this.state.courses.map((c) => c.department).filter(Boolean)),
      ];
      const semesters = [
        ...new Set(this.state.courses.map((c) => c.semester).filter(Boolean)),
      ].sort();

      // Update View
      this.view.populateFilters(departments, semesters);
      this._refreshCourseList();
      this._updateSummary();
    } catch (error) {
      console.error(error);
      alert(error.message || "Error loading data.");
    }
  }

  /**
   * Filters courses based on search query and dropdowns.
   * Maps to 'getFilteredCourses' in panel.js
   * @returns {Array} Filtered list of courses
   * @private
   */
  _getFilteredCourses() {
    let filtered = [...this.state.courses];

    // Filter by Search Query
    if (this.state.searchQuery) {
      const query = this.state.searchQuery.toLowerCase();
      filtered = filtered.filter(
        (c) =>
          c.name.toLowerCase().includes(query) ||
          c.code.toLowerCase().includes(query) ||
          c.department.toLowerCase().includes(query)
      );
    }

    // Filter by Department
    if (this.state.filterDepartment) {
      filtered = filtered.filter(
        (c) => c.department === this.state.filterDepartment
      );
    }

    // Filter by Semester
    if (this.state.filterSemester) {
      filtered = filtered.filter(
        (c) => c.semester === this.state.filterSemester
      );
    }

    return filtered;
  }

  /**
   * Refreshes the course table in the UI based on current filters.
   * @private
   */
  _refreshCourseList() {
    const filteredCourses = this._getFilteredCourses();
    this.view.renderCourses(filteredCourses);
  }

  /**
   * Updates the statistics summary cards.
   * Maps to 'updateSummary' in panel.js
   * @private
   */
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

  /**
   * Binds DOM events from the View to Controller handlers.
   * @private
   */
  _bindEvents() {
    // Search & Filter
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

    // Modal Actions
    this.view.bindAddCourseBtn(() => this._handleAddCourseClick());
    this.view.bindCancelCourseBtn(() => this.view.closeCourseModal());

    // Form Submission
    this.view.bindCourseFormSubmit((formData) =>
      this._handleFormSubmit(formData)
    );

    // Table Actions (Edit/Delete)
    this.view.bindTableActions(
      (id) => this._handleEditCourseClick(id), // onEdit
      (id) => this._handleDeleteCourseClick(id) // onDelete
    );

    // Modal Close Buttons
    this.view.bindModalCloseBtns((modal) => {
      this.view.closeModal(modal);
      this.view.resetForm();
    });

    // Navigation
    this.view.bindNavLinks((targetId) => {
      localStorage.setItem("activeAdminSection", targetId);
      this.view.setActiveSection(targetId);
    });

    // Logout
    this.view.bindLogout(() => this.auth.logout());



    // Set Active Section
    const activeSection =
      localStorage.getItem("activeAdminSection") || "course-management";
    this.view.setActiveSection(activeSection);
  }

  // ============================================================
  // Event Handlers (Business Logic)
  // ============================================================

  /**
   * Prepares the UI for adding a new course.
   */
  _handleAddCourseClick() {
    this.state.currentEditId = null;
    this.view.resetForm();
    this.view.setModalTitle("افزودن درس جدید");
    this.view.clearValidationErrors();
    this.view.openCourseModal();
  }

  /**
   * Prepares the UI for editing an existing course.
   * @param {number|string} id - Course ID
   */
  _handleEditCourseClick(id) {
    const course = this.state.courses.find((c) => c.id === id);
    if (!course) return;

    this.state.currentEditId = id;
    this.view.fillForm(course);
    this.view.setModalTitle("ویرایش درس");
    this.view.clearValidationErrors();
    this.view.openCourseModal();
  }

  /**
   * Handles course deletion logic.
   * @param {number|string} id - Course ID
   */
  _handleDeleteCourseClick(id) {
    const course = this.state.courses.find((c) => c.id === id);
    if (!course) return;

    this.view.showConfirmation(
      `آیا از حذف درس "${course.name}" (${course.code}) مطمئن هستید؟`,
      async () => {
        try {
          await this.api.deleteCourse(id);
          // Reload data
          await this.loadInitialData();
        } catch (error) {
          alert(error.message);
        }
      }
    );
  }

  /**
   * Handles the form submission for both Add and Update operations.
   * @param {Object} formData - Raw data from the form
   */
  async _handleFormSubmit(formData) {
    // 1. Validation
    this.view.clearValidationErrors();

    // Pass existing courses to validator to check for duplicate codes
    const validationResult = this.validator.validate(
      formData,
      this.state.courses,
      this.state.currentEditId
    );

    if (!validationResult.isValid) {
      this.view.showValidationErrors(validationResult.errors);
      return;
    }

    // 2. API Call
    this.view.setFormSubmitting(true); // Disable button, show spinner

    try {
      if (this.state.currentEditId) {
        // Update
        await this.api.updateCourse(this.state.currentEditId, formData);
      } else {
        // Create
        await this.api.addCourse(formData);
      }

      // 3. Success Handling
      this.view.resetForm();
      this.view.closeCourseModal();
      this.state.currentEditId = null;

      await this.loadInitialData(); // Reload list
      alert("درس با موفقیت ذخیره شد.");
    } catch (error) {
      console.error(error);
      alert(`خطا: ${error.message}`);
    } finally {
      this.view.setFormSubmitting(false); // Re-enable button
    }
  }
}
