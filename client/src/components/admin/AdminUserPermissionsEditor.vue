<script setup lang="ts">
import { computed } from "vue";

import ToolIcon from "@/components/icons/ToolIcon.vue";
import { groupServicesByCategory, type PlatformService } from "@/platform/services";
import { permissionKey, SUPERUSER_PERMISSION } from "@/utils/permissions";

const props = defineProps<{
  permissions: string[];
  disabled?: boolean;
  lockSuperuser?: boolean;
  services: PlatformService[];
}>();

const emit = defineEmits<{
  "update:permissions": [value: string[]];
}>();

const isSuperuser = computed(() => props.permissions.includes(SUPERUSER_PERMISSION));
const permissionSet = computed(() => new Set(props.permissions));

const sections = computed(() => groupServicesByCategory(props.services));
const explicitToolPermissionCount = computed(
  () => props.permissions.filter((permission) => permission !== SUPERUSER_PERMISSION).length,
);

function hasPermission(key: string): boolean {
  return permissionSet.value.has(key);
}

function emitPermissions(next: string[]): void {
  emit("update:permissions", [...new Set(next)]);
}

function toggleSuperuser(checked: boolean): void {
  if (checked) {
    emitPermissions([...props.permissions, SUPERUSER_PERMISSION]);
    return;
  }
  emitPermissions(props.permissions.filter((p) => p !== SUPERUSER_PERMISSION));
}

function togglePermission(key: string, checked: boolean): void {
  if (checked) {
    emitPermissions([...props.permissions, key]);
    return;
  }
  emitPermissions(props.permissions.filter((p) => p !== key));
}

function capabilityLabel(capability: string): string {
  return capability.replace(/[-_]/g, " ");
}

function servicePermissionCount(service: PlatformService): number {
  return service.capabilities.filter((capability) =>
    hasPermission(permissionKey(service.slug, capability)),
  ).length;
}

function servicePermissionSummary(service: PlatformService): string {
  if (isSuperuser.value) return "All";
  return `${servicePermissionCount(service)}/${service.capabilities.length}`;
}
</script>

<template>
  <div class="space-y-4">
    <div
      class="rounded-lg border border-surface-border bg-surface-dark/70 px-4 py-4"
      :class="{ 'border-accent-violet/40 bg-accent-violet/10': isSuperuser }"
    >
      <label
        class="flex items-start gap-3 text-sm text-surface-light cursor-pointer"
        :class="{ 'opacity-50 cursor-not-allowed': disabled || lockSuperuser }"
      >
        <input
          type="checkbox"
          class="mt-1 accent-accent-blue"
          :checked="isSuperuser"
          :disabled="disabled || lockSuperuser"
          @change="toggleSuperuser(($event.target as HTMLInputElement).checked)"
        />
        <span class="min-w-0">
          <span class="font-semibold">Platform superuser</span>
          <span class="block text-xs text-surface-mid mt-1">
            Full admin access to all tools and user management
          </span>
        </span>
      </label>
      <p
        v-if="lockSuperuser"
        class="mt-3 rounded border border-accent-golden/30 bg-accent-golden/10 px-3 py-2 text-xs text-accent-golden"
      >
        Cannot demote the last admin
      </p>
    </div>

    <div class="space-y-4">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3 class="text-sm font-semibold text-surface-light">Tool permissions</h3>
          <p class="text-xs text-surface-mid">
            <template v-if="isSuperuser">All tools included via superuser</template>
            <template v-else>{{ explicitToolPermissionCount }} selected</template>
          </p>
        </div>
        <p v-if="disabled" class="text-xs text-surface-muted">Editing disabled for this user</p>
      </div>

      <section v-for="section in sections" :key="section.category" class="space-y-2">
        <h3 class="text-meta mb-2 uppercase tracking-wider">
          {{ section.label }}
        </h3>
        <div
          v-for="service in section.services"
          :key="service.slug"
          class="rounded-lg border border-surface-border/60 bg-surface-dark/30 px-3 py-3"
        >
          <div class="mb-3 flex flex-wrap items-start justify-between gap-2">
            <div class="min-w-0">
              <p class="flex items-center gap-2 text-sm font-medium text-surface-light">
                <ToolIcon :slug="service.slug" class="h-4 w-4 shrink-0 text-surface-light" />
                {{ service.name }}
              </p>
              <p class="mt-0.5 text-xs text-surface-mid">{{ service.description }}</p>
            </div>
            <span
              class="rounded border border-surface-border bg-surface-card px-2 py-0.5 text-xs text-surface-muted"
            >
              {{ servicePermissionSummary(service) }}
            </span>
          </div>

          <div class="flex flex-wrap gap-2">
            <label
              v-for="capability in service.capabilities"
              :key="permissionKey(service.slug, capability)"
              class="inline-flex items-center gap-2 rounded border border-surface-border bg-surface-card px-2.5 py-1.5 text-xs text-surface-light cursor-pointer transition-colors hover:border-accent-blue"
              :class="{ 'opacity-50 cursor-not-allowed': disabled || isSuperuser }"
            >
              <input
                type="checkbox"
                class="accent-accent-blue"
                :checked="hasPermission(permissionKey(service.slug, capability))"
                :disabled="disabled || isSuperuser"
                @change="
                  togglePermission(
                    permissionKey(service.slug, capability),
                    ($event.target as HTMLInputElement).checked,
                  )
                "
              />
              <span class="capitalize">{{ capabilityLabel(capability) }}</span>
              <span class="font-data text-surface-muted">{{
                permissionKey(service.slug, capability)
              }}</span>
            </label>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>
