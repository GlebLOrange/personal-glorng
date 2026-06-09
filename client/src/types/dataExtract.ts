export type DataExtractFormat = "csv" | "json" | "xml";

export type XmlExtractMode = "rows" | "tree";

export interface ExtractionResult {
  format: DataExtractFormat;
  records: Record<string, unknown>[];
  meta: Record<string, unknown>;
}
