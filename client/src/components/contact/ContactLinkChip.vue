<script setup lang="ts">
import ContactIcon from "@/components/contact/ContactIcon.vue";
import type { ContactLink } from "@/constants/contactMeta";
import { computed } from "vue";

const props = defineProps<{
  link: ContactLink;
}>();

const isExternal = computed(() => /^https?:/i.test(props.link.href));
</script>

<template>
  <a
    :href="link.href"
    :target="isExternal ? '_blank' : undefined"
    :rel="isExternal ? 'noopener noreferrer' : undefined"
    class="contact-link-chip inline-flex h-10 items-center gap-1.5 rounded-lg border border-transparent bg-surface-card px-4 text-sm text-surface-sage transition-colors hover:border-accent-blue/40 hover:bg-accent-blue/15 focus-visible:border-accent-blue/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
  >
    <ContactIcon :id="link.id" class="size-4 shrink-0" />
    {{ link.label }}
    <span v-if="isExternal" class="sr-only">(opens in new tab)</span>
  </a>
</template>
