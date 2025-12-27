/**
 * js/controllers/student-course.controller.js
 * Responsibility: Fetch data and coordinate between API and View.
 */
export class StudentCourseController {
    constructor(apiService, authService, view) {
      this.api = apiService;
      this.auth = authService;
      this.view = view;
  
      // State Management for Filtering
      this.state = {
        allCourses: [],
        prerequisites: [],
        searchQuery: "",
        filterType: "course_mix", 
      };
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
  
      this.view.bindSearch(
        this._debounce((query) => {
          this.state.searchQuery = query;
          this._filterAndRender();
        }, 300)
      );
  
      this.view.bindFilterType((type) => {
        this.state.filterType = type;
        // optional
        // this.view.updateSearchPlaceholder(type); 
        this._filterAndRender();
      });
    }
  
    async loadCourses() {
      this.view.setLoading(true);
      try {
        const [courses, prerequisites] = await Promise.all([
          this.api.getCourses(),
          this.api.getPrerequisites(),
        ]);
  
        const currentSemester = "1403-1";
  
        this.state.allCourses = courses.filter(
          (c) => c.semester === currentSemester
        );
        this.state.prerequisites = prerequisites;
  
        this._filterAndRender();
      } catch (error) {
        console.error("StudentController Error:", error);
        this.view.showError(
          "خطا در دریافت لیست دروس. لطفاً اتصال خود را بررسی کنید."
        );
      } finally {
        this.view.setLoading(false);
      }
    }
  
    _filterAndRender() {
      const { allCourses, prerequisites, searchQuery, filterType } = this.state;
      let filteredCourses = allCourses;
  
      if (searchQuery) {
        const query = searchQuery.toLowerCase().trim();
  
        filteredCourses = allCourses.filter((course) => {
         
          if (filterType === "course_mix") {
            const nameMatch = course.name && course.name.toLowerCase().includes(query);
            const codeMatch = course.code && course.code.toLowerCase().includes(query);
            return nameMatch || codeMatch;
          } 
        
          else {
            const valueToCheck = course[filterType]
              ? String(course[filterType]).toLowerCase()
              : "";
            return valueToCheck.includes(query);
          }
        });
      }
  
      this.view.renderCourses(filteredCourses, prerequisites);
    }
  
    _debounce(func, wait) {
      let timeout;
      return function (...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
      };
    }
  }