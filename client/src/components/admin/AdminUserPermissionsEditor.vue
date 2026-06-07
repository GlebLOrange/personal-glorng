<script setup lang="ts">
import { computed } from "vue";

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

const sections = computed(() => groupServicesByCategory(props.services));

function hasPermission(key: string): boolean {
  return props.permissions.includes(key);
}

function emitPermissions(next: string[]): void {
  emit("update:permissions", next);
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
</script>

<template>
  <div class="space-y-4">
    <div class="rounded border border-surface-border bg-surface-dark/80 px-3 py-3 space-y-1">
      <label
        class="flex items-start gap-2 text-sm text-surface-light cursor-pointer"
        :class="{ 'opacity-50 cursor-not-allowed': disabled || lockSuperuser }"
      >
        <input
          type="checkbox"
          class="mt-0.5 accent-accent-blue"
          :checked="isSuperuser"
          :disabled="disabled || lockSuperuser"
          @change="toggleSuperuser(($event.target as HTMLInputElement).checked)"
        />
        <span>
          <span class="font-medium">Platform superuser</span>
          <span class="block text-xs text-surface-mid mt-0.5">
            Full admin access to all tools and user management
          </span>
        </span>
      </label>
      <p v-if="lockSuperuser" class="text-xs text-yellow-300/90 pl-6">
        Cannot demote the last admin
      </p>
    </div>

    <div class="space-y-4">
      <p class="text-xs text-surface-mid">
        Tool permissions
        <span v-if="isSuperuser" class="text-surface-muted">— included via superuser</span>
      </p>

      <section v-for="section in sections" :key="section.category" class="space-y-2">
        <h3 class="text-xs font-medium text-surface-light uppercase tracking-wide">
          {{ section.label }}
        </h3>
        <div
          v-for="service in section.services"
          :key="service.slug"
          class="rounded border border-surface-border/60 px-3 py-2"
        >
          <p class="text-xs text-surface-mid mb-2">{{ service.name }}</p>
          <div class="flex flex-wrap gap-x-4 gap-y-2">
            <label
              v-for="capability in service.capabilities"
              :key="permissionKey(service.slug, capability)"
              class="flex items-center gap-1.5 text-xs text-surface-light cursor-pointer"
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
              {{ permissionKey(service.slug, capability) }}
            </label>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>
