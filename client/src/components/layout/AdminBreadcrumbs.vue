<script setup lang="ts">
defineProps<{
  currentLabel: string;
}>();
</script>

<template>
  <nav aria-label="Breadcrumb" class="text-xs mb-3">
    <ol class="flex items-center gap-2">
      <li>
        <RouterLink
          to="/admin"
          class="text-surface-mid hover:text-accent-blue transition-colors"
        >
          tools
        </RouterLink>
      </li>
      <li class="text-surface-muted" aria-hidden="true">/</li>
      <li>
        <span class="text-surface-light" aria-current="page">{{ currentLabel }}</span>
      </li>
    </ol>
  </nav>
</template>
