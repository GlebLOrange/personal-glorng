<script setup lang="ts">
import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminListToolbar from "@/components/admin/AdminListToolbar.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import NewsAdminArticleList from "@/components/news/NewsAdminArticleList.vue";
import NewsArticleDrawer from "@/components/news/NewsArticleDrawer.vue";
import NewsTabs from "@/components/news/NewsTabs.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { Card } from "@/components/ui/card";
import { newsStatusClass } from "@/constants/filterColors";
import { STATUS_FILTERS, useNewsAdmin } from "@/composables/useNewsAdmin";

const {
  canWrite,
  canManageSources,
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
  goToSources,
} = useNewsAdmin();
</script>

<template>
  <AdminPageLayout hub="tools" title="news" max-width="xl" back-to="/news">
    <NewsTabs />
    <AdminListToolbar v-if="!listLoading && !listError">
      <template #actions>
        <AdminFilterDropdown
          ref="filterDropdown"
          :has-active-filters="hasActiveFilters"
          :active-label="activeFilterLabel"
          :option-labels="STATUS_FILTERS.map((chip) => chip.label)"
          @clear="clearFilters"
        >
          <template #chips>
            <AdminFilterChip
              v-for="chip in STATUS_FILTERS"
              :key="chip.value"
              :label="chip.label"
              :active="statusFilter === chip.value"
              :color-class="newsStatusClass(chip.value)"
              @click="setStatusFilter(chip.value)"
            />
          </template>
        </AdminFilterDropdown>
        <template v-if="canManageSources">
          <ToolbarPillButton family="1xx" @click="goToSources"> sources </ToolbarPillButton>
        </template>
        <template v-if="canWrite">
          <ToolbarPillButton family="3xx" :disabled="actionLoading" @click="runIngest">
            run ingest
          </ToolbarPillButton>
        </template>
      </template>
      <ToolbarPillButton
        v-if="canWrite"
        family="2xx"
        class="ml-auto"
        :disabled="actionLoading"
        @click="openCreate"
      >
        + article
      </ToolbarPillButton>
    </AdminListToolbar>

    <section v-if="listLoading" class="space-y-3" aria-busy="true" aria-label="Loading news">
      <Card v-for="i in 5" :key="i" class="h-36 animate-pulse" />
    </section>

    <ErrorState v-else-if="listError" :message="listError" show-retry @retry="reloadAdminNews" />

    <NewsAdminArticleList
      v-else-if="articles.length"
      :articles="articles"
      :can-write="canWrite"
      :action-loading="actionLoading"
      @edit="openEditableArticle"
      @set-status="setStatus"
      @repost="repost"
    />

    <EmptyState
      v-else-if="!listLoading && !listError"
      title="no articles"
      :description="emptyFilterDescription"
    />

    <AdminListFooter
      v-if="!listLoading && !listError"
      :total="total"
      :page="page"
      :total-pages="totalPages"
      :has-next-page="hasNextPage"
      :has-previous-page="hasPreviousPage"
      :loading="listLoading"
      item-label="articles"
      aria-label="News pagination"
      @first="goToPage(1)"
      @prev="goToPage(page - 1)"
      @next="goToPage(page + 1)"
      @last="goToPage(totalPages)"
    />

    <NewsArticleDrawer
      v-if="canWrite"
      :open="drawerOpen"
      :mode="drawerMode"
      :form="form"
      :sources="sources"
      :loading="actionLoading"
      @update:form="updateForm"
      @close="closeDrawer"
      @delete="deleteDrawerArticle"
      @save="saveDrawer"
    />
  </AdminPageLayout>
</template>
