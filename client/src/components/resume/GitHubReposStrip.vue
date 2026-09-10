<script setup lang="ts">
import { Card } from "@/components/ui/card";
import type { PublicGitHubRepo } from "@/types";

defineProps<{
  repos: PublicGitHubRepo[];
  profileUrl?: string;
}>();
</script>

<template>
  <div v-if="repos.length" class="space-y-4">
    <div class="flex flex-wrap items-baseline justify-between gap-2">
      <p class="text-meta lowercase">engineering highlights from github</p>
      <a
        v-if="profileUrl"
        :href="profileUrl"
        target="_blank"
        rel="noopener noreferrer"
        class="text-sm text-accent-blue underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 rounded lowercase"
      >
        view profile
        <span class="sr-only">(opens in new tab)</span>
      </a>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
      <Card
        v-for="repo in repos"
        :key="repo.full_name"
        class="!bg-surface-card ring-1 ring-inset ring-surface-border/70"
      >
        <a
          :href="repo.html_url"
          target="_blank"
          rel="noopener noreferrer"
          class="card-title lowercase text-inherit underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 rounded"
        >
          {{ repo.name }}
          <span class="sr-only">(opens in new tab)</span>
        </a>
        <p class="text-body mt-2 lowercase">
          {{ repo.description || "no description" }}
        </p>
        <p class="text-meta mt-3 lowercase">
          <span v-if="repo.language">{{ repo.language }} · </span>
          {{ repo.stargazers_count }} stars
        </p>
      </Card>
    </div>
  </div>
</template>
