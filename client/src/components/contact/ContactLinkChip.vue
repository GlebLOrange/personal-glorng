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
    class="interactive-surface inline-flex items-center gap-2 px-5 py-3 min-h-11 text-base text-surface-sage"
  >
    <ContactIcon :id="link.id" class="size-4 shrink-0" />
    {{ link.label }}
    <span v-if="isExternal" class="sr-only">(opens in new tab)</span>
  </a>
</template>
