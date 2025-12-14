/**
 * js/controllers/admin-course.controller.js
 */
export class AdminCourseController {
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
      this._bindEvents();
      await this.loadCourses();
    }
  
    async loadCourses() {
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
        this.view.notifier.showError("خطا در بارگیری لیست دروس.");
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
  
      this.view.bindFilters(
        (dept) => {
          this.state.filterDepartment = dept;
          this._refreshCourseList();
        },
        (sem) => {
          this.state.filterSemester = sem;
          this._refreshCourseList();
        }
      );
  
      this.view.bindAddCourse(() => this._handleAddCourseClick());
      this.view.bindCancel(() => this.view.closeModal());
      this.view.bindSubmit((formData) => this._handleFormSubmit(formData));
  
      this.view.bindTableActions(
        (id) => this._handleEditCourseClick(id),
        (id) => this._handleDeleteCourseClick(id)
      );
    }
  
    _handleAddCourseClick() {
      this.state.currentEditId = null;
      this.view.resetForm();
      this.view.openModal("افزودن درس جدید");
      this.view.notifier.clearValidationErrors(this.view.elements.form);
    }
  
    _handleEditCourseClick(id) {
      const course = this.state.courses.find((c) => c.id === id);
      if (!course) return;
  
      this.state.currentEditId = id;
      this.view.fillForm(course);
      this.view.openModal("ویرایش درس");
      this.view.notifier.clearValidationErrors(this.view.elements.form);
    }
  
    _handleDeleteCourseClick(id) {
      const course = this.state.courses.find((c) => c.id === id);
      if (!course) return;
  
      this.view.notifier.showConfirmation(
        `آیا از حذف درس "${course.name}" (${course.code}) مطمئن هستید؟`,
        async () => {
          try {
            await this.api.deleteCourse(id);
            this.view.notifier.showSuccess("درس با موفقیت حذف شد.");
            await this.loadCourses(); // Reload data
          } catch (error) {
            this.view.notifier.showError(error.message);
          }
        }
      );
    }
  
    async _handleFormSubmit(formData) {
      this.view.notifier.clearValidationErrors(this.view.elements.form);
  
      const validationResult = this.validator.validate(
        formData,
        this.state.courses,
        this.state.currentEditId
      );
  
      if (!validationResult.isValid) {
        this.view.notifier.showValidationErrors(validationResult.errors);
        return;
      }
  
      this.view.setFormSubmitting(true);
  
      try {
        if (this.state.currentEditId) {
          await this.api.updateCourse(this.state.currentEditId, formData);
        } else {
          await this.api.addCourse(formData);
        }
  
        this.view.closeModal();
        this.state.currentEditId = null;
        await this.loadCourses(); // Reload data
        this.view.notifier.showSuccess("درس با موفقیت ذخیره شد.");
      } catch (error) {
        console.error(error);
        this.view.notifier.showError(`خطا: ${error.message}`);
      } finally {
        this.view.setFormSubmitting(false);
      }
    }
  }