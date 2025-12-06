/**
 * js/utils/login.validator.js
 * Responsibility: Pure validation logic for login form.
 */
export class LoginValidator {
  /**
   * Validate a specific field individually (used for 'blur' events)
   */
  validateField(fieldName, value) {
    const trimmed = value ? value.trim() : "";

    if (fieldName === "username") {
      if (!trimmed)
        return { isValid: false, message: "نام کاربری الزامی است." };
      if (trimmed.length < 3)
        return {
          isValid: false,
          message: "نام کاربری باید حداقل ۳ کاراکتر باشد.",
        };
      if (trimmed.length > 50)
        return {
          isValid: false,
          message: "نام کاربری نمی‌تواند بیشتر از ۵۰ کاراکتر باشد.",
        };
      if (!/^[a-zA-Z0-9_\u0600-\u06FF]+$/.test(trimmed)) {
        return {
          isValid: false,
          message: "نام کاربری فقط می‌تواند شامل حروف، اعداد و خط زیر باشد.",
        };
      }
      return { isValid: true, message: "" };
    }

    if (fieldName === "password") {
      if (!value) return { isValid: false, message: "رمز عبور الزامی است." };
      if (value.length < 4)
        return {
          isValid: false,
          message: "رمز عبور باید حداقل ۴ کاراکتر باشد.",
        };
      if (value.length > 100)
        return {
          isValid: false,
          message: "رمز عبور نمی‌تواند بیشتر از ۱۰۰ کاراکتر باشد.",
        };
      return { isValid: true, message: "" };
    }

    return { isValid: true, message: "" };
  }

  /**
   * Validate the entire form (used for 'submit' event)
   */
  validate(data) {
    const errors = {};

    const userVal = this.validateField("username", data.username);
    if (!userVal.isValid) errors.username = userVal.message;

    const passVal = this.validateField("password", data.password);
    if (!passVal.isValid) errors.password = passVal.message;

    return {
      isValid: Object.keys(errors).length === 0,
      errors,
    };
  }
}
