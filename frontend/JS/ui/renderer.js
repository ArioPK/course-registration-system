/**
 * js/ui/view.js
 * Responsibility: Manages the DOM, renders HTML, and binds UI events.
 * It extends NotificationService to inherit modal and alert capabilities.
 */

import { NotificationService } from "./notification.js";

export class CourseView extends NotificationService {
  constructor() {
    super(); // Initialize parent (NotificationService)

    // Cache DOM Elements (Extracted from panel.js 'cacheElements')
    this.elements = {
      // Form Inputs
      courseCode: document.getElementById("course-code"),
      courseName: document.getElementById("course-name"),
      courseUnits: document.getElementById("course-units"),
      courseDepartment: document.getElementById("course-department"),
      courseSemester: document.getElementById("course-semester"),
      courseCapacity: document.getElementById("course-capacity"),
      courseProfessor: document.getElementById("course-professor"),
      courseDay: document.getElementById("course-day"),
      courseStart: document.getElementById("course-start"),
      courseEnd: document.getElementById("course-end"),
      courseLocation: document.getElementById("course-location"),

      // Buttons & Interactive Elements
      addCourseBtn: document.getElementById("add-course-btn"),
      cancelCourseBtn: document.getElementById("cancel-course-btn"),
      logoutBtn: document.getElementById("logout-btn"),
      courseForm: document.getElementById("course-form"),
      courseSearch: document.getElementById("course-search"),
      filterDepartment: document.getElementById("filter-department"),
      filterSemester: document.getElementById("filter-semester"),

      // Display Containers
      coursesTableBody: document.getElementById("courses-table-body"),
      courseModal: document.getElementById("course-modal"),
      courseModalTitle: document.getElementById("course-modal-title"),

      // Summary Cards
      totalCourses: document.getElementById("total-courses"),
      totalCapacity: document.getElementById("total-capacity"),
      totalEnrolled: document.getElementById("total-enrolled"),

      // Modal Close Buttons
      modalCloseBtns: document.querySelectorAll(".modal-close-btn"),
      navLinks: document.querySelectorAll(".nav-link"),
      sections: document.querySelectorAll(".management-section"),
    };
  }

  // ============================================================
  // Rendering Methods
  // ============================================================

