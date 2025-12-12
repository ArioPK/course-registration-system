export class CourseValidator {
  /**
    
     * @param {Object} formData 
     * @param {Array} existingCourses 
     * @param {number|string|null} currentEditId 
     * @returns {Object} 
     */
  validate(formData, existingCourses = [], currentEditId = null) {
    const errors = [];

    if (!formData.code) {
      errors.push({
        field: "course-code",
        message: "کد درس الزامی است.",
      });
    } else if (formData.code.length < 2) {
      errors.push({
        field: "course-code",
        message: "کد درس باید حداقل 2 کاراکتر باشد.",
      });
    } else if (!/^[A-Z0-9]+$/i.test(formData.code)) {
      errors.push({
        field: "course-code",
        message: "کد درس فقط می‌تواند شامل حروف و اعداد باشد.",
      });
    } else {
      if (Array.isArray(existingCourses)) {
        const isDuplicate = existingCourses.some(
          (course) =>
            course &&
            course.code &&
            course.code.toLowerCase() === formData.code.toLowerCase() &&
            course.id != currentEditId
        );

        if (isDuplicate) {
          errors.push({
            field: "course-code",
            message: `کد درس "${formData.code}" قبلاً استفاده شده است.`,
          });
        }
      }
    }

    if (!formData.name) {
      errors.push({
        field: "course-name",
        message: "نام درس الزامی است.",
      });
    } else if (formData.name.length < 3) {
      errors.push({
        field: "course-name",
        message: "نام درس باید حداقل 3 کاراکتر باشد.",
      });
    }

    if (!formData.units || isNaN(formData.units)) {
      errors.push({
        field: "course-units",
        message: "تعداد واحد الزامی است.",
      });
    } else if (formData.units < 1 || formData.units > 4) {
      errors.push({
        field: "course-units",
        message: "تعداد واحد باید بین 1 تا 4 باشد.",
      });
    }

    if (!formData.department) {
      errors.push({
        field: "course-department",
        message: "رشته الزامی است.",
      });
    } else if (formData.department.length < 2) {
      errors.push({
        field: "course-department",
        message: "نام رشته باید حداقل 2 کاراکتر باشد.",
      });
    }

    if (!formData.semester) {
      errors.push({
        field: "course-semester",
        message: "ترم الزامی است.",
      });
    } else if (formData.semester.length < 3) {
      errors.push({
        field: "course-semester",
        message: "فرمت ترم صحیح نیست. مثال: 1403-1",
      });
    }

    if (!formData.capacity || isNaN(formData.capacity)) {
      errors.push({
        field: "course-capacity",
        message: "ظرفیت الزامی است.",
      });
    } else if (formData.capacity < 1) {
      errors.push({
        field: "course-capacity",
        message: "ظرفیت باید بیشتر از 0 باشد.",
      });
    } else if (formData.capacity > 1000) {
      errors.push({
        field: "course-capacity",
        message: "ظرفیت نمی‌تواند بیشتر از 1000 باشد.",
      });
    }

    return {
      isValid: errors.length === 0,
      errors: errors,
    };
  }

  /**
   * Validates the unit configuration form data.
   * - Ensures values are positive integers.
   * - Ensures Max Unit > Min Unit.
   * @param {Object} formData - { min_units, max_units }
   * @returns {Object} { isValid, errors: Array }
   */
  validateUnitConfiguration(formData) {
    const errors = [];
    const minUnits = formData.min_units;
    const maxUnits = formData.max_units;

    // Helper to check for positive integer
    const isPositiveInteger = (val) =>
      !isNaN(val) && val > 0 && Number.isInteger(val);

    // 1. Minimum Units Validation
    if (isNaN(minUnits) || minUnits === null) {
      errors.push({
        field: "min-units",
        message: "حداقل واحد مجاز الزامی است.",
      });
    } else if (!isPositiveInteger(minUnits)) {
      errors.push({
        field: "min-units",
        message: "حداقل واحد باید یک عدد صحیح مثبت باشد.",
      });
    }

    // 2. Maximum Units Validation
    if (isNaN(maxUnits) || maxUnits === null) {
      errors.push({
        field: "max-units",
        message: "حداکثر واحد مجاز الزامی است.",
      });
    } else if (!isPositiveInteger(maxUnits)) {
      errors.push({
        field: "max-units",
        message: "حداکثر واحد باید یک عدد صحیح مثبت باشد.",
      });
    }

    // 3. Max > Min Validation (only if both are valid numbers)
    if (isPositiveInteger(minUnits) && isPositiveInteger(maxUnits)) {
      if (minUnits >= maxUnits) {
        errors.push({
          field: "max-units",
          message: "حداکثر واحد باید از حداقل واحد بیشتر باشد.",
        });
      }
    }

    return {
      isValid: errors.length === 0,
      errors: errors,
    };
  }
}
