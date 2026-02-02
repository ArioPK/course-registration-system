/**
 * js/controllers/student-course.controller.js
 * Responsibility: Fetch data, Handle Filtering, Manage Enrollments, Check Unit Limits.
 */
export class StudentCourseController {
  constructor(apiService, authService, view) {
    this.api = apiService;
    this.auth = authService;
    this.view = view;

    // State Management
    this.state = {
      allCourses: [],
      prerequisites: [],
      myEnrollments: [],
      unitConfig: { min_units: 12, max_units: 20 },
      searchQuery: "",
      filterType: "course_mix",
    };

    this.myEnrollmentsBtn = document.getElementById("my-enrollments-btn");
    this.backFromEnrollmentsBtn = document.getElementById(
      "back-from-enrollments-btn"
    );
  }

  async init() {
    // 1. Auth Guard
    if (!this.auth.isAuthenticated()) {
      this.auth.logout();
      return;
    }

    this._bindEvents();
    await this.loadData();
  }

  _bindEvents() {
    // 1. Logout
    if (this.view.bindLogout) {
      this.view.bindLogout(() => this.auth.logout());
    }

    if (this.view.bindSearch) {
      this.view.bindSearch(
        this._debounce((query) => {
          this.state.searchQuery = query;
          this._filterAndRender();
        }, 300)
      );
    }

    if (this.view.bindFilterType) {
      this.view.bindFilterType((type) => {
        this.state.filterType = type;
        this._filterAndRender();
      });
    }

    if (this.myEnrollmentsBtn) {
      this.myEnrollmentsBtn.addEventListener("click", () =>
        this.showMyEnrollments()
      );
    }
    if (this.backFromEnrollmentsBtn) {
      this.backFromEnrollmentsBtn.addEventListener("click", () =>
        this.showCatalog()
      );
    }
  }

  async loadData() {
    if (this.view.showLoading) {
      this.view.showLoading(true);
    } else if (this.view.setLoading) {
      this.view.setLoading(true);
    }
    try {
      // Load data with individual error handling to prevent one failure from breaking everything
      let courses = [];
      let prerequisites = [];
      let enrollments = [];
      let config = null;

      try {
        // Use student-specific endpoint
        courses = await this.api.getStudentCourses();
        console.log("Courses loaded:", courses);
      } catch (error) {
        console.error("Error loading courses:", error);
        // Continue with empty array
      }

      try {
        prerequisites = await this.api.getPrerequisites();
        console.log("Prerequisites loaded:", prerequisites);
      } catch (error) {
        console.error("Error loading prerequisites:", error);
        // Continue with empty array
      }

      try {
        enrollments = await this.api.getMyEnrollments();
        console.log("Enrollments loaded:", enrollments);
      } catch (error) {
        console.error("Error loading enrollments:", error);
        // Continue with empty array
      }

      try {
        config = await this.api.getUnitConfiguration();
        console.log("Unit config loaded:", config);
      } catch (error) {
        console.error("Error loading unit config:", error);
        // Continue with default config
      }

      // Ensure courses is an array
      const coursesArray = Array.isArray(courses) ? courses : [];
      const prerequisitesArray = Array.isArray(prerequisites) ? prerequisites : [];
      const enrollmentsArray = Array.isArray(enrollments) ? enrollments : [];

      // Use current term - backend uses 1404-1 by default
      // This should match backend's CURRENT_TERM setting
      const currentSemester = "1404-1";
      this.state.allCourses = coursesArray.filter(
        (c) => c && c.semester === currentSemester
      );

      this.state.prerequisites = prerequisitesArray;
      this.state.myEnrollments = enrollmentsArray;

      if (config) {
        this.state.unitConfig = config;
      }

      // Only show error if courses failed to load
      if (coursesArray.length === 0 && !this.api.USE_MOCK) {
        this.view.showError("خطا در دریافت لیست دروس. لطفاً اتصال خود را بررسی کنید.");
      } else {
        this._filterAndRender();
      }
    } catch (error) {
      console.error("StudentController Error:", error);
      const errorMessage = error?.message || "خطا در دریافت اطلاعات. لطفاً اتصال خود را بررسی کنید.";
      this.view.showError(errorMessage);
    } finally {
      if (this.view.showLoading) {
        this.view.showLoading(false);
      } else if (this.view.setLoading) {
        this.view.setLoading(false);
      }
    }
  }

