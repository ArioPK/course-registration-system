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
          const courses = await this.api.getCourses();
          this.data.courses = courses;
          
          // Extract unique departments and semesters
          this.data.departments = [...new Set(courses.map(c => c.department))];
          this.data.semesters = [...new Set(courses.map(c => c.semester))];
          
          // Populate filter dropdowns
          this.populateFilters();
        } catch (error) {
          console.error("Failed to load initial data:", error);
          alert("خطا در بارگذاری اطلاعات اولیه.");
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
          
          const formData = {
            code: AdminCourseApp.elements.courseCode.value.trim(),
            name: AdminCourseApp.elements.courseName.value.trim(),
            units: parseInt(AdminCourseApp.elements.courseUnits.value),
            department: AdminCourseApp.elements.courseDepartment.value.trim(),
            semester: AdminCourseApp.elements.courseSemester.value.trim(),
            capacity: parseInt(AdminCourseApp.elements.courseCapacity.value),
          };

          // Validation
          if (!formData.code || !formData.name || !formData.units || !formData.department || !formData.semester || !formData.capacity) {
            alert("لطفاً تمام فیلدها را پر کنید.");
            return;
          }

          if (formData.units < 1 || formData.units > 6) {
            alert("تعداد واحد باید بین 1 تا 6 باشد.");
            return;
          }

          if (formData.capacity < 1) {
            alert("ظرفیت باید بیشتر از 0 باشد.");
            return;
          }

          try {
            if (AdminCourseApp.state.currentEditId) {
              // Update existing course
              await AdminCourseApp.api.updateCourse(AdminCourseApp.state.currentEditId, formData);
            } else {
              // Add new course
              await AdminCourseApp.api.addCourse(formData);
            }
            
            await AdminCourseApp.loadInitialData();
            AdminCourseApp.renderAll();
            AdminCourseApp.updateSummary();
            AdminCourseApp.ui.closeModal(AdminCourseApp.elements.courseModal);
          } catch (error) {
            console.error("Failed to save course:", error);
            alert("خطا در ذخیره‌سازی درس.");
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
        closeModal: (modal) => modal.classList.remove("active"),
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
      // SECTION 6: API SIMULATION
      //==================================================================
      api: {
        // Mock database
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

        async getCourses() {
          console.log("API: Fetching courses...");
          await this._delay(300);
          return structuredClone(this._mockDB.courses);
        },

        async addCourse(courseData) {
          console.log("API: Adding course...", courseData);
          await this._delay(500);
          const newId = Math.max(0, ...this._mockDB.courses.map(c => c.id)) + 1;
          const newCourse = {
            id: newId,
            ...courseData,
            enrolled: 0, // New courses start with 0 enrollments
          };
          this._mockDB.courses.push(newCourse);
          return newCourse;
        },

        async updateCourse(id, courseData) {
          console.log("API: Updating course:", id, courseData);
          await this._delay(500);
          const course = this._mockDB.courses.find(c => c.id === id);
          if (course) {
            // Preserve enrolled count when updating
            const enrolled = course.enrolled;
            Object.assign(course, courseData);
            course.enrolled = enrolled; // Keep existing enrollment
          }
          return course;
        },

        async deleteCourse(id) {
          console.log("API: Deleting course:", id);
          await this._delay(300);
          this._mockDB.courses = this._mockDB.courses.filter(c => c.id !== id);
          return { success: true };
        },
      },
    };

    // Start the application
    AdminCourseApp.init();
    }
  });
