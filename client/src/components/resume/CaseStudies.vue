<script setup lang="ts">
import { RouterLink } from "vue-router";

import { Card } from "@/components/ui/card";
import { colorThemeResolved } from "@/composables/useColorTheme";
import { projectArtForSlug } from "@/constants/projectArt";
import type { Project } from "@/types";

defineProps<{
  projects: Project[];
}>();

function isExternal(url: string): boolean {
  return /^https?:\/\//i.test(url);
}

/** Hostnames that count as a source repository (not docs or pages sites). */
const REPO_HOST_SUFFIXES = ["github.com", "gitlab.com", "codeberg.org"] as const;

function isRepoHost(hostname: string): boolean {
  const host = hostname.toLowerCase();
  return REPO_HOST_SUFFIXES.some((suffix) => host === suffix || host.endsWith(`.${suffix}`));
}

/** Short label for recruiters — avoid dumping the raw URL. */
function linkLabel(url: string): string {
  try {
    const host = new URL(url, "https://example.invalid").hostname;
    if (isRepoHost(host)) {
      return "repository";
    }
  } catch {
    // relative or non-URL path — fall through
  }
  return isExternal(url) ? "live site" : "open";
}

function artSrc(slug: string): string {
  return projectArtForSlug(slug, colorThemeResolved.value);
}
</script>

<template>
  <div class="case-study-list grid grid-cols-1 gap-4 md:grid-cols-2">
    <Card
      v-for="proj in projects"
      :key="proj.slug"
      as="article"
      class="min-w-0 overflow-hidden !p-0"
    >
      <div class="overflow-hidden" aria-hidden="true">
        <img
          :src="artSrc(proj.slug)"
          alt=""
          class="h-28 w-full object-cover object-center sm:h-32"
          width="640"
          height="200"
          decoding="async"
          loading="lazy"
        />
      </div>

      <div class="flex flex-col gap-3 p-4 sm:p-5">
        <h3 class="card-title text-balance">{{ proj.name }}</h3>
        <p class="text-body text-pretty">{{ proj.description }}</p>

        <dl v-if="proj.problem || proj.approach || proj.result" class="space-y-2 text-sm">
          <div v-if="proj.problem">
            <dt class="text-label text-accent-blue">problem</dt>
            <dd class="text-body mt-0.5">{{ proj.problem }}</dd>
          </div>
          <div v-if="proj.approach">
            <dt class="text-label text-accent-blue">approach</dt>
            <dd class="text-body mt-0.5">{{ proj.approach }}</dd>
          </div>
          <div v-if="proj.result">
            <dt class="text-label text-accent-blue">result</dt>
            <dd class="text-body mt-0.5">{{ proj.result }}</dd>
          </div>
        </dl>

        <div class="flex flex-wrap gap-2">
          <span
            v-for="t in proj.tech"
            :key="t"
            class="inline-flex items-center rounded-lg bg-surface-dark px-2.5 py-1 text-sm text-surface-sage"
          >
            {{ t }}
          </span>
        </div>

        <p v-if="proj.url" class="mt-1">
          <a
            v-if="isExternal(proj.url)"
            :href="proj.url"
            target="_blank"
            rel="noopener noreferrer"
            class="text-accent-blue underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 rounded"
          >
            {{ linkLabel(proj.url) }}
            <span class="sr-only">(opens in new tab)</span>
          </a>
          <RouterLink
            v-else
            :to="proj.url"
            class="text-accent-blue underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 rounded"
          >
            {{ linkLabel(proj.url) }}
          </RouterLink>
        </p>
      </div>
    </Card>
  </div>
</template>
