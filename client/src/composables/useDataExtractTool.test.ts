import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  batchLabel,
  buildDataExtractQueryParams,
  formatDataExtractCell,
  useDataExtractTool,
} from "@/composables/useDataExtractTool";
import { useAuthStore } from "@/stores/auth";
import { SUPERUSER_PERMISSION } from "@/utils/permissions";
import type { ImportBatchSummary } from "@/types/dataExtract";
import type { UserResponse } from "@/types";

vi.mock("@/composables/useApi", () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

vi.mock("@/composables/useApiAction", () => ({
  useApiAction: () => ({
    loading: { value: false },
    run: vi.fn(async (fn: () => Promise<unknown>) => fn()),
  }),
}));

vi.mock("@/composables/useClipboard", () => ({
  useClipboard: () => ({
    copy: vi.fn(),
  }),
}));

import { api } from "@/composables/useApi";

function makeUser(permissions: string[]): UserResponse {
  return {
    id: "1",
    email: "a@b.c",
    permissions,
    is_verified: true,
    display_name: "User",
    timezone: "UTC",
    preferences: {},
    created_at: "2026-01-01T00:00:00Z",
  };
}

function makeBatch(overrides: Partial<ImportBatchSummary> = {}): ImportBatchSummary {
  return {
    id: 1,
    filename: "a.pipe",
    format: "delimited",
    profile: "pipe_embed",
    status: "completed",
    row_count: 4,
    error_count: 0,
    imported_by: 1,
    promoted_count: 0,
    meta: {},
    ...overrides,
  };
}

describe("buildDataExtractQueryParams", () => {
  it("omits format for auto with custom profile", () => {
    const params = buildDataExtractQueryParams({
      formatChoice: "auto",
      profileChoice: "custom",
      fieldDelimiter: "|",
      listDelimiter: ";",
      rowTag: "",
      xmlMode: "rows",
      showDelimitedOptions: true,
      showXmlOptions: true,
    });
    expect(params.get("format")).toBeNull();
    expect(params.get("field_delimiter")).toBe("|");
    expect(params.get("list_delimiter")).toBe(";");
    expect(params.get("xml_mode")).toBe("rows");
  });

  it("sets delimited format for pipe_embed under auto", () => {
    const params = buildDataExtractQueryParams({
      formatChoice: "auto",
      profileChoice: "pipe_embed",
      fieldDelimiter: "|",
      listDelimiter: ";",
      rowTag: "",
      xmlMode: "rows",
      showDelimitedOptions: true,
      showXmlOptions: false,
    });
    expect(params.get("format")).toBe("delimited");
    expect(params.get("profile")).toBe("pipe_embed");
    expect(params.get("field_delimiter")).toBeNull();
  });

  it("includes explicit format and xml row tag", () => {
    const params = buildDataExtractQueryParams({
      formatChoice: "xml",
      profileChoice: "custom",
      fieldDelimiter: "|",
      listDelimiter: ";",
      rowTag: "item",
      xmlMode: "tree",
      showDelimitedOptions: false,
      showXmlOptions: true,
    });
    expect(params.get("format")).toBe("xml");
    expect(params.get("row_tag")).toBe("item");
    expect(params.get("xml_mode")).toBe("tree");
  });
});

describe("formatDataExtractCell / batchLabel", () => {
  it("formats cells and batch labels", () => {
    expect(formatDataExtractCell(null)).toBe("");
    expect(formatDataExtractCell({ a: 1 })).toBe('{"a":1}');
    expect(formatDataExtractCell("x")).toBe("x");

    const batch = makeBatch({
      id: 7,
      filename: "rows.pipe",
      promoted_count: 2,
    });
    expect(batchLabel(batch)).toContain("#7");
    expect(batchLabel(batch)).toContain("2 promoted");
  });
});

describe("useDataExtractTool", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
    vi.mocked(api.get).mockResolvedValue({
      data: { items: [], total: 0, pages: 0, page: 1, per_page: 20 },
    });
  });

  it("blocks promote unless write + pipe_embed + rows", async () => {
    const auth = useAuthStore();
    auth.user = makeUser(["data-extract:read"]);

    const tool = useDataExtractTool();
    await Promise.resolve();

    tool.selectedBatchId.value = 1;
    tool.batchHistory.value = [makeBatch()];
    expect(tool.canPromoteSelected.value).toBe(false);

    auth.user = makeUser(["data-extract:write"]);
    expect(tool.canPromoteSelected.value).toBe(true);

    tool.batchHistory.value[0]!.profile = "custom";
    expect(tool.canPromoteSelected.value).toBe(false);
  });

  it("extractFile posts multipart and stores result", async () => {
    const auth = useAuthStore();
    auth.user = makeUser([SUPERUSER_PERMISSION]);

    vi.mocked(api.post).mockResolvedValue({
      data: {
        format: "csv",
        records: [{ a: "1" }],
        meta: { row_count: 1 },
      },
    });

    const tool = useDataExtractTool();
    tool.selectedFile.value = new File(["a,b\n1,2"], "t.csv", { type: "text/csv" });
    await tool.extractFile();

    expect(api.post).toHaveBeenCalled();
    expect(tool.result.value?.format).toBe("csv");
    expect(tool.result.value?.records).toEqual([{ a: "1" }]);
    expect(tool.importResult.value).toBeNull();
  });
});
