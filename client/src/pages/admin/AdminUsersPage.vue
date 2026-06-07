<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import AdminUserPermissionsEditor from "@/components/admin/AdminUserPermissionsEditor.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import {
  PLATFORM_SERVICES,
  type PlatformService,
} from "@/platform/services";
import { getApiErrorMessage } from "@/types/api";
import type { AdminUserSummary } from "@/types";
import { isAiChatEnabled } from "@/utils/featureFlags";
import { SUPERUSER_PERMISSION } from "@/utils/permissions";

function filterAiChat(services: PlatformService[]): PlatformService[] {
  if (isAiChatEnabled()) return services;
  return services.filter((s) => s.slug !== "ai-chat");
}

const { toast } = useNotify();
const users = ref<AdminUserSummary[]>([]);
const services = ref<PlatformService[]>(filterAiChat(PLATFORM_SERVICES));
const loading = ref(false);
const savingId = ref<string | null>(null);
const draftPermissions = ref<Record<string, string[]>>({});

const superuserCount = computed(
  () => users.value.filter((u) => u.permissions.includes(SUPERUSER_PERMISSION)).length,
);

function isLastSuperuser(user: AdminUserSummary): boolean {
  return user.permissions.includes(SUPERUSER_PERMISSION) && superuserCount.value <= 1;
}

function setDraftPermissions(userId: string, permissions: string[]): void {
  draftPermissions.value[userId] = permissions;
}

async function loadPlatformServices(): Promise<void> {
  try {
    const { data } = await api.get<{
      services: Array<{
        slug: string;
        name: string;
        category: string;
        category_label: string;
        description: string;
        api_prefix: string;
        admin_route: string;
        icon: string;
        capabilities: string[];
        external: boolean;
      }>;
    }>("/platform/services");
    services.value = filterAiChat(
      data.services.map((s) => ({
        slug: s.slug,
        name: s.name,
        category: s.category,
        categoryLabel: s.category_label,
        description: s.description,
        apiPrefix: s.api_prefix,
        adminRoute: s.admin_route,
        icon: s.icon,
        capabilities: s.capabilities,
        external: s.external,
      })),
    );
  } catch {
    // Fallback to static registry
  }
}

async function loadUsers(): Promise<void> {
  loading.value = true;
  try {
    const { data } = await api.get<AdminUserSummary[]>("/admin/users");
    users.value = data;
    for (const user of data) {
      draftPermissions.value[user.id] = [...user.permissions];
    }
  } catch (err) {
    toast(getApiErrorMessage(err, "Failed to load users"), "error");
  } finally {
    loading.value = false;
  }
}

async function savePermissions(user: AdminUserSummary): Promise<void> {
  savingId.value = user.id;
  try {
    const permissions = draftPermissions.value[user.id] ?? [];
    const { data } = await api.patch<AdminUserSummary>(`/admin/users/${user.id}/permissions`, {
      permissions,
    });
    const index = users.value.findIndex((row) => row.id === user.id);
    if (index >= 0) {
      users.value[index] = data;
      draftPermissions.value[user.id] = [...data.permissions];
    }
    toast("Permissions updated", "success");
  } catch (err) {
    draftPermissions.value[user.id] = [...user.permissions];
    toast(getApiErrorMessage(err, "Failed to update permissions"), "error");
  } finally {
    savingId.value = null;
  }
}

onMounted(() => {
  void Promise.all([loadUsers(), loadPlatformServices()]);
});
</script>

<template>
  <AdminPageLayout title="users" max-width="xl">
    <p class="text-sm text-surface-mid mb-6">
      Manage tool permissions and promote users to platform superuser. Users cannot change
      these themselves.
    </p>

    <p v-if="loading" class="text-surface-mid text-sm">Loading users...</p>

    <div v-else class="space-y-6">
      <article
        v-for="user in users"
        :key="user.id"
        class="rounded-lg border border-surface-border bg-surface-dark/50 p-4 space-y-3"
      >
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div>
            <p class="text-surface-light font-medium">
              {{ user.display_name || user.email }}
            </p>
            <p class="text-xs text-surface-mid">{{ user.email }}</p>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <span
              v-if="user.is_protected"
              class="text-xs px-2 py-1 rounded bg-blue-900/40 text-blue-300"
            >
              protected
            </span>
            <span
              class="text-xs px-2 py-1 rounded"
              :class="user.is_verified ? 'bg-green-900/40 text-green-300' : 'bg-yellow-900/40 text-yellow-300'"
            >
              {{ user.is_verified ? "verified" : "unverified" }}
            </span>
          </div>
        </div>

        <AdminUserPermissionsEditor
          :permissions="draftPermissions[user.id] ?? []"
          :disabled="user.is_protected"
          :lock-superuser="isLastSuperuser(user)"
          :services="services"
          @update:permissions="setDraftPermissions(user.id, $event)"
        />

        <BaseButton
          variant="secondary"
          :disabled="savingId === user.id || user.is_protected"
          @click="savePermissions(user)"
        >
          {{ savingId === user.id ? "Saving..." : "Save permissions" }}
        </BaseButton>
      </article>
    </div>
  </AdminPageLayout>
</template>
