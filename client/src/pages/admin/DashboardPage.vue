<script setup lang="ts">
import { computed, onMounted } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import { Card } from "@/components/ui/card";
import { usePlatformCatalog } from "@/composables/usePlatformCatalog";
import { groupServicesByCategory } from "@/platform/services";
import { usePermissions } from "@/composables/usePermissions";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const { can, isSuperuser } = usePermissions();
const { services, load } = usePlatformCatalog();

const SUPERUSER_ONLY_SERVICES = new Set(["news"]);

const visibleServices = computed(() =>
  services.value.filter(
    (service) =>
      can(service.slug, "read") &&
      (!SUPERUSER_ONLY_SERVICES.has(service.slug) || isSuperuser.value),
  ),
);

const sections = computed(() => groupServicesByCategory(visibleServices.value));

onMounted(() => load());
</script>

<template>
  <AdminPageLayout title="tools" max-width="xl">
    <div class="mb-6">
      <p class="text-surface-mid text-sm mb-2">
        Welcome back, {{ auth.user?.display_name || auth.user?.email || "admin" }}
      </p>
      <p class="text-surface-muted text-xs">Services shared across web, bot, and workers</p>
      <RouterLink
        v-if="isSuperuser"
        to="/admin/users"
        class="inline-block mt-3 text-xs text-accent-blue hover:underline"
      >
        Manage users
      </RouterLink>
    </div>

    <section v-for="section in sections" :key="section.category" class="mb-10">
      <h2 class="text-lg font-bold text-surface-light mb-4">{{ section.label }}</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <component
          :is="tool.external ? 'a' : 'RouterLink'"
          v-for="tool in section.services"
          :key="tool.adminRoute"
          :to="tool.external ? undefined : tool.adminRoute"
          :href="tool.external ? tool.adminRoute : undefined"
          :target="tool.external ? '_blank' : undefined"
          :rel="tool.external ? 'noopener' : undefined"
        >
          <Card hoverable class="h-full">
            <div class="text-2xl mb-3">{{ tool.icon }}</div>
            <h3 class="text-surface-light font-bold mb-1">{{ tool.name }}</h3>
            <p class="text-xs text-surface-mid">{{ tool.description }}</p>
          </Card>
        </component>
      </div>
    </section>
  </AdminPageLayout>
</template>
