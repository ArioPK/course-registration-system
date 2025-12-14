/**
 * js/utils/validators/settings.validator.js
 */
export class SettingsValidator {
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