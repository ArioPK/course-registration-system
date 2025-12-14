/**
 * js/ui/views/prerequisite.view.js
 */
export class PrerequisiteView {
  constructor(notificationService) {
    this.notifier = notificationService;
    this.elements = {
      tableBody: document.getElementById("prerequisites-table-body"),
      modal: document.getElementById("prerequisite-modal"),
      form: document.getElementById("prerequisite-form"),
      openBtn: document.getElementById("open-prereq-modal-btn"),
      saveBtn: document.getElementById("save-prereq-btn"),
      targetSelect: document.getElementById("target-course-id"),
      prereqSelect: document.getElementById("prerequisite-course-id"),
    };
  }

  renderPrerequisites(prerequisites, coursesMap) {
    const tbody = this.elements.tableBody;
    tbody.innerHTML = "";

    if (!prerequisites || prerequisites.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 40px; color: var(--medium-grey);">هیچ پیش‌نیازی تعریف نشده است.</td></tr>`;
      return;
    }

    prerequisites.forEach((prereq) => {
      const target = coursesMap[prereq.target_course_id] || {
        name: "ناشناس",
        code: "N/A",
      };
      const pre = coursesMap[prereq.prerequisite_course_id] || {
        name: "ناشناس",
        code: "N/A",
      };

      const row = document.createElement("tr");
      row.innerHTML = `
          <td>${target.name}</td>
          <td>${target.code}</td>
          <td>${pre.name}</td>
          <td>${pre.code}</td>
          <td style="text-align: center;">
              <button class="action-btn delete-prereq-btn" data-id="${prereq.id}" title="حذف">
                <i class="ri-delete-bin-6-line"></i>
              </button>
          </td>
        `;
      tbody.appendChild(row);
    });
  }

  populateDropdowns(courses) {
    const fill = (select) => {
      while (select.children.length > 1) select.removeChild(select.lastChild);
      courses.forEach((c) => {
        const opt = document.createElement("option");
        opt.value = c.id;
        opt.textContent = `${c.code} - ${c.name}`;
        select.appendChild(opt);
      });
    };
    fill(this.elements.targetSelect);
    fill(this.elements.prereqSelect);
  }

  openModal() {
    this.notifier.openModal(this.elements.modal);
  }

  closeModal() {
    this.notifier.closeModal(this.elements.modal);
    this.elements.form.reset();
  }

  setSubmitting(isSubmitting) {
    const btn = this.elements.saveBtn;
    if (isSubmitting) {
      btn.dataset.originalText = btn.textContent;
      btn.disabled = true;
      btn.textContent = "در حال ذخیره...";
    } else {
      btn.disabled = false;
      if (btn.dataset.originalText) btn.textContent = btn.dataset.originalText;
    }
  }


  bindOpenModal(handler) {
    this.elements.openBtn.addEventListener("click", handler);
  }

  bindSubmit(handler) {
    this.elements.form.addEventListener("submit", (e) => {
      e.preventDefault();
      const data = {
        target_course_id: parseInt(this.elements.targetSelect.value),
        prerequisite_course_id: parseInt(this.elements.prereqSelect.value),
      };
      handler(data);
    });
  }

  bindDelete(handler) {
    this.elements.tableBody.addEventListener("click", (e) => {
      const btn = e.target.closest(".delete-prereq-btn");
      if (btn) handler(parseInt(btn.dataset.id));
    });
  }
}
