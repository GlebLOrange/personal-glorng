<script setup lang="ts">
import MaintenanceJobActions from "@/components/admin/MaintenanceJobActions.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import { usePermissions } from "@/composables/usePermissions";

const { isSuperuser } = usePermissions();
</script>

<template>
  <AdminPageLayout title="admin" hub="tools" max-width="5xl" back-to="/tools">
    <div v-if="isSuperuser" class="page-tool-actions mb-8">
      <MaintenanceJobActions mode="hub" />
    </div>
    <p
      v-else
      class="rounded-lg border border-surface-border bg-surface-card px-3 py-2 text-sm text-surface-sage"
      role="status"
    >
      Admin tools live on the tools page for site owners. Ask the site owner if you need access.
    </p>
  </AdminPageLayout>
</template>