  _filterAndRender() {
    const { allCourses, searchQuery, filterType, myEnrollments, prerequisites } = this.state;
    let filteredCourses = allCourses;

    if (searchQuery) {
      const query = searchQuery.toLowerCase().trim();
      filteredCourses = allCourses.filter((course) => {
        if (filterType === "course_mix") {
          const nameMatch = course.name && course.name.toLowerCase().includes(query);
          const codeMatch = course.code && course.code.toLowerCase().includes(query);
          return nameMatch || codeMatch;
        } else {
          const valueToCheck = course[filterType] ? String(course[filterType]).toLowerCase() : "";
          return valueToCheck.includes(query);
        }
      });
    }

    const enrolledIds = new Set((myEnrollments || []).map((e) => e.course?.id).filter(Boolean));
    const prereqList = Array.isArray(prerequisites) ? prerequisites : [];

    // Pass parameters in correct order: courses, prerequisites, onEnrollClick, enrolledIdsSet
    this.view.renderCourses(
      filteredCourses,
      prerequisites || [], 
      (courseId) => this.handleEnroll(courseId), 
      enrolledIds 
    );
  }
  showMyEnrollments() {
    const { myEnrollments, unitConfig } = this.state;

    const totalUnits = myEnrollments.reduce(
      (sum, item) => sum + (item.course.units || 0),
      0
    );

    this.view.renderEnrollments(
      myEnrollments,
      totalUnits,
      (courseId) => this.handleDrop(courseId),
      unitConfig
    );

    this.view.toggleSection("enrollments");
  }

  showCatalog() {
    this.view.toggleSection("catalog");
  }

  async handleEnroll(courseId) {
    const course = this.state.allCourses.find((c) => c.id === courseId);
    if (!course) return;

    const currentUnits = this.state.myEnrollments.reduce(
      (sum, item) => sum + (item.course.units || 0),
      0
    );
    const maxUnits = this.state.unitConfig.max_units;

    if (currentUnits + course.units > maxUnits) {
      this.view.showError(
        `خطا: اخذ این درس باعث عبور از سقف مجاز (${maxUnits} واحد) می‌شود.`
      );
      return;
    }

    if (!confirm(`آیا از اخذ درس "${course.name}" اطمینان دارید؟`)) return;

    if (this.view.showLoading) {
      this.view.showLoading(true);
    } else if (this.view.setLoading) {
      this.view.setLoading(true);
    }
    try {
      await this.api.enrollCourse(courseId);
      await this.loadData();
    } catch (error) {
      let msg = error.message || "خطا در ثبت‌نام درس.";
      if (msg.includes("409"))
        msg = "تداخل زمانی، تکراری بودن درس یا محدودیت واحد.";
      this.view.showError(msg);
    } finally {
      if (this.view.showLoading) {
        this.view.showLoading(false);
      } else if (this.view.setLoading) {
        this.view.setLoading(false);
      }
    }
  }

  async handleDrop(courseId) {
    // 1. پیدا کردن درس در لیست ثبت‌نامی‌ها
    const enrollment = this.state.myEnrollments.find(
      (e) => e.course.id === courseId
    );
    if (!enrollment) return;

    const courseUnits = enrollment.course.units;
    const currentUnits = this.state.myEnrollments.reduce(
      (sum, item) => sum + (item.course.units || 0),
      0
    );
    const minUnits = this.state.unitConfig.min_units;

    if (currentUnits - courseUnits < minUnits) {
      this.view.showError(
        `خطا: حذف این درس باعث می‌شود مجموع واحدها کمتر از حد مجاز (${minUnits} واحد) شود.`
      );
      return;
    }

    if (!confirm("آیا از حذف این درس اطمینان دارید؟")) return;

    if (this.view.showLoading) {
      this.view.showLoading(true);
    } else if (this.view.setLoading) {
      this.view.setLoading(true);
    }
    try {
      await this.api.dropCourse(courseId);

      // آپدیت State و رفرش
      this.state.myEnrollments = this.state.myEnrollments.filter(
        (e) => e.course.id !== courseId
      );

      this.showMyEnrollments();
      this._filterAndRender();
    } catch (error) {
      let msg = error.message || "خطا در حذف درس.";
      if (msg.includes("409")) msg = "رعایت حداقل واحد الزامی است.";
      this.view.showError(msg);
    } finally {
      if (this.view.showLoading) {
        this.view.showLoading(false);
      } else if (this.view.setLoading) {
        this.view.setLoading(false);
      }
    }
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
