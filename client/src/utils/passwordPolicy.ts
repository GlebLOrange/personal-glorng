export const PASSWORD_MIN_LENGTH = 12;

const PASSWORD_PATTERN = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{12,}$/;

export interface PasswordStrength {
  score: number;
  label: string;
  valid: boolean;
  message: string;
}

export function validatePassword(password: string): string | null {
  if (!PASSWORD_PATTERN.test(password)) {
    return "Password must be 12+ chars with uppercase, lowercase, digit, and special";
  }
  return null;
}

export function passwordStrength(password: string): PasswordStrength {
  if (!password) {
    return { score: 0, label: "empty", valid: false, message: "Enter a password" };
  }

  let score = 0;
  if (password.length >= 12) score += 1;
  if (password.length >= 16) score += 1;
  if (/[a-z]/.test(password)) score += 1;
  if (/[A-Z]/.test(password)) score += 1;
  if (/\d/.test(password)) score += 1;
  if (/[^\w\s]/.test(password)) score += 1;

  const error = validatePassword(password);
  if (error) {
    const label = score <= 2 ? "weak" : score <= 4 ? "fair" : "good";
    return { score, label, valid: false, message: error };
  }

  const label = score >= 6 ? "strong" : "good";
  return { score, label, valid: true, message: "Password meets requirements" };
}
