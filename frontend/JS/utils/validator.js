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
    } else if (formData.units < 1 || formData.units > 6) {
      errors.push({
        field: "course-units",
        message: "تعداد واحد باید بین 1 تا 6 باشد.",
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
}
