<script setup lang="ts">
/**
 * Monoline catalog icons for admin/tools tiles.
 * Mapped by platform service slug; unknown slugs get a plain square.
 */
defineProps<{
  slug: string;
}>();
</script>

<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.75"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <!-- tasks: checklist -->
    <template v-if="slug === 'tasks'">
      <rect x="4" y="4" width="16" height="16" rx="2" />
      <path d="M8 12l2.5 2.5L16 9" />
    </template>

    <!-- email: envelope -->
    <template v-else-if="slug === 'email'">
      <rect x="3" y="5" width="18" height="14" rx="2" />
      <path d="m3 7 9 6 9-6" />
    </template>

    <!-- expenses: coin -->
    <template v-else-if="slug === 'expenses'">
      <circle cx="12" cy="12" r="8" />
      <path d="M12 7v10M14.5 9.5c0-1.1-1.1-2-2.5-2s-2.5.9-2.5 2 1.1 2 2.5 2 2.5.9 2.5 2-1.1 2-2.5 2-2.5-.9-2.5-2" />
    </template>

    <!-- recipes: bowl + utensil -->
    <template v-else-if="slug === 'recipes'">
      <path d="M4 11h16v1a8 8 0 0 1-16 0v-1Z" />
      <path d="M8 11V8a2 2 0 0 1 2-2h0" />
      <path d="M16 4v4" />
    </template>

    <!-- news: newspaper -->
    <template v-else-if="slug === 'news'">
      <path d="M4 6h12a2 2 0 0 1 2 2v10H6a2 2 0 0 1-2-2V6Z" />
      <path d="M18 8h1a1 1 0 0 1 1 1v7a2 2 0 0 1-2 2h-1" />
      <path d="M8 10h6M8 13h6M8 16h3" />
    </template>

    <!-- file-share: share nodes -->
    <template v-else-if="slug === 'file-share'">
      <circle cx="18" cy="5" r="2.5" />
      <circle cx="6" cy="12" r="2.5" />
      <circle cx="18" cy="19" r="2.5" />
      <path d="M8.2 10.8 15.8 6.2M8.2 13.2l7.6 4.6" />
    </template>

    <!-- url-shortener: link chain -->
    <template v-else-if="slug === 'url-shortener'">
      <path d="M10 13a5 5 0 0 0 7.5.5l2-2a5 5 0 0 0-7.1-7.1l-1.1 1.1" />
      <path d="M14 11a5 5 0 0 0-7.5-.5l-2 2a5 5 0 0 0 7.1 7.1l1.1-1.1" />
    </template>

    <!-- calculator: keypad -->
    <template v-else-if="slug === 'calculator'">
      <rect x="5" y="3" width="14" height="18" rx="2" />
      <path d="M8 7h8M8 12h.01M12 12h.01M16 12h.01M8 16h.01M12 16h.01M16 16h.01" />
    </template>

    <!-- password-generator: key -->
    <template v-else-if="slug === 'password-generator'">
      <circle cx="8" cy="12" r="4" />
      <path d="M12 12h9M18 12v3M21 12v2" />
    </template>

    <!-- vid-download: play + down -->
    <template v-else-if="slug === 'vid-download'">
      <path d="M6 5.5v13l11-6.5L6 5.5Z" />
      <path d="M18 14v5M16 17l2 2 2-2" />
    </template>

    <!-- ai-chat: bubble + spark -->
    <template v-else-if="slug === 'ai-chat'">
      <path d="M4 6a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H9l-3 3v-3H6a2 2 0 0 1-2-2V6Z" />
      <path d="M18.5 4.5 19 6l1.5.5L19 7l-.5 1.5L18 7l-1.5-.5L18 6l.5-1.5Z" />
    </template>

    <!-- data-extract: table + arrow -->
    <template v-else-if="slug === 'data-extract'">
      <rect x="3" y="4" width="12" height="16" rx="1" />
      <path d="M3 9h12M3 14h12M8 4v16M17 12h4M19 10v4" />
    </template>

    <!-- feedback: speech bubble -->
    <template v-else-if="slug === 'feedback'">
      <path d="M4 5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H9l-4 4v-4H6a2 2 0 0 1-2-2V5Z" />
      <path d="M8 9h8M8 12h5" />
    </template>

    <!-- news-sources: RSS arcs -->
    <template v-else-if="slug === 'news-sources'">
      <circle cx="6" cy="18" r="1.5" fill="currentColor" stroke="none" />
      <path d="M4 11a9 9 0 0 1 9 9" />
      <path d="M4 6a14 14 0 0 1 14 14" />
    </template>

    <!-- audit: shield check -->
    <template v-else-if="slug === 'audit'">
      <path d="M12 3 5 6v5c0 5 3 8 7 10 4-2 7-5 7-10V6l-7-3Z" />
      <path d="M9.5 12l2 2 3.5-3.5" />
    </template>

    <!-- app-logs: stacked lines -->
    <template v-else-if="slug === 'app-logs'">
      <path d="M5 7h14M5 12h14M5 17h10" />
    </template>

    <!-- search: magnifying glass -->
    <template v-else-if="slug === 'search'">
      <circle cx="11" cy="11" r="6" />
      <path d="m20 20-3.5-3.5" />
    </template>

    <!-- api-docs: braces -->
    <template v-else-if="slug === 'api-docs'">
      <path d="M9 5c-2 0-3 1.5-3 3.5S5 12 5 12s1 1.5 1 3.5S7 19 9 19" />
      <path d="M15 5c2 0 3 1.5 3 3.5S19 12 19 12s-1 1.5-1 3.5S17 19 15 19" />
    </template>

    <!-- users: person -->
    <template v-else-if="slug === 'users'">
      <circle cx="12" cy="8" r="3.5" />
      <path d="M5 20c1.5-3.5 4-5 7-5s5.5 1.5 7 5" />
    </template>

    <!-- sync: circular arrows -->
    <template v-else-if="slug === 'sync'">
      <path d="M21 12a9 9 0 0 0-15.5-6.4" />
      <path d="M5.5 5.6V9h3.4" />
      <path d="M3 12a9 9 0 0 0 15.5 6.4" />
      <path d="M18.5 18.4V15h-3.4" />
    </template>

    <!-- location: map pin -->
    <template v-else-if="slug === 'location'">
      <path d="M12 21s-6-5.2-6-10a6 6 0 1 1 12 0c0 4.8-6 10-6 10Z" />
      <circle cx="12" cy="11" r="2.25" />
    </template>

    <!-- fallback -->
    <template v-else>
      <rect x="5" y="5" width="14" height="14" rx="2" />
    </template>
  </svg>
</template>
