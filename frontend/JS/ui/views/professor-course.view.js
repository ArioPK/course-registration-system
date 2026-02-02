/**
 * frontend/JS/ui/professor-course.view.js

 */
export class ProfessorCourseView {
  constructor() {
    this.coursesGrid = document.getElementById("professor-courses-grid");
    this.studentsSection = document.getElementById("students-section");
    this.studentsTableBody = document.getElementById("students-table-body");
    this.selectedCourseNameSpan = document.getElementById(
      "selected-course-name"
    );
    this.loadingSpinner = document.getElementById("loading-spinner");
    this.emptyState = document.getElementById("empty-state");

    const backBtn = document.getElementById("back-to-courses-btn");
    if (backBtn) {
      backBtn.addEventListener("click", () => this.showCoursesList());
    }
  }

  showLoading(isLoading) {
    if (this.loadingSpinner) {
      this.loadingSpinner.classList.toggle("hidden", !isLoading);
    }
  }

  renderCourses(courses, onManageClick) {
    this.coursesGrid.innerHTML = "";

    if (!courses || courses.length === 0) {
      if (this.emptyState) this.emptyState.classList.remove("hidden");
      return;
    }

    if (this.emptyState) this.emptyState.classList.add("hidden");

    courses.forEach((course) => {
      const card = document.createElement("div");
      card.className = "course-card";
      card.innerHTML = `
                <h4>${course.name}</h4>
                <div class="course-info">
                    <p><i class="ri-barcode-line"></i> کد درس: ${
                      course.code
                    }</p>
                    <p><i class="ri-calendar-line"></i> ${
                      course.day_of_week || "نامشخص"
                    } - ${
        course.start_time ? course.start_time.slice(0, 5) : ""
      }</p>
                    <p><i class="ri-map-pin-line"></i> مکان: ${
                      course.location
                    }</p>
                </div>
                <button class="manage-btn-card">
                    <i class="ri-group-line"></i> مدیریت دانشجویان
                </button>
            `;

      const btn = card.querySelector(".manage-btn-card");
      btn.addEventListener("click", () => onManageClick(course));

      this.coursesGrid.appendChild(card);
    });
  }

  renderStudents(courseName, students, onRemoveClick) {
    document.getElementById("courses-section").classList.add("hidden");
    this.studentsSection.classList.remove("hidden");

    this.selectedCourseNameSpan.textContent = courseName;
    this.studentsTableBody.innerHTML = "";

    const noStudentsMsg = document.getElementById("no-students-msg");

    if (!students || students.length === 0) {
      if (noStudentsMsg) noStudentsMsg.classList.remove("hidden");
      return;
    }

    if (noStudentsMsg) noStudentsMsg.classList.add("hidden");

    students.forEach((student, index) => {
      const row = document.createElement("tr");
      row.innerHTML = `
                <td>${index + 1}</td>
                <td>${student.name || "نامشخص"}</td>
                <td>${student.student_id_number || student.student_id}</td>
                <td>
                    <button class="btn-danger-small remove-student-btn">
                        <i class="ri-delete-bin-line"></i> حذف
                    </button>
                </td>
            `;

      const removeBtn = row.querySelector(".remove-student-btn");
      removeBtn.addEventListener("click", () => {
        if (
          confirm(
            `آیا از حذف دانشجو "${student.name}" از این درس اطمینان دارید؟`
          )
        ) {
          onRemoveClick(student.id);
        }
      });

      this.studentsTableBody.appendChild(row);
    });
  }

  showCoursesList() {
    this.studentsSection.classList.add("hidden");
    document.getElementById("courses-section").classList.remove("hidden");
  }

  showError(message) {
    alert(message);
  }
}
