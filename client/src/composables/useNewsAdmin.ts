import { computed, onMounted, ref, useTemplateRef, watch } from "vue";

import {
  NEWS_STATUS_META,
  NEWS_SUMMARY_MAX_LENGTH,
  NEWS_TAG_LIMIT,
  NEWS_TAG_SET,
  NEWS_TITLE_MAX_LENGTH,
} from "@/constants/news";
import { useNews } from "@/composables/useNews";
import { useNotify } from "@/composables/useNotify";
import { usePermissions } from "@/composables/usePermissions";
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";
import type {
  NewsArticle,
  NewsArticleCreate,
  NewsArticleFormData,
  NewsArticleUpdate,
  NewsStatus,
} from "@/types";
import { normalizeHttpUrl, titleFromNewsLink } from "@/utils/newsForms";

export type DrawerMode = "create" | "edit";
export type StatusFilter = "" | NewsStatus;

export const STATUS_FILTERS: { label: string; value: NewsStatus }[] = (
  Object.entries(NEWS_STATUS_META) as [NewsStatus, (typeof NEWS_STATUS_META)[NewsStatus]][]
).map(([value, meta]) => ({ label: meta.label, value }));

export function emptyForm(): NewsArticleFormData {
  return {
    slug: "",
    status: "draft",
    source_id: null,
    source_name: "",
    source_url: "",
    source_feed_url: "",
    source_published_at: "",
    original_title: "",
    title: "",
    summary: "",
    bullets: [],
    tags: "world",
    language: "en",
    published_at: "",
    telegram_message_id: "",
    ai_model: "",
    ai_input_hash: "",
    ingest_error: "",
  };
}

export function formFromArticle(article: NewsArticle): NewsArticleFormData {
  return {
    slug: article.slug,
    status: article.status,
    source_id: article.source_id,
    source_name: article.source_name,
    source_url: article.source_url,
    source_feed_url: article.source_feed_url,
    source_published_at: article.source_published_at?.slice(0, 16) ?? "",
    original_title: article.original_title,
    title: article.title,
    summary: article.summary,
    bullets: [],
    tags: article.tags.join(", "),
    language: article.language,
    published_at: article.published_at?.slice(0, 16) ?? "",
    telegram_message_id: article.telegram_message_id?.toString() ?? "",
    ai_model: article.ai_model ?? "",
    ai_input_hash: article.ai_input_hash ?? "",
    ingest_error: article.ingest_error ?? "",
  };
}

