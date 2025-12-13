/**
 * js/ui/student-course.view.js
 * Responsibility: Render student course list and handle UI states.
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
    };
  }

  setLoading(isLoading) {
    if (isLoading) {
      this.elements.loadingSpinner.classList.remove("hidden");
      this.elements.coursesGrid.classList.add("hidden");
      this.elements.emptyState.classList.add("hidden");
      this.elements.errorMessage.classList.add("hidden");
    } else {
      this.elements.loadingSpinner.classList.add("hidden");
    }
  }

  showError(message) {
    this.elements.errorMessage.textContent = message;
    this.elements.errorMessage.classList.remove("hidden");
    this.elements.coursesGrid.classList.add("hidden");
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

  renderCourses(courses, prerequisites = []) {
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
      const isFull = (course.enrolled || 0) >= course.capacity;

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
                     )} ${course.start_time.slice(
        0,
        5
      )} - ${course.end_time.slice(0, 5)}</span>
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
           `;

      this.elements.coursesGrid.appendChild(card);
    });
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
