/**
 * js/ui/views/course-manager.view.js
 */
export class CourseManagerView {
  constructor(notificationService) {
    this.notifier = notificationService;
    this.elements = {
      form: document.getElementById("course-form"),
      inputs: {
        code: document.getElementById("course-code"),
        name: document.getElementById("course-name"),
        units: document.getElementById("course-units"),
        department: document.getElementById("course-department"),
        semester: document.getElementById("course-semester"),
        capacity: document.getElementById("course-capacity"),
        professor: document.getElementById("course-professor"),
        day: document.getElementById("course-day"),
        start: document.getElementById("course-start"),
        end: document.getElementById("course-end"),
        location: document.getElementById("course-location"),
      },
      addBtn: document.getElementById("add-course-btn"),
      cancelBtn: document.getElementById("cancel-course-btn"),
      modal: document.getElementById("course-modal"),
      modalTitle: document.getElementById("course-modal-title"),
      tableBody: document.getElementById("courses-table-body"),

      search: document.getElementById("course-search"),
      filterDept: document.getElementById("filter-department"),
      filterSem: document.getElementById("filter-semester"),

      summary: {
        total: document.getElementById("total-courses"),
        capacity: document.getElementById("total-capacity"),
        enrolled: document.getElementById("total-enrolled"),
      },
    };
  }

  renderCourses(courses) {
    const tbody = this.elements.tableBody;
    tbody.innerHTML = "";

    if (!courses || courses.length === 0) {
      tbody.innerHTML = `<tr><td colspan="11" style="text-align: center; padding: 40px; color: var(--medium-grey);">درسی یافت نشد</td></tr>`;
      return;
    }

    courses.forEach((course) => {
      const enrolled = course.enrolled || 0;
      const isFull = enrolled >= course.capacity;

      const row = document.createElement("tr");
      if (isFull) row.classList.add("full-row");

      row.innerHTML = `
          <td>${course.code}</td>
          <td>${course.name}</td>
          <td>${course.units}</td>
          <td>${course.department}</td>
          <td>${course.semester}</td>
          <td>${course.professor_name}</td>
          <td style="font-size: 0.85rem; direction: ltr; text-align: right;">
              ${this._translateDay(course.day_of_week)}<br>
              ${this._formatTime(course.start_time)} - ${this._formatTime(
        course.end_time
      )}
          </td>
          <td>${course.location}</td>
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
              }" title="ویرایش"><i class="ri-pencil-fill"></i></button>
              <button class="action-btn delete-btn" data-id="${
                course.id
              }" title="حذف"><i class="ri-delete-bin-6-line"></i></button>
            </div>
          </td>
        `;
      tbody.appendChild(row);
    });
  }

  populateFilters(departments, semesters) {
    const renderOptions = (select, items) => {
      while (select.children.length > 1) select.removeChild(select.lastChild);
      items.forEach((item) => {
        const opt = document.createElement("option");
        opt.value = item;
        opt.textContent = item;
        select.appendChild(opt);
      });
    };
    renderOptions(this.elements.filterDept, departments);
    renderOptions(this.elements.filterSem, semesters);
  }

  updateSummary(stats) {
    this.elements.summary.total.textContent = stats.totalCourses;
    this.elements.summary.capacity.textContent = stats.totalCapacity;
    this.elements.summary.enrolled.textContent = stats.totalEnrolled;
  }

  fillForm(course) {
    const i = this.elements.inputs;
    i.code.value = course.code;
    i.name.value = course.name;
    i.units.value = course.units;
    i.department.value = course.department;
    i.semester.value = course.semester;
    i.capacity.value = course.capacity;
    i.professor.value = course.professor_name;
    i.day.value = course.day_of_week;
    i.start.value = this._formatTime(course.start_time);
    i.end.value = this._formatTime(course.end_time);
    i.location.value = course.location;
  }

  resetForm() {
    this.elements.form.reset();
  }

  openModal(title) {
    this.elements.modalTitle.textContent = title;
    this.notifier.openModal(this.elements.modal);
  }

  closeModal() {
    this.notifier.closeModal(this.elements.modal);
    this.resetForm();
  }

  setFormSubmitting(isSubmitting) {
    const btn = this.elements.form.querySelector('button[type="submit"]');
    if (isSubmitting) {
      btn.dataset.originalText = btn.textContent;
      btn.disabled = true;
      btn.textContent = "در حال ذخیره...";
    } else {
      btn.disabled = false;
      if (btn.dataset.originalText) btn.textContent = btn.dataset.originalText;
    }
  }

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
    return days[day] || day;
  }

  _formatTime(timeStr) {
    return timeStr ? timeStr.split(":").slice(0, 2).join(":") : "";
  }

  bindSearch(handler) {
    this.elements.search.addEventListener("input", (e) =>
      handler(e.target.value)
    );
  }

  bindFilters(deptHandler, semHandler) {
    this.elements.filterDept.addEventListener("change", (e) =>
      deptHandler(e.target.value)
    );
    this.elements.filterSem.addEventListener("change", (e) =>
      semHandler(e.target.value)
    );
  }

  bindAddCourse(handler) {
    this.elements.addBtn.addEventListener("click", handler);
  }

  bindCancel(handler) {
    this.elements.cancelBtn.addEventListener("click", handler);
  }

  bindSubmit(handler) {
    this.elements.form.addEventListener("submit", (e) => {
      e.preventDefault();
      const formData = {
        code: this.elements.inputs.code.value.trim(),
        name: this.elements.inputs.name.value.trim(),
        units: parseInt(this.elements.inputs.units.value),
        department: this.elements.inputs.department.value.trim(),
        semester: this.elements.inputs.semester.value.trim(),
        professor_name: this.elements.inputs.professor.value.trim(),
        day_of_week: this.elements.inputs.day.value,
        start_time: this.elements.inputs.start.value,
        end_time: this.elements.inputs.end.value,
        location: this.elements.inputs.location.value.trim(),
        capacity: parseInt(this.elements.inputs.capacity.value),
      };
      handler(formData);
    });
  }

  bindTableActions(onEdit, onDelete) {
    this.elements.tableBody.addEventListener("click", (e) => {
      const editBtn = e.target.closest(".edit-btn");
      const deleteBtn = e.target.closest(".delete-btn");

      if (editBtn) onEdit(parseInt(editBtn.dataset.id));
      else if (deleteBtn) onDelete(parseInt(deleteBtn.dataset.id));
    });
  }
}
