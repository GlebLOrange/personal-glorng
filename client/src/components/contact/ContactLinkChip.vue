<script setup lang="ts">
import ContactIcon from "@/components/contact/ContactIcon.vue";
import type { ContactLink } from "@/constants/contactMeta";

defineProps<{
  link: ContactLink;
}>();
</script>

<template>
  <a
    :href="link.href"
    target="_blank"
    rel="noopener noreferrer"
    class="interactive-surface inline-flex items-center gap-2 px-4 py-2 text-sm text-surface-mid"
  >
    <ContactIcon :id="link.id" class="size-4 shrink-0" />
    {{ link.label }}
  </a>
</template>
