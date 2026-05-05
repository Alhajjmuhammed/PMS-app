/**
 * Centralized validation utilities for form inputs
 * Provides consistent validation across the mobile app
 */

export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

/**
 * Validation utility functions
 */
export const validators = {
  /**
   * Validate email format
   */
  email: (email: string): ValidationResult => {
    const trimmed = email?.trim() || '';
    if (!trimmed) {
      return { isValid: false, error: 'Email is required' };
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(trimmed)) {
      return { isValid: false, error: 'Invalid email format' };
    }
    return { isValid: true };
  },

  /**
   * Validate phone number format
   */
  phone: (phone: string): ValidationResult => {
    const trimmed = phone?.trim() || '';
    if (!trimmed) {
      return { isValid: false, error: 'Phone number is required' };
    }
    // Accepts: +1234567890, (123) 456-7890, 123-456-7890, etc.
    const phoneRegex = /^\+?[\d\s\-()]+$/;
    if (!phoneRegex.test(trimmed) || trimmed.replace(/\D/g, '').length < 10) {
      return { isValid: false, error: 'Invalid phone number (min 10 digits)' };
    }
    return { isValid: true };
  },

  /**
   * Validate required field (not empty after trim)
   */
  required: (value: any, fieldName: string = 'Field'): ValidationResult => {
    const trimmed = value?.toString().trim() || '';
    if (!trimmed) {
      return { isValid: false, error: `${fieldName} is required` };
    }
    return { isValid: true };
  },

  /**
   * Validate minimum length
   */
  minLength: (value: string, min: number, fieldName: string = 'Field'): ValidationResult => {
    const trimmed = value?.trim() || '';
    if (trimmed.length < min) {
      return { isValid: false, error: `${fieldName} must be at least ${min} characters` };
    }
    return { isValid: true };
  },

  /**
   * Validate maximum length
   */
  maxLength: (value: string, max: number, fieldName: string = 'Field'): ValidationResult => {
    const trimmed = value?.trim() || '';
    if (trimmed.length > max) {
      return { isValid: false, error: `${fieldName} must not exceed ${max} characters` };
    }
    return { isValid: true };
  },

  /**
   * Validate numeric input
   */
  numeric: (value: string, fieldName: string = 'Field'): ValidationResult => {
    const trimmed = value?.trim() || '';
    if (!trimmed) {
      return { isValid: false, error: `${fieldName} is required` };
    }
    if (!/^\d+$/.test(trimmed)) {
      return { isValid: false, error: `${fieldName} must be a number` };
    }
    return { isValid: true };
  },

  /**
   * Validate positive number (int or float)
   */
  positiveNumber: (value: string | number, fieldName: string = 'Field'): ValidationResult => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(num) || num <= 0) {
      return { isValid: false, error: `${fieldName} must be a positive number` };
    }
    return { isValid: true };
  },

  /**
   * Validate date format (YYYY-MM-DD)
   */
  dateFormat: (date: string, fieldName: string = 'Date'): ValidationResult => {
    const trimmed = date?.trim() || '';
    if (!trimmed) {
      return { isValid: false, error: `${fieldName} is required` };
    }
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(trimmed)) {
      return { isValid: false, error: `${fieldName} must be in YYYY-MM-DD format` };
    }
    const parsedDate = new Date(trimmed);
    if (isNaN(parsedDate.getTime())) {
      return { isValid: false, error: `${fieldName} is not a valid date` };
    }
    return { isValid: true };
  },

  /**
   * Validate date range (start date must be before end date)
   */
  dateRange: (startDate: string, endDate: string): ValidationResult => {
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    if (isNaN(start.getTime()) || isNaN(end.getTime())) {
      return { isValid: false, error: 'Invalid date(s)' };
    }
    
    if (start >= end) {
      return { isValid: false, error: 'Check-out date must be after check-in date' };
    }
    
    return { isValid: true };
  },

  /**
   * Validate password strength
   */
  password: (password: string): ValidationResult => {
    const trimmed = password?.trim() || '';
    if (!trimmed) {
      return { isValid: false, error: 'Password is required' };
    }
    if (trimmed.length < 8) {
      return { isValid: false, error: 'Password must be at least 8 characters' };
    }
    // Optional: Check for complexity (uncomment if needed)
    // const hasUpperCase = /[A-Z]/.test(trimmed);
    // const hasLowerCase = /[a-z]/.test(trimmed);
    // const hasNumber = /\d/.test(trimmed);
    // if (!hasUpperCase || !hasLowerCase || !hasNumber) {
    //   return { isValid: false, error: 'Password must contain uppercase, lowercase, and number' };
    // }
    return { isValid: true };
  },

  /**
   * Validate ID number format
   */
  idNumber: (idNum: string, fieldName: string = 'ID number'): ValidationResult => {
    const trimmed = idNum?.trim() || '';
    if (!trimmed) {
      return { isValid: false, error: `${fieldName} is required` };
    }
    // Alphanumeric with optional spaces/dashes
    if (!/^[A-Za-z0-9\s\-]+$/.test(trimmed)) {
      return { isValid: false, error: `${fieldName} contains invalid characters` };
    }
    if (trimmed.replace(/[\s\-]/g, '').length < 6) {
      return { isValid: false, error: `${fieldName} must be at least 6 characters` };
    }
    return { isValid: true };
  },

  /**
   * Validate number within range
   */
  range: (value: number, min: number, max: number, fieldName: string = 'Value'): ValidationResult => {
    if (isNaN(value)) {
      return { isValid: false, error: `${fieldName} must be a number` };
    }
    if (value < min || value > max) {
      return { isValid: false, error: `${fieldName} must be between ${min} and ${max}` };
    }
    return { isValid: true };
  },
};

/**
 * Sanitize input by trimming whitespace and converting to lowercase (optional)
 */
export const sanitizeInput = {
  /**
   * Trim whitespace
   */
  trim: (value: string): string => value?.trim() || '',

  /**
   * Trim and convert to lowercase
   */
  toLowerCase: (value: string): string => value?.trim().toLowerCase() || '',

  /**
   * Trim and convert to uppercase
   */
  toUpperCase: (value: string): string => value?.trim().toUpperCase() || '',

  /**
   * Remove all whitespace
   */
  removeWhitespace: (value: string): string => value?.replace(/\s/g, '') || '',

  /**
   * Remove non-numeric characters
   */
  numericOnly: (value: string): string => value?.replace(/\D/g, '') || '',

  /**
   * Format phone number
   */
  formatPhone: (value: string): string => {
    const numeric = value?.replace(/\D/g, '') || '';
    if (numeric.length === 10) {
      return `(${numeric.slice(0, 3)}) ${numeric.slice(3, 6)}-${numeric.slice(6)}`;
    }
    return value;
  },
};

/**
 * Validate multiple fields at once
 * Returns array of errors, or empty array if all valid
 */
export const validateFields = (
  validations: Array<{ validator: () => ValidationResult; field: string }>
): string[] => {
  const errors: string[] = [];
  validations.forEach(({ validator, field }) => {
    const result = validator();
    if (!result.isValid) {
      errors.push(result.error || `${field} is invalid`);
    }
  });
  return errors;
};

/**
 * Custom hook for form validation
 */
export const useFormValidation = () => {
  const validate = (validations: Array<() => ValidationResult>): string[] => {
    const errors: string[] = [];
    validations.forEach((validator) => {
      const result = validator();
      if (!result.isValid && result.error) {
        errors.push(result.error);
      }
    });
    return errors;
  };

  return { validate };
};
