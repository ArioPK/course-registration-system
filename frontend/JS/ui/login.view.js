/**
 * js/ui/login.view.js
 * Responsibility: DOM manipulation for the login page.
 */
export class LoginView {
  constructor() {
    this.elements = {
      form: document.getElementById("loginForm"),
      username: document.getElementById("username"),
      password: document.getElementById("password"),
      submitBtn: document.querySelector(".login-btn"),
      errorElement: document.getElementById("login-error"),
    };
    
    // Set default values
    this.setDefaultValues();
  }
  
  setDefaultValues() {
    // Set default student ID
    if (this.elements.username) {
      this.elements.username.placeholder = "مثال: stu_1001 یا p123456";
    }
  }

  getFormData() {
    return {
      username: this.elements.username.value,
      password: this.elements.password.value,
    };
  }

  /**
   * Bind submit event
   */
  bindLogin(handler) {
    if (this.elements.form) {
      this.elements.form.addEventListener("submit", (e) => {
        e.preventDefault();
        handler(this.getFormData());
      });
    }
  }

  /**
   * Bind real-time validation events (blur & input) - NEW
   * This matches the original Login.js logic.
   */
  bindRealTimeValidation(validationHandler) {
    const inputs = [this.elements.username, this.elements.password];

    inputs.forEach((input) => {
      // Validate on blur (leaving the field)
      input.addEventListener("blur", () => {
        const fieldName = input.id; // "username" or "password"
        const value = input.value;
        const result = validationHandler(fieldName, value);
        this.updateFieldValidation(input, result.isValid, result.message);
      });

      // Clear errors on input (typing)
      input.addEventListener("input", () => {
        if (input.classList.contains("input-error")) {
          this.updateFieldValidation(input, true, "");
        }
      });
    });
  }

  /**
   * Updates visual state of a field (Error/Success classes) - NEW
   */
  updateFieldValidation(input, isValid, message) {
    const formGroup = input.closest(".form-group");
    const errorSpan = formGroup.querySelector(".field-error");

    // Reset classes
    input.classList.remove("input-error", "input-success");
    if (errorSpan) errorSpan.remove();

    if (isValid === false) {
      // Show Error
      input.classList.add("input-error");
      const errorElement = document.createElement("span");
      errorElement.className = "field-error";
      errorElement.textContent = message;
      formGroup.appendChild(errorElement);
    } else if (isValid === true && input.value.trim()) {
      // Show Success (Green border)
      input.classList.add("input-success");
    }
  }

  // Used for Form Submit validation
  showFieldErrors(errors) {
    this.clearGlobalError();

    if (errors.username) {
      this.updateFieldValidation(
        this.elements.username,
        false,
        errors.username
      );
    }
    if (errors.password) {
      this.updateFieldValidation(
        this.elements.password,
        false,
        errors.password
      );
    }

    this.showGlobalError("لطفاً فیلدهای فرم را به درستی پر کنید.");
    this.shakeForm();
  }

  clearGlobalError() {
    this.elements.errorElement.textContent = "";
    this.elements.errorElement.className = "error-message";
  }

  // Clear all validation styles
  clearAllValidation() {
    [this.elements.username, this.elements.password].forEach((input) => {
      input.classList.remove("input-error", "input-success");
      const group = input.closest(".form-group");
      const err = group.querySelector(".field-error");
      if (err) err.remove();
    });
  }

  setLoading(isLoading) {
    const btn = this.elements.submitBtn;
    if (isLoading) {
      btn.disabled = true;
      btn.classList.add("loading");
      btn.innerHTML = '<span class="spinner"></span> در حال ورود...';
    } else {
      btn.disabled = false;
      btn.classList.remove("loading");
      btn.textContent = "ورود";
    }
  }

  showGlobalError(message) {
    this.elements.errorElement.className = "error-message";
    this.elements.errorElement.textContent = message;
    this.shakeForm();
  }

  shakeForm() {
    this.elements.form.style.animation = "shake 0.5s";
    setTimeout(() => {
      this.elements.form.style.animation = "";
    }, 500);
  }

  showSuccessMessage() {
    this.elements.errorElement.textContent = "";
    this.elements.errorElement.className = "success-message";
    this.elements.errorElement.textContent =
      "ورود موفقیت‌آمیز بود. در حال انتقال...";
  }
}
