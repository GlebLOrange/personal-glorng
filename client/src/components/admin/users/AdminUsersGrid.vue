<script setup lang="ts">
import StatusBadge from "@/components/ui/StatusBadge.vue";
import { userRoleClass, userStatusClass } from "@/constants/filterColors";
import type { AdminUserSummary } from "@/types";
import { formatDate } from "@/utils/format";
import { SUPERUSER_PERMISSION } from "@/utils/permissions";

type BadgeView = { id: string; label: string; className: string };

defineProps<{
  users: AdminUserSummary[];
  draftPermissions: Record<string, string[]>;
}>();

const emit = defineEmits<{
  select: [user: AdminUserSummary];
}>();

function permissionCount(user: AdminUserSummary, draft: Record<string, string[]>): number {
  return (draft[user.id] ?? user.permissions).filter(
    (permission) => permission !== SUPERUSER_PERMISSION,
  ).length;
}

function roleBadge(user: AdminUserSummary): BadgeView {
  const isSuperuser = user.permissions.includes(SUPERUSER_PERMISSION);
  return {
    id: "role",
    label: isSuperuser ? "superuser" : "custom access",
    className: isSuperuser ? userRoleClass("superuser") : userRoleClass("custom"),
  };
}

function statusBadges(user: AdminUserSummary): BadgeView[] {
  return [
    ...(user.is_protected
      ? [{ id: "protected", label: "protected", className: userStatusClass("protected") }]
      : []),
    user.is_verified
      ? { id: "verified", label: "verified", className: userStatusClass("verified") }
      : { id: "unverified", label: "unverified", className: userStatusClass("unverified") },
  ];
}
</script>

<template>
  <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
    <button
      v-for="user in users"
      :key="user.id"
      type="button"
      class="interactive-surface h-full w-full p-4 text-left transition-colors"
      :aria-label="`open permissions for ${user.display_name || user.email}`"
      @click="emit('select', user)"
    >
      <span class="flex min-h-full flex-col gap-4">
        <span class="flex items-start justify-between gap-3">
          <span class="min-w-0">
            <span class="block truncate text-base font-semibold text-surface-light">
              {{ user.display_name || user.email }}
            </span>
            <span class="mt-1 block truncate text-xs text-surface-mid">{{ user.email }}</span>
          </span>
          <StatusBadge :label="roleBadge(user).label" :class-name="roleBadge(user).className" />
        </span>

        <span class="flex flex-wrap gap-2">
          <StatusBadge
            v-for="badge in statusBadges(user)"
            :key="badge.id"
            :label="badge.label"
            :class-name="badge.className"
          />
        </span>

        <span class="mt-auto flex items-center justify-between gap-3 text-xs text-surface-muted">
          <span>{{ permissionCount(user, draftPermissions) }} permissions</span>
          <span>Joined {{ formatDate(user.created_at) }}</span>
        </span>
      </span>
    </button>
  </div>
</template>
