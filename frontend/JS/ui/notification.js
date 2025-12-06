/**
 * js/ui/notification.js
 * Responsibility: Handles user feedback, modals, and visual validation states.
 * Replaces the 'ui' object from the monolithic panel.js.
 */

export class NotificationService {
  constructor() {
    // Cache the confirmation modal element as it's used globally
    this.confirmationModal = document.getElementById("confirmation-modal");
  }

  // ============================================================
  // General Notifications (Alerts/Toasts)
  // ============================================================

  /**
   * Shows a success message.
   * Currently uses native alert, but can be upgraded to a custom toast.
   * @param {string} message - The message to display.
   */
  showSuccess(message) {
    // In a real app, you might replace this with a toast notification
    alert(message);
  }

  /**
   * Shows an error message.
   * @param {string} message - The error message.
   */
  showError(message) {
    alert(message);
  }

  // ============================================================
  // Modal Management
  // ============================================================

  /**
   * Opens a generic modal by adding the active class.
   * @param {HTMLElement} modal - The modal element to open.
   */
  openModal(modal) {
    if (modal) {
      modal.classList.add("active");
    }
  }

  /**
   * Closes a generic modal by removing the active class.
   * @param {HTMLElement} modal - The modal element to close.
   */
  closeModal(modal) {
    if (modal) {
      modal.classList.remove("active");
    }
  }

  /**
   * Shows the confirmation modal with a custom message and action.
   * Logic extracted from panel.js 'showConfirmation'.
   * @param {string} message - The question to ask the user.
   * @param {Function} onConfirm - Callback function to run if confirmed.
   */
  showConfirmation(message, onConfirm) {
    if (!this.confirmationModal) {
      console.error("Confirmation modal element not found!");
      return;
    }

    // Set the message
    const messageEl = this.confirmationModal.querySelector(
      "#confirmation-message"
    );
    if (messageEl) messageEl.textContent = message;

    // Open the modal
    this.openModal(this.confirmationModal);

    // Get buttons
    const confirmBtn = this.confirmationModal.querySelector("#confirm-btn");
    const cancelBtn = this.confirmationModal.querySelector("#cancel-btn");

    // Clean up old event listeners using cloneNode
    // This prevents multiple event listeners from stacking up
    const newConfirmBtn = confirmBtn.cloneNode(true);
    const newCancelBtn = cancelBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
    cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);

    // Define cleanup function to close modal
    const cleanup = () => {
      this.closeModal(this.confirmationModal);
    };

    // Attach new listeners
    newConfirmBtn.addEventListener("click", () => {
      onConfirm();
      cleanup();
    });

    newCancelBtn.addEventListener("click", cleanup);
  }

  // ============================================================
  // Form Validation UI
  // ============================================================

  /**
   * Displays validation errors on the form fields.
   * Logic extracted from panel.js 'showFormValidationErrors'.
   * @param {Array} errors - Array of error objects { field: 'id', message: 'text' }
   */
  showValidationErrors(errors) {
    errors.forEach((error) => {
      const field = document.getElementById(error.field);
      if (field) {
        // Add error styling to input
        field.classList.add("input-error");

        // Find parent group to append error message
        const formGroup = field.closest(".form-group");

        // Remove existing error message if any
        const existingError = formGroup.querySelector(".field-error");
        if (existingError) {
          existingError.remove();
        }

        // Create and append new error message
        const errorElement = document.createElement("span");
        errorElement.className = "field-error";
        errorElement.textContent = error.message;

        // Simple animation (CSS animation logic is handled in CSS file)
        formGroup.appendChild(errorElement);
      }
    });

    // Focus on the first field with an error for better UX
    if (errors.length > 0) {
      const firstErrorField = document.getElementById(errors[0].field);
      if (firstErrorField) {
        firstErrorField.focus();
      }
    }
  }

  /**
   * Clears all validation error styles and messages from a form.
   * Logic extracted from panel.js 'clearFormValidation'.
   * @param {HTMLFormElement} formElement - The form to clear errors from.
   */
  clearValidationErrors(formElement) {
    if (!formElement) return;

    // Remove red borders/backgrounds
    const errorFields = formElement.querySelectorAll(".input-error");
    errorFields.forEach((field) => field.classList.remove("input-error"));

    // Remove error text messages
    const errorMessages = formElement.querySelectorAll(".field-error");
    errorMessages.forEach((msg) => msg.remove());
  }
}
