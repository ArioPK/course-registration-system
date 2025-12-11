/**
 * js/ui/notification.js
 * Responsibility: Handles user feedback (Toasts), modals, and visual validation states.
 */

export class NotificationService {
  constructor() {
    this.confirmationModal = document.getElementById("confirmation-modal");
    
    
    this._initToastContainer();
  }

 
  _initToastContainer() {
    if (!document.querySelector('.toast-container')) {
      this.toastContainer = document.createElement('div');
      this.toastContainer.className = 'toast-container';
      document.body.appendChild(this.toastContainer);
    } else {
      this.toastContainer = document.querySelector('.toast-container');
    }
  }

  /**
   * @param {string} title 
   * @param {string} message 
   * @param {string} type 
   */
  _showToast(title, message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
   
    const iconClass = type === 'success' ? 'ri-checkbox-circle-fill' : 'ri-error-warning-fill';

    toast.innerHTML = `
      <i class="${iconClass}"></i>
      <div class="toast-content">
        <span class="toast-title">${title}</span>
        <span class="toast-message">${message}</span>
      </div>
    `;

    this.toastContainer.appendChild(toast);

   
    setTimeout(() => {
      toast.style.animation = 'toastFadeOut 0.5s ease forwards';
      toast.addEventListener('animationend', () => {
        toast.remove();
      });
    }, 4000);
  }

  // ============================================================
  // General Notifications (Toasts) 
  // ============================================================

  showSuccess(message) {
    
    this._showToast("موفقیت‌آمیز", message, "success");
  }

  showError(message) {
    this._showToast("خطا", message, "error");
  }

  // ============================================================
  // Modal Management 
  // ============================================================

  openModal(modal) {
    if (modal) modal.classList.add("active");
  }

  closeModal(modal) {
    if (modal) modal.classList.remove("active");
  }

  showConfirmation(message, onConfirm) {
    if (!this.confirmationModal) return;

    const messageEl = this.confirmationModal.querySelector("#confirmation-message");
    if (messageEl) messageEl.textContent = message;

    this.openModal(this.confirmationModal);

    const confirmBtn = this.confirmationModal.querySelector("#confirm-btn");
    const cancelBtn = this.confirmationModal.querySelector("#cancel-btn");

    const newConfirmBtn = confirmBtn.cloneNode(true);
    const newCancelBtn = cancelBtn.cloneNode(true);
    
    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
    cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);

    const cleanup = () => this.closeModal(this.confirmationModal);

    newConfirmBtn.addEventListener("click", () => {
      onConfirm();
      cleanup();
    });

    newCancelBtn.addEventListener("click", cleanup);
  }

  // ============================================================
  // Form Validation UI 
  // ============================================================

  showValidationErrors(errors) {
    errors.forEach((error) => {
      const field = document.getElementById(error.field);
      if (field) {
        field.classList.add("input-error");
        const formGroup = field.closest(".form-group");
        const existingError = formGroup.querySelector(".field-error");
        if (existingError) existingError.remove();

        const errorElement = document.createElement("span");
        errorElement.className = "field-error";
        errorElement.textContent = error.message;
        formGroup.appendChild(errorElement);
      }
    });

    if (errors.length > 0) {
      const firstErrorField = document.getElementById(errors[0].field);
      if (firstErrorField) firstErrorField.focus();
    }
  }

  clearValidationErrors(formElement) {
    if (!formElement) return;
    const errorFields = formElement.querySelectorAll(".input-error");
    errorFields.forEach((field) => field.classList.remove("input-error"));
    const errorMessages = formElement.querySelectorAll(".field-error");
    errorMessages.forEach((msg) => msg.remove());
  }
}