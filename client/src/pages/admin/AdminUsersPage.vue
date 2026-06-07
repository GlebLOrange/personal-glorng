<script setup lang="ts">
import { onMounted, ref } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { getApiErrorMessage } from "@/types/api";
import type { AdminUserSummary } from "@/types";

const { toast } = useNotify();
const users = ref<AdminUserSummary[]>([]);
const loading = ref(false);
const savingId = ref<string | null>(null);
const draftPermissions = ref<Record<string, string>>({});

async function loadUsers(): Promise<void> {
  loading.value = true;
  try {
    const { data } = await api.get<AdminUserSummary[]>("/admin/users");
    users.value = data;
    for (const user of data) {
      draftPermissions.value[user.id] = user.permissions.join(", ");
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
    const permissions = draftPermissions.value[user.id]
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
    const { data } = await api.patch<AdminUserSummary>(`/admin/users/${user.id}/permissions`, {
      permissions,
    });
    const index = users.value.findIndex((row) => row.id === user.id);
    if (index >= 0) {
      users.value[index] = data;
      draftPermissions.value[user.id] = data.permissions.join(", ");
    }
    toast("Permissions updated", "success");
  } catch (err) {
    toast(getApiErrorMessage(err, "Failed to update permissions"), "error");
  } finally {
    savingId.value = null;
  }
}

onMounted(() => {
  void loadUsers();
});
</script>

<template>
  <AdminPageLayout title="users" max-width="xl">
    <p class="text-sm text-surface-mid mb-6">
      Manage tool permissions. Users cannot change these themselves.
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
          <span
            class="text-xs px-2 py-1 rounded"
            :class="user.is_verified ? 'bg-green-900/40 text-green-300' : 'bg-yellow-900/40 text-yellow-300'"
          >
            {{ user.is_verified ? "verified" : "unverified" }}
          </span>
        </div>
        <label class="block text-xs text-surface-mid">
          Permissions (comma-separated)
          <input
            v-model="draftPermissions[user.id]"
            type="text"
            class="mt-1 w-full rounded border border-surface-border bg-surface-dark px-3 py-2 text-surface-light text-sm"
            placeholder="expenses:read, tasks:write"
          />
        </label>
        <BaseButton
          variant="secondary"
          :disabled="savingId === user.id"
          @click="savePermissions(user)"
        >
          {{ savingId === user.id ? "Saving..." : "Save permissions" }}
        </BaseButton>
      </article>
    </div>
  </AdminPageLayout>
</template>