export function useNewsAdmin() {
  const { can } = usePermissions();
  const { toast } = useNotify();
  const canWrite = computed(() => can("news", "write"));
  const drawerOpen = ref(false);
  const drawerMode = ref<DrawerMode>("create");
  const editingArticleId = ref<number | null>(null);
  const form = ref<NewsArticleFormData>(emptyForm());
  const lastAutoTitle = ref<string | null>(null);
  const metadataRequestId = ref(0);
  const statusFilter = ref<StatusFilter>("");
  const filterDropdownRef = useTemplateRef<{ close: () => void }>("filterDropdown");

  const {
    articles,
    sources,
    page,
    total,
    totalPages,
    listLoading,
    listError,
    actionLoading,
    hasNextPage,
    hasPreviousPage,
    loadNews,
    loadSources,
    goToPage,
    ingestNews,
    loadArticleMetadata,
    createArticle,
    updateArticle,
    deleteArticle,
    repostToTelegram,
  } = useNews();

  const hasActiveFilters = computed(() => Boolean(statusFilter.value));
  const activeFilterLabel = computed(
    () => STATUS_FILTERS.find((chip) => chip.value === statusFilter.value)?.label,
  );

  function setStatusFilter(next: StatusFilter): void {
    statusFilter.value = next;
    page.value = 1;
    filterDropdownRef.value?.close();
    void loadAdminNews();
  }

  function clearFilters(): void {
    statusFilter.value = "";
    page.value = 1;
    filterDropdownRef.value?.close();
    void loadAdminNews();
  }

  const emptyFilterDescription = computed(() => {
    if (!statusFilter.value) {
      return "no news articles yet. run ingestion after configuring trusted sources.";
    }
    return `no ${statusFilter.value} articles match this filter.`;
  });

  async function reloadAdminNews(): Promise<void> {
    await loadNews({ admin: true, status: statusFilter.value || undefined });
  }

  useScrollListFingerprint(
    () => `${statusFilter.value}:${page.value}:${total.value}:${articles.value[0]?.id ?? ""}`,
  );

  function parsedTags(): string[] {
    return form.value.tags
      .split(",")
      .map((tag) => tag.trim())
      .filter(Boolean);
  }

  function canReplaceAutoValue(currentValue: string, lastAutoValue: string | null): boolean {
    return !currentValue.trim() || (lastAutoValue !== null && currentValue === lastAutoValue);
  }

  function normalizedDateTime(value: string): string | null {
    if (!value.trim()) return null;
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? null : parsed.toISOString();
  }

  function normalizedSourcePublishedAt(): string | null {
    return normalizedDateTime(form.value.source_published_at);
  }

  function optionalText(value: string): string | null {
    const trimmed = value.trim();
    return trimmed || null;
  }

  function sourcePublishedAtPayload(): string | null {
    return normalizedSourcePublishedAt();
  }

  function sourceUrlPayload(): string | null {
    return normalizeHttpUrl(form.value.source_url);
  }

  function sourceFeedUrlPayload(): string | undefined {
    const sourceFeedUrl = normalizeHttpUrl(form.value.source_feed_url);
    return sourceFeedUrl ?? undefined;
  }

  function slugPayload(): string | undefined {
    const slug = form.value.slug.trim();
    return slug || undefined;
  }

  function applySource(sourceId: number | null): void {
    const source = sources.value.find((item) => item.id === sourceId);
    form.value = {
      ...form.value,
      source_id: sourceId,
      source_name: source?.name ?? form.value.source_name,
      source_feed_url: source?.feed_url ?? form.value.source_feed_url,
    };
  }

  async function hydrateFromSourceUrl(sourceUrl: string): Promise<void> {
    const requestId = metadataRequestId.value + 1;
    metadataRequestId.value = requestId;
    const metadata = await loadArticleMetadata(sourceUrl);
    if (!metadata || requestId !== metadataRequestId.value) return;
    await loadSources();
    const nextValues: Partial<NewsArticleFormData> = {
      source_url: metadata.source_url,
      source_id: metadata.source_id,
      source_name: metadata.source_name,
      source_feed_url: metadata.source_feed_url,
    };
    if (metadata.title && canReplaceAutoValue(form.value.title, lastAutoTitle.value)) {
      nextValues.title = metadata.title;
      lastAutoTitle.value = metadata.title;
    }
    form.value = { ...form.value, ...nextValues };
  }

  function dateIsInvalid(value: string, normalizedValue: string | null): boolean {
    return Boolean(value.trim()) && normalizedValue === null;
  }

  function withSourceUrlDefaults(nextForm: NewsArticleFormData): NewsArticleFormData {
    const sourceUrl = normalizeHttpUrl(nextForm.source_url);
    if (!sourceUrl) return { ...nextForm, source_feed_url: "" };

    const nextValues: Partial<NewsArticleFormData> = {
      source_feed_url: sourceUrl,
    };
    const autoTitle = titleFromNewsLink(sourceUrl);
    if (autoTitle && canReplaceAutoValue(nextForm.title, lastAutoTitle.value)) {
      nextValues.title = autoTitle;
      lastAutoTitle.value = autoTitle;
    }
    return { ...nextForm, ...nextValues };
  }

  async function updateForm(nextForm: NewsArticleFormData): Promise<void> {
    if (nextForm.source_id !== form.value.source_id) {
      applySource(nextForm.source_id);
      return;
    }
    if (nextForm.source_url !== form.value.source_url) {
      const nextWithDefaults = withSourceUrlDefaults(nextForm);
      form.value = nextWithDefaults;
      const sourceUrl = normalizeHttpUrl(nextWithDefaults.source_url);
      if (sourceUrl) await hydrateFromSourceUrl(sourceUrl);
      return;
    }
    form.value = nextForm;
  }

  function validateForm(): boolean {
    const title = form.value.title.trim();
    const summary = form.value.summary.trim();
    const tags = parsedTags();

    if (!title) {
      toast("Title is required", "error");
      return false;
    }
    if (title.length > NEWS_TITLE_MAX_LENGTH) {
      toast(`Title must be ${NEWS_TITLE_MAX_LENGTH} characters or fewer`, "error");
      return false;
    }
    if (!summary) {
      toast("Summary is required", "error");
      return false;
    }
    if (summary.length > NEWS_SUMMARY_MAX_LENGTH) {
      toast(`Summary must be ${NEWS_SUMMARY_MAX_LENGTH} characters or fewer`, "error");
      return false;
    }
    const sourceUrl = sourceUrlPayload();
    if (!sourceUrl) {
      toast("Source URL must start with http:// or https://", "error");
      return false;
    }
    if (tags.length < 1) {
      toast("Add at least one tag", "error");
      return false;
    }
    if (tags.length > NEWS_TAG_LIMIT) {
      toast(`Choose no more than ${NEWS_TAG_LIMIT} tags`, "error");
      return false;
    }
    if (tags.some((tag) => !NEWS_TAG_SET.has(tag))) {
      toast("Choose only supported news tags", "error");
      return false;
    }
    if (dateIsInvalid(form.value.source_published_at, normalizedSourcePublishedAt())) {
      toast("Source published date is invalid", "error");
      return false;
    }
    return true;
  }

  function buildCreatePayload(): NewsArticleCreate {
    const sourceUrl = sourceUrlPayload() ?? form.value.source_url.trim();
    const title = form.value.title.trim();
    const originalTitle = form.value.original_title.trim() || title;
    return {
      status: form.value.status,
      source_id: form.value.source_id,
      source_name: optionalText(form.value.source_name) ?? undefined,
      source_url: sourceUrl,
      source_feed_url: sourceFeedUrlPayload(),
      source_published_at: sourcePublishedAtPayload(),
      original_title: originalTitle,
      title,
      summary: form.value.summary.trim(),
      tags: parsedTags(),
      language: form.value.language.trim() || "en",
    };
  }

  function buildUpdatePayload(): NewsArticleUpdate {
    return {
      ...buildCreatePayload(),
      slug: slugPayload(),
    };
  }

  async function loadAdminNews(): Promise<void> {
    await loadNews({ admin: true, status: statusFilter.value || undefined });
  }

  async function runIngest(): Promise<void> {
    await ingestNews();
    await reloadAdminNews();
  }

  async function setStatus(articleId: number, status: NewsStatus): Promise<void> {
    await updateArticle(articleId, { status });
    await reloadAdminNews();
  }

  async function repost(articleId: number): Promise<void> {
    await repostToTelegram(articleId);
    await reloadAdminNews();
  }

  function openCreate(): void {
    drawerMode.value = "create";
    editingArticleId.value = null;
    lastAutoTitle.value = null;
    form.value = emptyForm();
    drawerOpen.value = true;
  }

  function openEdit(article: NewsArticle): void {
    drawerMode.value = "edit";
    editingArticleId.value = article.id;
    lastAutoTitle.value = null;
    form.value = formFromArticle(article);
    drawerOpen.value = true;
  }

  function openEditableArticle(article: NewsArticle): void {
    if (!canWrite.value) return;
    openEdit(article);
  }

  function closeDrawer(): void {
    drawerOpen.value = false;
    editingArticleId.value = null;
  }

  async function saveDrawer(): Promise<void> {
    if (!validateForm()) return;
    if (drawerMode.value === "create") {
      const created = await createArticle(buildCreatePayload());
      if (!created) return;
    } else if (editingArticleId.value) {
      const updated = await updateArticle(editingArticleId.value, buildUpdatePayload());
      if (!updated) return;
    }
    closeDrawer();
    await reloadAdminNews();
  }

  async function deleteDrawerArticle(): Promise<void> {
    if (!editingArticleId.value) return;
    const title = form.value.title.trim() || "this article";
    if (!window.confirm(`Delete "${title}"? This cannot be undone.`)) return;
    if (!(await deleteArticle(editingArticleId.value))) return;
    closeDrawer();
    await reloadAdminNews();
  }

  onMounted(async () => {
    await Promise.all([reloadAdminNews(), loadSources()]);
  });

  watch(page, () => {
    void loadAdminNews();
  });

  return {
    canWrite,
    drawerOpen,
    drawerMode,
    form,
    statusFilter,
    articles,
    sources,
    page,
    total,
    totalPages,
    listLoading,
    listError,
    actionLoading,
    hasNextPage,
    hasPreviousPage,
    hasActiveFilters,
    activeFilterLabel,
    emptyFilterDescription,
    setStatusFilter,
    clearFilters,
    reloadAdminNews,
    goToPage,
    runIngest,
    setStatus,
    repost,
    openCreate,
    openEditableArticle,
    closeDrawer,
    updateForm,
    saveDrawer,
    deleteDrawerArticle,
  };
}
