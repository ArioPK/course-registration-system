/**
 * js/ui/student-course.view.js
 * Responsibility: Render student course list, enrollments, and handle UI states.
 */
export class StudentCourseView {
  constructor() {
    this.elements = {
      coursesGrid: document.getElementById("courses-grid"),
      loadingSpinner: document.getElementById("loading-spinner"),
      errorMessage: document.getElementById("error-message"),
      emptyState: document.getElementById("empty-state"),
      logoutBtn: document.getElementById("logout-btn"),
      searchInput: document.getElementById("course-search"),
      filterTypeSelect: document.getElementById("search-filter-type"),
      searchToolbar: document.querySelector(".student-search-toolbar"),

      enrollmentsSection: document.getElementById("enrollments-section"),
      enrollmentsBody: document.getElementById("my-enrollments-body"),
      totalUnitsEl: document.getElementById("total-units-count"),
      totalCoursesEl: document.getElementById("total-courses-count"),
      noEnrollmentsMsg: document.getElementById("no-enrollments-msg"),

      scheduleSection: document.getElementById("schedule-section"),
    };
  }

  setLoading(isLoading) {
    if (isLoading) {
      if (this.elements.loadingSpinner)
        this.elements.loadingSpinner.classList.remove("hidden");
      if (this.elements.coursesGrid)
        this.elements.coursesGrid.classList.add("hidden");
      if (this.elements.emptyState)
        this.elements.emptyState.classList.add("hidden");
      if (this.elements.errorMessage)
        this.elements.errorMessage.classList.add("hidden");
    } else {
      if (this.elements.loadingSpinner)
        this.elements.loadingSpinner.classList.add("hidden");
    }
  }

  showLoading(isLoading) {
    this.setLoading(isLoading);
  }

  showError(message) {
    if (this.elements.errorMessage) {
      this.elements.errorMessage.textContent = message;
      this.elements.errorMessage.classList.remove("hidden");
    }
    if (this.elements.coursesGrid)
      this.elements.coursesGrid.classList.add("hidden");
    alert(message);
  }

  _translateDay(dayCode) {
    const days = {
      SAT: "شنبه",
      SUN: "یک‌شنبه",
      MON: "دوشنبه",
      TUE: "سه‌شنبه",
      WED: "چهارشنبه",
      THU: "پنج‌شنبه",
      FRI: "جمعه",
    };
    return days[dayCode] || dayCode;
  }

  _formatTime(time) {
    if (!time) return "";
    // Handle both string and time object
    if (typeof time === "string") {
      return time.slice(0, 5);
    }
    // Handle time object from backend (HH:MM:SS format)
    const timeStr = String(time);
    return timeStr.slice(0, 5);
  }

  /**
   *
   * @param {Array} courses
   * @param {Array} prerequisites
   * @param {Function} onEnrollClick
   * @param {Set} enrolledIdsSet
   */
  renderCourses(
    courses,
    prerequisites = [],
    onEnrollClick,
    enrolledIdsSet = new Set()
  ) {
    this.elements.coursesGrid.innerHTML = "";

    if (!courses || courses.length === 0) {
      this.elements.coursesGrid.classList.add("hidden");
      this.elements.emptyState.classList.remove("hidden");
      return;
    }

    this.elements.coursesGrid.classList.remove("hidden");
    this.elements.emptyState.classList.add("hidden");

    courses.forEach((course) => {
      const coursePrereqs = prerequisites.filter(
        (p) => p.target_course_id === course.id
      );
      const hasPrereq = coursePrereqs.length > 0;

      const isEnrolled = enrolledIdsSet.has(course.id);
      const isFull = (course.enrolled || 0) >= course.capacity;

      let btnHtml = "";
      if (isEnrolled) {
        btnHtml = `<button class="manage-btn-card disabled" disabled>اخذ شده <i class="ri-check-line"></i></button>`;
      } else {
        btnHtml = `<button class="manage-btn-card enroll-btn">اخذ درس <i class="ri-add-line"></i></button>`;
      }

      const card = document.createElement("div");
      card.className = "course-card";

      card.innerHTML = `
              <div class="course-header">
                 <span class="course-code">${course.code}</span>
                 ${
                   hasPrereq
                     ? '<i class="ri-links-line" title="دارای پیش‌نیاز" style="color: var(--accent);"></i>'
                     : ""
                 }
              </div>
              <div class="course-title">${course.name}</div>
              
              <div class="course-info">
                  <div class="info-row">
                      <i class="ri-user-voice-line"></i>
                      <span>${course.professor_name}</span>
                  </div>
                  <div class="info-row">
                      <i class="ri-file-list-3-line"></i>
                      <span>${course.units} واحد</span>
                  </div>
                  <div class="info-row">
                      <i class="ri-time-line"></i>
                      <span>${this._translateDay(
                        course.day_of_week
                      )} ${this._formatTime(course.start_time)} - ${this._formatTime(course.end_time)}</span>
                  </div>
                  <div class="info-row">
                      <i class="ri-map-pin-line"></i>
                      <span>${course.location}</span>
                  </div>
                  <div class="info-row" style="margin-top: 10px; color: ${
                    isFull ? "var(--danger)" : "#4caf50"
                  }">
                      <i class="ri-group-line"></i>
                      <span>ظرفیت: ${course.enrolled || 0} / ${
        course.capacity
      }</span>
                  </div>
              </div>
              ${btnHtml}
            `;

      if (!isEnrolled) {
        const btn = card.querySelector(".enroll-btn");
        if (btn) {
          btn.addEventListener("click", () => onEnrollClick(course.id));
        }
      }

      this.elements.coursesGrid.appendChild(card);
    });
  }

