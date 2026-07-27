<script setup lang="ts">
import AdminUserPermissionsEditor from "@/components/admin/AdminUserPermissionsEditor.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import DrawerFooterActions from "@/components/ui/DrawerFooterActions.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { userRoleClass, userStatusClass } from "@/constants/filterColors";
import type { PlatformService } from "@/platform/services";
import type { AdminUserSummary } from "@/types";
import { formatDate } from "@/utils/format";
import { SUPERUSER_PERMISSION } from "@/utils/permissions";

type BadgeView = { id: string; label: string; className: string };

const props = defineProps<{
  user: AdminUserSummary | null;
  draftPermissions: string[];
  services: PlatformService[];
  saving: boolean;
  lockSuperuser: boolean;
  hasDraftChanges: boolean;
}>();

const emit = defineEmits<{
  close: [];
  save: [];
  "update:permissions": [value: string[]];
}>();

function permissionCount(permissions: string[]): number {
  return permissions.filter((permission) => permission !== SUPERUSER_PERMISSION).length;
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
  <BaseDrawer
    :open="user !== null"
    :title="user ? `Permissions · ${user.display_name || user.email}` : 'User permissions'"
    max-width="2xl"
    @close="emit('close')"
  >
    <template v-if="user">
      <p class="mb-5 break-all text-xs text-surface-mid">{{ user.email }}</p>

      <div class="mb-5 space-y-3">
        <div class="flex flex-wrap gap-2">
          <StatusBadge :label="roleBadge(user).label" :class-name="roleBadge(user).className" />
          <StatusBadge
            v-for="badge in statusBadges(user)"
            :key="badge.id"
            :label="badge.label"
            :class-name="badge.className"
          />
        </div>
        <p class="text-xs text-surface-muted">
          Joined {{ formatDate(user.created_at) }} ·
          {{ permissionCount(props.draftPermissions) }} tool permissions selected
        </p>
        <p
          v-if="user.is_protected"
          class="rounded-lg border border-accent-blue/30 bg-accent-blue/10 px-3 py-2 text-xs text-accent-blue"
        >
          Protected accounts are managed by the system and cannot be edited here.
        </p>
      </div>

      <AdminUserPermissionsEditor
        :permissions="draftPermissions"
        :disabled="user.is_protected"
        :lock-superuser="lockSuperuser"
        :services="services"
        @update:permissions="emit('update:permissions', $event)"
      />
    </template>

    <template v-if="user" #footer>
      <DrawerFooterActions>
        <template #start>
          <p v-if="hasDraftChanges" class="text-xs text-surface-muted">
            unsaved permission changes
          </p>
        </template>
        <template #dismiss>
          <BaseButton variant="secondary" @click="emit('close')"> cancel </BaseButton>
        </template>
        <template #primary>
          <ToolbarPillButton
            family="2xx"
            :disabled="user.is_protected || !hasDraftChanges || saving"
            @click="emit('save')"
          >
            {{ saving ? "saving…" : "save permissions" }}
          </ToolbarPillButton>
        </template>
      </DrawerFooterActions>
    </template>
  </BaseDrawer>
</template>
