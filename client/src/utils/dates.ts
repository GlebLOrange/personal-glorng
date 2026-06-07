function localYearMonth(d: Date): { year: number; month: string } {
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  return { year, month };
}

/** Local calendar date as YYYY-MM-DD. */
export function isoDateLocal(d: Date = new Date()): string {
  const { year, month } = localYearMonth(d);
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

/** Local calendar month as YYYY-MM (HTML month input value). */
export function monthValueLocal(d: Date = new Date()): string {
  const { year, month } = localYearMonth(d);
  return `${year}-${month}`;
}

/** Value for HTML datetime-local inputs (local time, no timezone suffix). */
export function datetimeLocalValue(d: Date = new Date()): string {
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  const hours = String(d.getHours()).padStart(2, "0");
  const minutes = String(d.getMinutes()).padStart(2, "0");
  return `${year}-${month}-${day}T${hours}:${minutes}`;
}

const ISO_DATE_RE = /^\d{4}-\d{2}-\d{2}$/;
const MONTH_VALUE_RE = /^\d{4}-(0[1-9]|1[0-2])$/;
const DATETIME_LOCAL_RE = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/;

/** Return true when value is a valid YYYY-MM-DD calendar date. */
export function isValidIsoDate(value: string): boolean {
  if (!ISO_DATE_RE.test(value)) {
    return false;
  }
  const parsed = new Date(`${value}T00:00:00`);
  if (Number.isNaN(parsed.getTime())) {
    return false;
  }
  return isoDateLocal(parsed) === value;
}

/** Return true when value is a valid YYYY-MM month selector value. */
export function isValidMonthValue(value: string): boolean {
  return MONTH_VALUE_RE.test(value);
}

/** Return true when value matches datetime-local input format. */
export function isValidDatetimeLocal(value: string): boolean {
  if (!DATETIME_LOCAL_RE.test(value)) {
    return false;
  }
  const parsed = new Date(value);
  return !Number.isNaN(parsed.getTime());
}

/** Parse datetime-local value to ISO string, or null when invalid. */
export function parseDatetimeLocalToIso(value: string): string | null {
  if (!isValidDatetimeLocal(value)) {
    return null;
  }
  return new Date(value).toISOString();
}

/** Return true when both dates are valid and from is not after to. */
export function isValidDateRange(from: string, to: string): boolean {
  if (!isValidIsoDate(from) || !isValidIsoDate(to)) {
    return false;
  }
  return from <= to;
}

/** Inclusive calendar bounds for a YYYY-MM month, or null when invalid. */
export function monthDateBounds(month: string): { from: string; to: string } | null {
  if (!isValidMonthValue(month)) {
    return null;
  }
  const [year, mon] = month.split("-").map(Number);
  const lastDay = new Date(year, mon, 0).getDate();
  const mm = String(mon).padStart(2, "0");
  return {
    from: `${year}-${mm}-01`,
    to: `${year}-${mm}-${String(lastDay).padStart(2, "0")}`,
  };
}
