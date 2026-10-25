<script setup lang="ts">
import MaintenanceJobActions from "@/components/admin/MaintenanceJobActions.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
</script>

<template>
  <AdminPageLayout
    hub="admin"
    title="db maintenance"
    back-to="/admin"
    description="run backup, stale check, calendar sync, cleanup, or seed. each finished job emails the operator."
  >
    <MaintenanceJobActions mode="page" />
  </AdminPageLayout>
</template>