  /**
   * Bind click events for modal close buttons (x icons)
   */
  bindModalCloseBtns(handler) {
    this.elements.modalCloseBtns.forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const modal = e.target.closest(".modal-backdrop");
        handler(modal);
      });
    });
  }

  /**
   * Bind click events for sidebar navigation links
   */
  bindNavLinks(handler) {
    this.elements.navLinks.forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        const targetId = e.currentTarget.dataset.target;
        handler(targetId);
      });
    });
  }

  /**
   * Update UI to show the active section and active link
   */
  setActiveSection(targetId) {
    // Update nav links
    this.elements.navLinks.forEach((link) => {
      link.classList.toggle("active", link.dataset.target === targetId);
    });

    // Update sections
    this.elements.sections.forEach((section) => {
      section.classList.toggle("active", section.id === targetId);
    });
  }

  /**
   * Helper to translate day codes to Persian.
   * @param {string} day - Day code (e.g., 'SAT')
   * @returns {string} Persian day name
   */
  _translateDay(day) {
    const days = {
      SAT: "شنبه",
      SUN: "یک‌شنبه",
      MON: "دوشنبه",
      TUE: "سه‌شنبه",
      WED: "چهارشنبه",
      THU: "پنج‌شنبه",
      FRI: "جمعه",
    };
    return days[day] || day || "-";
  }

  /**
   * Renders the list of courses into the table.
   * Maps to 'render.courses' in panel.js
   * @param {Array} courses - List of course objects
   */
  renderCourses(courses) {
    const tbody = this.elements.coursesTableBody;
    tbody.innerHTML = "";

    if (!courses || courses.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="10" style="text-align: center; padding: 40px; color: var(--medium-grey);">
            درسی یافت نشد
          </td>
        </tr>
      `;
      return;
    }

    courses.forEach((course) => {
      const enrolled = course.enrolled || 0;
      // Handle potential undefined capacity to avoid division by zero
      const capacity = course.capacity || 1;
      const isFull = enrolled >= capacity;

      const row = document.createElement("tr");
      if (isFull) row.classList.add("full-row");

      row.innerHTML = `
        <td>${course.code}</td>
        <td>${course.name}</td>
        <td>${course.units || "-"}</td>
        <td>${course.department || "-"}</td>
        <td>${course.semester || "-"}</td>
        <td>${course.professor_name || "-"}</td>
        <td style="font-size: 0.85rem; direction: ltr; text-align: right;">
            ${this._translateDay(course.day_of_week)}<br>
            ${course.start_time || ""} - ${course.end_time || ""}
        </td>
        <td>${course.location || "-"}</td>
        <td>${course.capacity}</td>
        <td>
          <span class="enrollment-info ${isFull ? "full" : ""}">
            ${enrolled} / ${course.capacity}
            ${isFull ? '<span class="full-badge">تکمیل</span>' : ""}
          </span>
        </td>
        <td>
          <div class="action-buttons">
            <button class="action-btn edit-btn" data-id="${
              course.id
            }" title="ویرایش">
              <i class="ri-pencil-fill"></i>
            </button>
            <button class="action-btn delete-btn" data-id="${
              course.id
            }" title="حذف">
              <i class="ri-delete-bin-6-line"></i>
            </button>
          </div>
        </td>
      `;

      tbody.appendChild(row);
    });
  }

  /**
   * Populates the department and semester filter dropdowns.
   * Maps to 'populateFilters' in panel.js
   * @param {Array<string>} departments
   * @param {Array<string>} semesters
   */
  populateFilters(departments, semesters) {
    // Clear existing options (keep the first "All" option)
    const deptSelect = this.elements.filterDepartment;
    const semSelect = this.elements.filterSemester;

    // Helper to clear Select
    const clearSelect = (select) => {
      while (select.children.length > 1) {
        select.removeChild(select.lastChild);
      }
    };

    clearSelect(deptSelect);
    clearSelect(semSelect);

    departments.forEach((dept) => {
      const option = document.createElement("option");
      option.value = dept;
      option.textContent = dept;
      deptSelect.appendChild(option);
    });

    semesters.forEach((sem) => {
      const option = document.createElement("option");
      option.value = sem;
      option.textContent = sem;
      semSelect.appendChild(option);
    });
  }

  /**
   * Updates the summary statistics cards.
   * @param {Object} stats - { totalCourses, totalCapacity, totalEnrolled }
   */
  updateSummary(stats) {
    this.elements.totalCourses.textContent = stats.totalCourses;
    this.elements.totalCapacity.textContent = stats.totalCapacity;
    this.elements.totalEnrolled.textContent = stats.totalEnrolled;
  }

  // ============================================================
  // Form & Modal Manipulation
  // ============================================================

  openCourseModal() {
    this.openModal(this.elements.courseModal);
  }

  closeCourseModal() {
    this.closeModal(this.elements.courseModal);
    this.resetForm();
  }

  setModalTitle(title) {
    this.elements.courseModalTitle.textContent = title;
  }

  /**
   * Fills the form with course data for editing.
   * @param {Object} course
   */
  fillForm(course) {
    this.elements.courseCode.value = course.code;
    this.elements.courseName.value = course.name;
    this.elements.courseUnits.value = course.units;
    this.elements.courseDepartment.value = course.department;
    this.elements.courseSemester.value = course.semester;
    this.elements.courseCapacity.value = course.capacity;
    this.elements.courseProfessor.value = course.professor_name || "";
    this.elements.courseDay.value = course.day_of_week || "";
    // Ensure time format is HH:MM (remove seconds if present)
    this.elements.courseStart.value = this._formatTime(course.start_time);
    this.elements.courseEnd.value = this._formatTime(course.end_time);
    this.elements.courseLocation.value = course.location || "";
  }

  /**
   * Resets the form inputs.
   */
  resetForm() {
    this.elements.courseForm.reset();
  }

  /**
   * Toggles the submit button state (loading vs ready).
   * @param {boolean} isSubmitting
   */
  setFormSubmitting(isSubmitting) {
    const btn = this.elements.courseForm.querySelector('button[type="submit"]');
    if (isSubmitting) {
      btn.dataset.originalText = btn.textContent;
      btn.disabled = true;
      btn.textContent = "در حال ذخیره...";
    } else {
      btn.disabled = false;
      if (btn.dataset.originalText) {
        btn.textContent = btn.dataset.originalText;
      }
    }
  }

  _formatTime(timeStr) {
    if (!timeStr) return "";
    // If format is HH:MM:SS, take only HH:MM
    return timeStr.split(":").slice(0, 2).join(":");
  }

  // ============================================================
  // Event Binding (Connecting View to Controller)
  // ============================================================

  bindSearch(handler) {
    this.elements.courseSearch.addEventListener("input", (e) => {
      handler(e.target.value);
    });
  }

  bindFilterDepartment(handler) {
    this.elements.filterDepartment.addEventListener("change", (e) => {
      handler(e.target.value);
    });
  }

  bindFilterSemester(handler) {
    this.elements.filterSemester.addEventListener("change", (e) => {
      handler(e.target.value);
    });
  }

  bindAddCourseBtn(handler) {
    this.elements.addCourseBtn.addEventListener("click", handler);
  }

  bindCancelCourseBtn(handler) {
    this.elements.cancelCourseBtn.addEventListener("click", handler);
  }

  bindLogout(handler) {
    this.elements.logoutBtn.addEventListener("click", handler);
  }

  bindCourseFormSubmit(handler) {
    this.elements.courseForm.addEventListener("submit", (e) => {
      e.preventDefault();

      // Extract data manually to ensure types (e.g., parseInt)
      // This matches logic from panel.js 'onCourseFormSubmit'
      const formData = {
        code: this.elements.courseCode.value.trim(),
        name: this.elements.courseName.value.trim(),
        units: parseInt(this.elements.courseUnits.value),
        department: this.elements.courseDepartment.value.trim(),
        semester: this.elements.courseSemester.value.trim(),
        professor_name: this.elements.courseProfessor.value.trim(),
        day_of_week: this.elements.courseDay.value,
        start_time: this.elements.courseStart.value,
        end_time: this.elements.courseEnd.value,
        location: this.elements.courseLocation.value.trim(),
        capacity: parseInt(this.elements.courseCapacity.value),
      };

      handler(formData);
    });
  }

  /**
   * Binds Edit and Delete actions using Event Delegation.
   * This handles clicks on dynamically created buttons.
   * @param {Function} onEdit - Callback for edit(id)
   * @param {Function} onDelete - Callback for delete(id)
   */
  bindTableActions(onEdit, onDelete) {
    this.elements.coursesTableBody.addEventListener("click", (e) => {
      const editBtn = e.target.closest(".edit-btn");
      const deleteBtn = e.target.closest(".delete-btn");

      if (editBtn) {
        const id = parseInt(editBtn.dataset.id);
        onEdit(id);
      } else if (deleteBtn) {
        const id = parseInt(deleteBtn.dataset.id);
        onDelete(id);
      }
    });
  }
}
