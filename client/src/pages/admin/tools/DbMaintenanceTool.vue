<script setup lang="ts">
import MaintenanceJobActions from "@/components/admin/MaintenanceJobActions.vue";
import PageShell from "@/components/layout/PageShell.vue";
</script>

<template>
  <PageShell
    title="db maintenance"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'db maintenance' }]"
    back-to="/tools"
    max-width="5xl"
    body-width="column"
    description="run backup, stale check, calendar sync, cleanup, or seed. each finished job emails the operator."
  >
    <div class="page-tool-actions">
      <MaintenanceJobActions mode="page" />
    </div>
  </PageShell>
</template>
