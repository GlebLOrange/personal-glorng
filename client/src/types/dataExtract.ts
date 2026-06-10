export type DataExtractFormat = "csv" | "json" | "xml" | "delimited";

export type XmlExtractMode = "rows" | "tree";

export type DelimitedProfile = "pipe_embed" | "custom";

export interface ExtractionResult {
  format: DataExtractFormat;
  records: Record<string, unknown>[];
  meta: Record<string, unknown>;
}

export interface ImportRowError {
  line_number?: number | null;
  message: string;
  raw_line?: string | null;
}

export interface ImportResult {
  batch_id: number;
  format: string;
  profile?: string | null;
  row_count: number;
  error_count: number;
  preview: Record<string, unknown>[];
  errors: ImportRowError[];
}

export interface ImportBatchSummary {
  id: number;
  filename: string;
  format: string;
  profile?: string | null;
  status: "completed" | "partial" | "failed";
  row_count: number;
  error_count: number;
  imported_by: number;
  promoted_count: number;
  promoted_at?: string | null;
  meta: Record<string, unknown>;
}

export interface ImportBatchList {
  items: ImportBatchSummary[];
  total: number;
}

export interface ImportBatchDetail {
  batch: ImportBatchSummary;
  preview_rows: Array<{
    id: number;
    batch_id: number;
    row_index: number;
    fields: Record<string, unknown>;
    raw_line?: string | null;
    error?: string | null;
  }>;
}

export interface PromoteBatchResult {
  batch_id: number;
  promoted: number;
  skipped: number;
  errors: string[];
}
