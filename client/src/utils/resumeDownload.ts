import { getApiErrorMessageFromBlob } from "@/types/api";

export type ResumeDownloadKind = "pdf" | "markdown" | "json";

const DOWNLOAD_SPECS: Record<
  ResumeDownloadKind,
  { path: string; accept: string; filename: string; contentTypeIncludes: string }
> = {
  pdf: {
    path: "/resume/pdf",
    accept: "application/pdf",
    filename: "gleb.y.cv.pdf",
    contentTypeIncludes: "application/pdf",
  },
  markdown: {
    path: "/resume/markdown",
    accept: "text/markdown",
    filename: "gleb.y.cv.md",
    contentTypeIncludes: "text/markdown",
  },
  json: {
    path: "/resume/json",
    accept: "application/json",
    filename: "gleb.y.cv.json",
    contentTypeIncludes: "application/json",
  },
};

/** Fetch a resume export blob and trigger a browser download. */
export async function downloadResumeExport(kind: ResumeDownloadKind): Promise<void> {
  const spec = DOWNLOAD_SPECS[kind];
  const { api } = await import("@/composables/useApi");
  const response = await api.get<Blob>(spec.path, {
    responseType: "blob",
    headers: { Accept: spec.accept },
  });
  const contentType = String(
    response.headers["content-type"] ?? response.data.type ?? "",
  ).toLowerCase();
  if (!contentType.includes(spec.contentTypeIncludes)) {
    throw new Error(`CV download did not return ${spec.contentTypeIncludes}`);
  }

  const url = URL.createObjectURL(response.data);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = spec.filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

export async function resumeDownloadErrorMessage(
  err: unknown,
  fallback: string,
): Promise<string> {
  return getApiErrorMessageFromBlob(err, fallback);
}
