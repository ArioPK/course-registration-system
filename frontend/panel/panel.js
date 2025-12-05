//==================================================================
  // ADMIN COURSE MANAGEMENT SYSTEM
  //==================================================================

  document.addEventListener("DOMContentLoaded", () => {
    const adminPanel = document.querySelector(".admin-container");
    if (adminPanel) {
      // Auth Guard: If not logged in, redirect to the login page.
      if (sessionStorage.getItem("isAdminLoggedIn") !== "true") {
        window.location.href = "../Login/index.html";
        return;
      }

    const AdminCourseApp = {
      // --- API Configuration ---
      API_CONFIG: {
        // Set to true to use mock API (for development)
        // Set to false to use real API endpoint
        USE_MOCK: false, // Set to false when backend is ready
        // Your actual API base URL
        BASE_URL: "http://localhost:8000", // Change this to your backend URL
        // API endpoints
        ENDPOINTS: {
          COURSES: "/api/courses",
          COURSE_BY_ID: (id) => `/api/courses/${id}`,
        },
        // Request timeout in milliseconds
        TIMEOUT: 10000,
      },

      // --- App State & Elements ---
      elements: {},
      state: {
        currentEditId: null,
        searchQuery: "",
        filterDepartment: "",
        filterSemester: "",
      },
      data: {
        courses: [], // All courses
        departments: [], // Available departments
        semesters: [], // Available semesters
      },

      /**
       * The starting point for the application.
       */
      async init() {
        this.cacheElements();
        this.bindEvents();
        await this.loadInitialData();
        this.applyState();
        this.renderAll();
        this.updateSummary();
      },

      //==================================================================
      // SECTION 1: SETUP & INITIALIZATION
      //==================================================================

      /**
       * Finds and caches all necessary DOM elements.
       */
      cacheElements() {
        this.elements = {
          navLinks: document.querySelectorAll(".nav-link"),
          sections: document.querySelectorAll(".management-section"),
          coursesTableBody: document.getElementById("courses-table-body"),
          courseSearch: document.getElementById("course-search"),
          filterDepartment: document.getElementById("filter-department"),
          filterSemester: document.getElementById("filter-semester"),
          addCourseBtn: document.getElementById("add-course-btn"),
          courseModal: document.getElementById("course-modal"),
          courseForm: document.getElementById("course-form"),
          courseModalTitle: document.getElementById("course-modal-title"),
          courseCode: document.getElementById("course-code"),
          courseName: document.getElementById("course-name"),
          courseUnits: document.getElementById("course-units"),
          courseDepartment: document.getElementById("course-department"),
          courseSemester: document.getElementById("course-semester"),
          courseCapacity: document.getElementById("course-capacity"),
          cancelCourseBtn: document.getElementById("cancel-course-btn"),
          confirmationModal: document.getElementById("confirmation-modal"),
          totalCourses: document.getElementById("total-courses"),
          totalCapacity: document.getElementById("total-capacity"),
          totalEnrolled: document.getElementById("total-enrolled"),
          logoutBtn: document.getElementById("logout-btn"),
        };
      },

      /**
       * Fetches all required data from the API.
       */
      async loadInitialData() {
        try {
          console.log("Loading initial course data...");
          const courses = await this.api.getCourses();
          
          // Ensure courses is an array
          if (!Array.isArray(courses)) {
            console.error("Invalid courses data format:", courses);
            this.data.courses = [];
            alert("خطا: فرمت داده دریافتی از سرور نامعتبر است.");
            return;
          }
          
          this.data.courses = courses;
          console.log(`Loaded ${courses.length} courses from API`);
          
          // Extract unique departments and semesters
          this.data.departments = [...new Set(courses.map(c => c.department).filter(Boolean))];
          this.data.semesters = [...new Set(courses.map(c => c.semester).filter(Boolean))];
          
          // Populate filter dropdowns
          this.populateFilters();
        } catch (error) {
          console.error("Failed to load initial data:", error);
          const errorMessage = error.message || "خطا در بارگذاری اطلاعات اولیه.";
          alert(errorMessage);
          // Set empty data to prevent further errors
          this.data.courses = [];
          this.data.departments = [];
          this.data.semesters = [];
        }
      },

      /**
       * Populates filter dropdowns with available options.
       */
      populateFilters() {
        // Clear existing options (except first one)
        while (this.elements.filterDepartment.children.length > 1) {
          this.elements.filterDepartment.removeChild(this.elements.filterDepartment.lastChild);
        }
        while (this.elements.filterSemester.children.length > 1) {
          this.elements.filterSemester.removeChild(this.elements.filterSemester.lastChild);
        }

        // Populate department filter
        this.data.departments.forEach(dept => {
          const option = document.createElement("option");
          option.value = dept;
          option.textContent = dept;
          this.elements.filterDepartment.appendChild(option);
        });

        // Populate semester filter
        this.data.semesters.sort().forEach(sem => {
          const option = document.createElement("option");
          option.value = sem;
          option.textContent = sem;
          this.elements.filterSemester.appendChild(option);
        });
      },

      /**
       * Retrieves and applies the active state from LocalStorage.
       */
      applyState() {
        const activeSectionId = localStorage.getItem("activeAdminSection") || "course-management";
        this.elements.navLinks.forEach((link) =>
          link.classList.toggle("active", link.dataset.target === activeSectionId)
        );
        this.elements.sections.forEach((section) =>
          section.classList.toggle("active", section.id === activeSectionId)
        );
      },

      //==================================================================
      // SECTION 2: UI RENDERING
      //==================================================================

      /**
       * Renders all data tables.
       */
      renderAll() {
        this.render.courses();
      },

      render: {
        /**
         * Builds and displays the HTML for courses table.
         */
        courses() {
          const tbody = AdminCourseApp.elements.coursesTableBody;
          tbody.innerHTML = "";

          const filteredCourses = AdminCourseApp.getFilteredCourses();

          if (filteredCourses.length === 0) {
            tbody.innerHTML = `
              <tr>
                <td colspan="8" style="text-align: center; padding: 40px; color: var(--medium-grey);">
                  درسی یافت نشد
                </td>
              </tr>
            `;
            return;
          }

          filteredCourses.forEach((course) => {
            const capacityPercent = (course.enrolled / course.capacity) * 100;
            const isFull = course.enrolled >= course.capacity;
            
            tbody.innerHTML += `
              <tr class="${isFull ? 'full-row' : ''}">
                <td>${course.code}</td>
                <td>${course.name}</td>
                <td>${course.units}</td>
                <td>${course.department}</td>
                <td>${course.semester}</td>
                <td>${course.capacity}</td>
                <td>
                  <span class="enrollment-info ${isFull ? 'full' : ''}">
                    ${course.enrolled} / ${course.capacity}
                    ${isFull ? '<span class="full-badge">تکمیل</span>' : ''}
                  </span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button class="action-btn edit-btn" data-id="${course.id}" title="ویرایش">
                      <i class="ri-pencil-fill"></i>
                    </button>
                    <button class="action-btn delete-btn" data-id="${course.id}" title="حذف">
                      <i class="ri-delete-bin-6-line"></i>
                    </button>
                  </div>
                </td>
              </tr>
            `;
          });
        },
      },

      /**
       * Gets filtered courses based on search and filters.
       */
      getFilteredCourses() {
        let filtered = [...this.data.courses];

        // Apply search filter
        if (this.state.searchQuery) {
          const query = this.state.searchQuery.toLowerCase();
          filtered = filtered.filter(course =>
            course.name.toLowerCase().includes(query) ||
            course.code.toLowerCase().includes(query) ||
            course.department.toLowerCase().includes(query)
          );
        }

        // Apply department filter
        if (this.state.filterDepartment) {
          filtered = filtered.filter(course => course.department === this.state.filterDepartment);
        }

        // Apply semester filter
        if (this.state.filterSemester) {
          filtered = filtered.filter(course => course.semester === this.state.filterSemester);
        }

        return filtered;
      },

      /**
       * Updates summary statistics.
       */
      updateSummary() {
        const totalCourses = this.data.courses.length;
        const totalCapacity = this.data.courses.reduce((sum, c) => sum + c.capacity, 0);
        const totalEnrolled = this.data.courses.reduce((sum, c) => sum + c.enrolled, 0);

        this.elements.totalCourses.textContent = totalCourses;
        this.elements.totalCapacity.textContent = totalCapacity;
        this.elements.totalEnrolled.textContent = totalEnrolled;
      },

      //==================================================================
      // SECTION 3: EVENT BINDING
      //==================================================================

      /**
       * Attaches all necessary event listeners.
       */
      bindEvents() {
        // Navigation
        this.elements.navLinks.forEach((link) =>
          link.addEventListener("click", this.handlers.onNavClick)
        );

        // Search
        this.elements.courseSearch.addEventListener("input", (e) => {
          this.state.searchQuery = e.target.value;
          this.render.courses();
        });

        // Filters
        this.elements.filterDepartment.addEventListener("change", (e) => {
          this.state.filterDepartment = e.target.value;
          this.render.courses();
        });

        this.elements.filterSemester.addEventListener("change", (e) => {
          this.state.filterSemester = e.target.value;
          this.render.courses();
        });

        // Add course button
        this.elements.addCourseBtn.addEventListener("click", this.handlers.onAddCourseClick);

        // Course form submission
        this.elements.courseForm.addEventListener("submit", this.handlers.onCourseFormSubmit);

        // Cancel course button
        this.elements.cancelCourseBtn.addEventListener("click", () => {
          this.ui.closeModal(this.elements.courseModal);
        });

        // Modal close buttons
        document.querySelectorAll(".modal-close-btn").forEach(btn => {
          btn.addEventListener("click", (e) => {
            const modal = e.target.closest(".modal-backdrop");
            this.ui.closeModal(modal);
          });
        });

        // Course edit/delete (event delegation)
        document.body.addEventListener("click", this.handlers.onBodyClick);

        // Logout
        this.elements.logoutBtn.addEventListener("click", this.handlers.onLogoutClick);
      },

      //==================================================================
      // SECTION 4: EVENT HANDLERS
      //==================================================================

      handlers: {
        /**
         * Handles clicks on the main sidebar navigation.
         */
        onNavClick(e) {
          e.preventDefault();
          localStorage.setItem("activeAdminSection", e.currentTarget.dataset.target);
          AdminCourseApp.applyState();
        },

        /**
         * Uses event delegation to handle clicks on dynamically created buttons.
         */
        onBodyClick(e) {
          const editBtn = e.target.closest(".edit-btn");
          const deleteBtn = e.target.closest(".delete-btn");

          if (editBtn) {
            const courseId = parseInt(editBtn.dataset.id);
            AdminCourseApp.handlers.onEditCourse(courseId);
          } else if (deleteBtn) {
            const courseId = parseInt(deleteBtn.dataset.id);
            AdminCourseApp.handlers.onDeleteCourse(courseId);
          }
        },

        /**
         * Opens the course modal in "add" mode.
         */
        onAddCourseClick() {
          AdminCourseApp.state.currentEditId = null;
          AdminCourseApp.elements.courseForm.reset();
          AdminCourseApp.elements.courseModalTitle.textContent = "افزودن درس جدید";
          
          // Clear any previous validation errors
          AdminCourseApp.ui.clearFormValidation();
          
          AdminCourseApp.ui.openModal(AdminCourseApp.elements.courseModal);
        },

        /**
         * Opens the course modal in "edit" mode.
         */
        onEditCourse(courseId) {
          const course = AdminCourseApp.data.courses.find(c => c.id === courseId);
          if (!course) return;

          AdminCourseApp.state.currentEditId = courseId;
          AdminCourseApp.elements.courseCode.value = course.code;
          AdminCourseApp.elements.courseName.value = course.name;
          AdminCourseApp.elements.courseUnits.value = course.units;
          AdminCourseApp.elements.courseDepartment.value = course.department;
          AdminCourseApp.elements.courseSemester.value = course.semester;
          AdminCourseApp.elements.courseCapacity.value = course.capacity;
          AdminCourseApp.elements.courseModalTitle.textContent = "ویرایش درس";
          AdminCourseApp.ui.openModal(AdminCourseApp.elements.courseModal);
        },

        /**
         * Handles course deletion.
         */
        onDeleteCourse(courseId) {
          const course = AdminCourseApp.data.courses.find(c => c.id === courseId);
          if (!course) return;

          const message = `آیا از حذف درس "${course.name}" (${course.code}) مطمئن هستید؟`;
          
          AdminCourseApp.ui.showConfirmation(message, async () => {
            try {
              await AdminCourseApp.api.deleteCourse(courseId);
              await AdminCourseApp.loadInitialData();
              AdminCourseApp.renderAll();
              AdminCourseApp.updateSummary();
            } catch (error) {
              console.error("Failed to delete course:", error);
              alert("خطا در حذف درس.");
            }
          });
        },

        /**
         * Handles course form submission.
         */
        async onCourseFormSubmit(e) {
          e.preventDefault();
          
          // Clear previous validation errors
          AdminCourseApp.ui.clearFormValidation();
          
          // Get form values
          const formData = {
            code: AdminCourseApp.elements.courseCode.value.trim(),
            name: AdminCourseApp.elements.courseName.value.trim(),
            units: parseInt(AdminCourseApp.elements.courseUnits.value),
            department: AdminCourseApp.elements.courseDepartment.value.trim(),
            semester: AdminCourseApp.elements.courseSemester.value.trim(),
            capacity: parseInt(AdminCourseApp.elements.courseCapacity.value),
          };

          // Comprehensive validation with field-level error messages
          const validationErrors = AdminCourseApp.ui.validateForm(formData);
          
          if (validationErrors.length > 0) {
            console.log("Validation errors:", validationErrors);
            AdminCourseApp.ui.showFormValidationErrors(validationErrors);
            return;
          }
          
          console.log("Form validation passed. Submitting...", formData);

          // Disable submit button to prevent double submission
          const submitButton = AdminCourseApp.elements.courseForm.querySelector('button[type="submit"]');
          const originalButtonText = submitButton.textContent;
          submitButton.disabled = true;
          submitButton.textContent = "در حال ذخیره...";

          try {
            let result;
            if (AdminCourseApp.state.currentEditId) {
              // Update existing course
              console.log("Updating course:", AdminCourseApp.state.currentEditId, formData);
              result = await AdminCourseApp.api.updateCourse(AdminCourseApp.state.currentEditId, formData);
            } else {
              // Add new course
              console.log("Adding new course:", formData);
              result = await AdminCourseApp.api.addCourse(formData);
            }
            
            console.log("Course saved successfully:", result);
            
            // Clear form and close modal
            AdminCourseApp.elements.courseForm.reset();
            AdminCourseApp.state.currentEditId = null;
            AdminCourseApp.ui.closeModal(AdminCourseApp.elements.courseModal);
            
            // Reload data and refresh UI
            await AdminCourseApp.loadInitialData();
            AdminCourseApp.renderAll();
            AdminCourseApp.updateSummary();
            
            // Show success message
            alert("درس با موفقیت ذخیره شد.");
          } catch (error) {
            console.error("Failed to save course - Full error:", error);
            console.error("Error stack:", error.stack);
            const errorMessage = error.message || "خطا در ذخیره‌سازی درس.";
            alert(`خطا: ${errorMessage}\n\nلطفاً Console را بررسی کنید (F12)`);
          } finally {
            // Re-enable submit button
            submitButton.disabled = false;
            submitButton.textContent = originalButtonText;
          }
        },

        /**
         * Handles logout.
         */
        onLogoutClick(e) {
          e.preventDefault();
          sessionStorage.removeItem("isAdminLoggedIn");
          sessionStorage.removeItem("authToken");
          sessionStorage.removeItem("userData");
          window.location.href = "../Login/index.html";
        },
      },

      //==================================================================
      // SECTION 5: UI HELPERS
      //==================================================================
      ui: {
        openModal: (modal) => modal.classList.add("active"),
        closeModal: (modal) => {
          modal.classList.remove("active");
          // Clear form when closing modal
          if (modal.id === "course-modal") {
            AdminCourseApp.elements.courseForm.reset();
            AdminCourseApp.state.currentEditId = null;
            AdminCourseApp.ui.clearFormValidation();
          }
        },
        
        /**
         * Validates form data and returns array of errors
         */
        validateForm(formData) {
          const errors = [];
          
          // Code validation
          if (!formData.code) {
            errors.push({ field: "course-code", message: "کد درس الزامی است." });
          } else if (formData.code.length < 2) {
            errors.push({ field: "course-code", message: "کد درس باید حداقل 2 کاراکتر باشد." });
          } else if (!/^[A-Z0-9]+$/i.test(formData.code)) {
            errors.push({ field: "course-code", message: "کد درس فقط می‌تواند شامل حروف و اعداد باشد." });
          } else {
            // Check for duplicate course code (only if courses data is loaded)
            if (AdminCourseApp.data.courses && Array.isArray(AdminCourseApp.data.courses)) {
              const existingCourse = AdminCourseApp.data.courses.find(
                course => course && course.code && 
                         course.code.toLowerCase() === formData.code.toLowerCase() &&
                         course.id !== AdminCourseApp.state.currentEditId
              );
              if (existingCourse) {
                errors.push({ field: "course-code", message: `کد درس "${formData.code}" قبلاً استفاده شده است.` });
              }
            }
          }
          
          // Name validation
          if (!formData.name) {
            errors.push({ field: "course-name", message: "نام درس الزامی است." });
          } else if (formData.name.length < 3) {
            errors.push({ field: "course-name", message: "نام درس باید حداقل 3 کاراکتر باشد." });
          }
          
          // Units validation
          if (!formData.units || isNaN(formData.units)) {
            errors.push({ field: "course-units", message: "تعداد واحد الزامی است." });
          } else if (formData.units < 1 || formData.units > 6) {
            errors.push({ field: "course-units", message: "تعداد واحد باید بین 1 تا 6 باشد." });
          }
          
          // Department validation
          if (!formData.department) {
            errors.push({ field: "course-department", message: "رشته الزامی است." });
          } else if (formData.department.length < 2) {
            errors.push({ field: "course-department", message: "نام رشته باید حداقل 2 کاراکتر باشد." });
          }
          
          // Semester validation (more flexible format)
          if (!formData.semester) {
            errors.push({ field: "course-semester", message: "ترم الزامی است." });
          } else if (formData.semester.length < 3) {
            errors.push({ field: "course-semester", message: "فرمت ترم صحیح نیست. مثال: 1403-1" });
          }
          
          // Capacity validation
          if (!formData.capacity || isNaN(formData.capacity)) {
            errors.push({ field: "course-capacity", message: "ظرفیت الزامی است." });
          } else if (formData.capacity < 1) {
            errors.push({ field: "course-capacity", message: "ظرفیت باید بیشتر از 0 باشد." });
          } else if (formData.capacity > 1000) {
            errors.push({ field: "course-capacity", message: "ظرفیت نمی‌تواند بیشتر از 1000 باشد." });
          }
          
          return errors;
        },
        
        /**
         * Shows validation errors in the form
         */
        showFormValidationErrors(errors) {
          errors.forEach(error => {
            const field = document.getElementById(error.field);
            if (field) {
              field.classList.add("input-error");
              
              // Remove existing error message
              const formGroup = field.closest(".form-group");
              const existingError = formGroup.querySelector(".field-error");
              if (existingError) {
                existingError.remove();
              }
              
              // Add new error message
              const errorElement = document.createElement("span");
              errorElement.className = "field-error";
              errorElement.textContent = error.message;
              formGroup.appendChild(errorElement);
            }
          });
          
          // Focus on first error field
          if (errors.length > 0) {
            const firstErrorField = document.getElementById(errors[0].field);
            if (firstErrorField) {
              firstErrorField.focus();
            }
          }
        },
        
        /**
         * Clears all validation errors from the form
         */
        clearFormValidation() {
          const form = AdminCourseApp.elements.courseForm;
          const errorFields = form.querySelectorAll(".input-error");
          errorFields.forEach(field => field.classList.remove("input-error"));
          
          const errorMessages = form.querySelectorAll(".field-error");
          errorMessages.forEach(msg => msg.remove());
        },
        
        showConfirmation(message, onConfirm) {
          const confirmModal = AdminCourseApp.elements.confirmationModal;
          confirmModal.querySelector("#confirmation-message").textContent = message;
          this.openModal(confirmModal);

          const confirmBtn = confirmModal.querySelector("#confirm-btn");
          const cancelBtn = confirmModal.querySelector("#cancel-btn");

          // Clone and replace to remove old listeners
          const newConfirmBtn = confirmBtn.cloneNode(true);
          confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
          const newCancelBtn = cancelBtn.cloneNode(true);
          cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);

          const cleanup = () => {
            this.closeModal(confirmModal);
          };

          newConfirmBtn.addEventListener("click", () => {
            onConfirm();
            cleanup();
          });
          newCancelBtn.addEventListener("click", cleanup);
        },
      },

      //==================================================================
      // SECTION 6: API INTEGRATION
      //==================================================================
      api: {
        /**
         * Gets authentication token from sessionStorage
         */
        _getAuthToken() {
          return sessionStorage.getItem("authToken");
        },

        /**
         * Gets headers for API requests with authentication
         */
        _getHeaders() {
          const headers = {
            "Content-Type": "application/json",
          };
          const token = this._getAuthToken();
          if (token) {
            headers["Authorization"] = `Bearer ${token}`;
          }
          return headers;
        },

        /**
         * Makes HTTP request with error handling
         * Handles FastAPI error responses and standard HTTP errors
         */
        async _request(url, options = {}) {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), AdminCourseApp.API_CONFIG.TIMEOUT);

          try {
            const response = await fetch(url, {
              ...options,
              headers: {
                ...this._getHeaders(),
                ...options.headers,
              },
              signal: controller.signal,
            });

            clearTimeout(timeoutId);

            // Handle non-OK responses
            if (!response.ok) {
              let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
              
              try {
                const errorData = await response.json();
                // FastAPI typically returns errors in 'detail' field
                if (errorData.detail) {
                  errorMessage = Array.isArray(errorData.detail) 
                    ? errorData.detail.map(e => e.msg || e.message || JSON.stringify(e)).join(", ")
                    : errorData.detail;
                } else if (errorData.message) {
                  errorMessage = errorData.message;
                } else if (typeof errorData === 'string') {
                  errorMessage = errorData;
                }
              } catch (e) {
                // If response is not JSON, try to get text
                try {
                  const text = await response.text();
                  if (text) errorMessage = text;
                } catch (e2) {
                  // Keep default error message
                }
              }
              
              throw new Error(errorMessage);
            }

            // Handle empty responses (204 No Content)
            if (response.status === 204 || response.headers.get("content-length") === "0") {
              return { success: true };
            }

            // Parse JSON response
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
              return await response.json();
            } else {
              // If not JSON, return text
              const text = await response.text();
              return text ? JSON.parse(text) : { success: true };
            }
          } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === "AbortError") {
              throw new Error("Request timeout. Please try again.");
            }
            if (error.message) {
              throw error;
            }
            throw new Error(`Network error: ${error.message || "Unknown error"}`);
          }
        },

        // Mock database (for development/testing)
        _mockDB: {
          courses: [
            { id: 1, code: "CS101", name: "مبانی کامپیوتر", units: 3, department: "کامپیوتر", semester: "1403-1", capacity: 40, enrolled: 35 },
            { id: 2, code: "CS102", name: "برنامه‌نویسی مقدماتی", units: 3, department: "کامپیوتر", semester: "1403-1", capacity: 35, enrolled: 35 },
            { id: 3, code: "CS201", name: "ساختمان داده", units: 3, department: "کامپیوتر", semester: "1403-1", capacity: 30, enrolled: 25 },
            { id: 4, code: "CS301", name: "پایگاه داده", units: 3, department: "کامپیوتر", semester: "1403-1", capacity: 30, enrolled: 20 },
            { id: 5, code: "MATH101", name: "ریاضی عمومی 1", units: 3, department: "ریاضی", semester: "1403-1", capacity: 50, enrolled: 45 },
            { id: 6, code: "MATH102", name: "ریاضی عمومی 2", units: 3, department: "ریاضی", semester: "1403-1", capacity: 45, enrolled: 40 },
            { id: 7, code: "PHYS101", name: "فیزیک 1", units: 3, department: "فیزیک", semester: "1403-1", capacity: 40, enrolled: 30 },
            { id: 8, code: "ENG101", name: "زبان انگلیسی", units: 2, department: "زبان", semester: "1403-1", capacity: 60, enrolled: 55 },
            { id: 9, code: "CS401", name: "هوش مصنوعی", units: 3, department: "کامپیوتر", semester: "1403-2", capacity: 25, enrolled: 15 },
            { id: 10, code: "CS402", name: "شبکه‌های کامپیوتری", units: 3, department: "کامپیوتر", semester: "1403-2", capacity: 30, enrolled: 22 },
          ],
        },

        _delay: (ms) => new Promise((res) => setTimeout(res, ms)),

        /**
         * Fetches all courses from API
         * GET /api/courses
         * Expected response: Array of course objects or {courses: [...]} or {data: [...]}
         */
        async getCourses() {
          if (AdminCourseApp.API_CONFIG.USE_MOCK) {
            console.log("API: Fetching courses (MOCK)...");
            await this._delay(300);
            return structuredClone(this._mockDB.courses);
          }

          try {
            console.log("API: Fetching courses from backend...");
            const url = `${AdminCourseApp.API_CONFIG.BASE_URL}${AdminCourseApp.API_CONFIG.ENDPOINTS.COURSES}`;
            const response = await this._request(url, { method: "GET" });
            
            // Handle different response formats from FastAPI
            // FastAPI typically returns arrays directly or wrapped in objects
            if (response && typeof response === 'object') {
              if (Array.isArray(response)) {
                // Direct array response: [{...}, {...}]
                return response;
              } else if (response.courses && Array.isArray(response.courses)) {
                // Wrapped in 'courses': {courses: [...]}
                return response.courses;
              } else if (response.data && Array.isArray(response.data)) {
                // Wrapped in 'data': {data: [...]}
                return response.data;
              } else if (response.items && Array.isArray(response.items)) {
                // Wrapped in 'items': {items: [...]}
                return response.items;
              } else if (response.results && Array.isArray(response.results)) {
                // Paginated response: {results: [...]}
                return response.results;
              }
            }
            
            // If we get here, return empty array as fallback
            console.warn("Unexpected API response format:", response);
            return [];
          } catch (error) {
            console.error("Error fetching courses:", error);
            throw new Error(`Failed to fetch courses: ${error.message}`);
          }
        },

        /**
         * Adds a new course via API
         */
        async addCourse(courseData) {
          if (AdminCourseApp.API_CONFIG.USE_MOCK) {
            console.log("API: Adding course (MOCK)...", courseData);
            await this._delay(500);
            const newId = Math.max(0, ...this._mockDB.courses.map(c => c.id)) + 1;
            const newCourse = {
              id: newId,
              ...courseData,
              enrolled: 0,
            };
            this._mockDB.courses.push(newCourse);
            console.log("Course added to mock DB:", newCourse);
            return newCourse;
          }

          try {
            console.log("API: Adding course to backend...", courseData);
            const url = `${AdminCourseApp.API_CONFIG.BASE_URL}${AdminCourseApp.API_CONFIG.ENDPOINTS.COURSES}`;
            console.log("API URL:", url);
            console.log("Request body:", JSON.stringify(courseData));
            
            const response = await this._request(url, {
              method: "POST",
              body: JSON.stringify(courseData),
            });
            
            console.log("Course added successfully - Response:", response);
            
            // Handle different response formats
            if (response && typeof response === 'object') {
              // If response has a course object, return it
              if (response.course) return response.course;
              if (response.data) return response.data;
              // Otherwise return the response itself
              return response;
            }
            
            return response;
          } catch (error) {
            console.error("Error adding course - Full details:", {
              message: error.message,
              error: error,
              stack: error.stack
            });
            throw new Error(`Failed to add course: ${error.message}`);
          }
        },

        /**
         * Updates an existing course via API
         */
        async updateCourse(id, courseData) {
          if (AdminCourseApp.API_CONFIG.USE_MOCK) {
            console.log("API: Updating course (MOCK):", id, courseData);
            await this._delay(500);
            const course = this._mockDB.courses.find(c => c.id === id);
            if (course) {
              const enrolled = course.enrolled;
              Object.assign(course, courseData);
              course.enrolled = enrolled;
            }
            return course;
          }

          console.log("API: Updating course in backend:", id, courseData);
          const url = `${AdminCourseApp.API_CONFIG.BASE_URL}${AdminCourseApp.API_CONFIG.ENDPOINTS.COURSE_BY_ID(id)}`;
          return await this._request(url, {
            method: "PUT",
            body: JSON.stringify(courseData),
          });
        },

        /**
         * Deletes a course via API
         */
        async deleteCourse(id) {
          if (AdminCourseApp.API_CONFIG.USE_MOCK) {
            console.log("API: Deleting course (MOCK):", id);
            await this._delay(300);
            this._mockDB.courses = this._mockDB.courses.filter(c => c.id !== id);
            return { success: true };
          }

          console.log("API: Deleting course from backend:", id);
          const url = `${AdminCourseApp.API_CONFIG.BASE_URL}${AdminCourseApp.API_CONFIG.ENDPOINTS.COURSE_BY_ID(id)}`;
          return await this._request(url, {
            method: "DELETE",
          });
        },
      },
    };

    // Start the application
    AdminCourseApp.init();
    }
  });
