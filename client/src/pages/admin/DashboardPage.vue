<script setup lang="ts">
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import WeatherWidget from "@/components/weather/WeatherWidget.vue";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();

const tools = [
  { name: "Weather", description: "Look up weather for any city", route: "/admin/tools/weather", icon: "☀" },
  { name: "Calculator", description: "Quick math calculations", route: "/admin/tools/calculator", icon: "⊞" },
  { name: "URL Shortener", description: "Create and manage short URLs", route: "/admin/tools/url-shortener", icon: "⟶" },
  { name: "Video Download", description: "Download videos with yt-dlp", route: "/admin/tools/vid-download", icon: "▶" },
  { name: "File Share", description: "Share files between devices", route: "/admin/tools/file-share", icon: "↗" },
  { name: "Tasks", description: "Manage todobot tasks & reminders", route: "/admin/tools/tasks", icon: "☐" },
  { name: "Recipes", description: "Personal recipe book & food notes", route: "/admin/tools/recipes", icon: "◉" },
  { name: "Email", description: "Send styled emails to anyone", route: "/admin/tools/email", icon: "✉" },
  { name: "Feedback", description: "Read visitor feedback messages", route: "/admin/tools/feedback", icon: "💬" },
  { name: "AI Chat", description: "Chat with GPT from the admin panel", route: "/admin/tools/ai-chat", icon: "⊛" },
  { name: "API Docs", description: "Swagger API documentation", route: "/api/docs", icon: "❴❵", external: true },
];
</script>

<template>
  <AdminPageLayout title="dashboard" max-width="xl">
    <p class="text-surface-mid text-sm mb-6 -mt-4">
      Welcome back, {{ auth.user?.email ?? "admin" }}
    </p>

    <div class="mb-10">
      <WeatherWidget city="Wroclaw" />
    </div>

    <h2 class="text-lg font-bold text-surface-light mb-4">Tools</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <component
        v-for="tool in tools"
        :key="tool.route"
        :is="tool.external ? 'a' : 'RouterLink'"
        :to="tool.external ? undefined : tool.route"
        :href="tool.external ? tool.route : undefined"
        :target="tool.external ? '_blank' : undefined"
        :rel="tool.external ? 'noopener' : undefined"
      >
        <BaseCard hoverable class="h-full">
          <div class="text-2xl mb-3">{{ tool.icon }}</div>
          <h3 class="text-surface-light font-bold mb-1">{{ tool.name }}</h3>
          <p class="text-xs text-surface-mid">{{ tool.description }}</p>
        </BaseCard>
      </component>
    </div>
  </AdminPageLayout>
</template>