  /**
  
   * @param {Array} enrollments
   * @param {number} totalUnits
   * @param {Function} onDropClick
   * @param {Object} unitConfig 
   */
  renderEnrollments(enrollments, totalUnits, onDropClick, unitConfig) {
    if (!this.elements.enrollmentsBody) return;

    this.elements.enrollmentsBody.innerHTML = "";

    if (this.elements.totalUnitsEl) {
      let text = `${totalUnits}`;
      if (unitConfig) {
        text += ` (مجاز: ${unitConfig.min_units} تا ${unitConfig.max_units})`;

        if (
          totalUnits < unitConfig.min_units ||
          totalUnits > unitConfig.max_units
        ) {
          this.elements.totalUnitsEl.style.color = "var(--danger)";
        } else {
          this.elements.totalUnitsEl.style.color = "var(--accent)";
        }
      }
      this.elements.totalUnitsEl.textContent = text;
    }

    if (this.elements.totalCoursesEl)
      this.elements.totalCoursesEl.textContent = enrollments.length;

    if (enrollments.length === 0) {
      if (this.elements.noEnrollmentsMsg)
        this.elements.noEnrollmentsMsg.classList.remove("hidden");
    } else {
      if (this.elements.noEnrollmentsMsg)
        this.elements.noEnrollmentsMsg.classList.add("hidden");

      enrollments.forEach((item) => {
        const c = item.course;
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${c.code}</td>
            <td>${c.name}</td>
            <td>${c.units}</td>
            <td>${c.professor_name}</td>
            <td>${this._translateDay(c.day_of_week)} ${this._formatTime(c.start_time)}</td>
            <td>
                <button class="btn-danger-small drop-btn">
                    <i class="ri-delete-bin-line"></i> حذف
                </button>
            </td>
        `;

        const dropBtn = tr.querySelector(".drop-btn");
        if (dropBtn) {
          dropBtn.addEventListener("click", () => onDropClick(c.id));
        }

        this.elements.enrollmentsBody.appendChild(tr);
      });
    }
  }

  /**
  
   */
  toggleSection(sectionName) {
    if (this.elements.searchToolbar)
      this.elements.searchToolbar.classList.add("hidden");
    if (this.elements.coursesGrid)
      this.elements.coursesGrid.classList.add("hidden");
    if (this.elements.enrollmentsSection)
      this.elements.enrollmentsSection.classList.add("hidden");
    if (this.elements.scheduleSection)
      this.elements.scheduleSection.classList.add("hidden");
    if (this.elements.emptyState)
      this.elements.emptyState.classList.add("hidden");

    if (sectionName === "catalog") {
      if (this.elements.searchToolbar)
        this.elements.searchToolbar.classList.remove("hidden");
      if (this.elements.coursesGrid)
        this.elements.coursesGrid.classList.remove("hidden");
    } else if (sectionName === "enrollments") {
      if (this.elements.enrollmentsSection)
        this.elements.enrollmentsSection.classList.remove("hidden");
    } else if (sectionName === "schedule") {
      if (this.elements.scheduleSection)
        this.elements.scheduleSection.classList.remove("hidden");
    }
  }

  updateSearchPlaceholder(filterType) {
    if (!this.elements.searchInput) return;

    if (filterType === "course_mix") {
      this.elements.searchInput.placeholder = "جستجو در نام یا کد درس...";
    } else if (filterType === "professor_name") {
      this.elements.searchInput.placeholder = "نام استاد را وارد کنید...";
    }
  }

  bindLogout(handler) {
    if (this.elements.logoutBtn) {
      this.elements.logoutBtn.addEventListener("click", handler);
    }
  }

  bindSearch(handler) {
    if (this.elements.searchInput) {
      this.elements.searchInput.addEventListener("input", (e) => {
        handler(e.target.value);
      });
    }
  }

  bindFilterType(handler) {
    if (this.elements.filterTypeSelect) {
      this.elements.filterTypeSelect.addEventListener("change", (e) => {
        const type = e.target.value;
        this.updateSearchPlaceholder(type);
        handler(type);
      });
    }
  }
}
