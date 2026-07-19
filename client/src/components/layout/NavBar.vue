<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";

import NavMobileMenu from "@/components/layout/NavMobileMenu.vue";
import { useScrollDirection } from "@/composables/useScrollDirection";
import { useAuthStore } from "@/stores/auth";

const headerEl = ref<HTMLElement | null>(null);
const headerSpacerHeight = ref(0);
let resizeObserver: ResizeObserver | null = null;
let mobileNavMq: MediaQueryList | null = null;
let syncMobileNav: (() => void) | null = null;

const auth = useAuthStore();
const router = useRouter();
const mobileOpen = ref(false);
const isMobileNav = ref(false);

const { isHidden: isHeaderHidden, show: showHeader } = useScrollDirection({
  disabled: () => mobileOpen.value || isMobileNav.value,
});

watch(mobileOpen, (open) => {
  if (open) showHeader();
});

onMounted(() => {
  mobileNavMq = window.matchMedia("(max-width: 767px)");
  syncMobileNav = (): void => {
    isMobileNav.value = mobileNavMq?.matches ?? false;
  };
  syncMobileNav();
  mobileNavMq.addEventListener("change", syncMobileNav);

  if (typeof ResizeObserver !== "undefined") {
    resizeObserver = new ResizeObserver(() => {
      headerSpacerHeight.value = headerEl.value?.offsetHeight ?? 0;
    });
    if (headerEl.value) resizeObserver.observe(headerEl.value);
  } else {
    headerSpacerHeight.value = headerEl.value?.offsetHeight ?? 0;
  }
});

onBeforeUnmount(() => {
  if (mobileNavMq && syncMobileNav) {
    mobileNavMq.removeEventListener("change", syncMobileNav);
  }
  mobileNavMq = null;
  syncMobileNav = null;
  resizeObserver?.disconnect();
  resizeObserver = null;
});

function handleLogout(): void {
  auth.logout();
  void router.push("/");
}

function toggleMobileMenu(): void {
  mobileOpen.value = !mobileOpen.value;
}

function closeMobileMenu(): void {
  mobileOpen.value = false;
}
</script>

<template>
  <div>
    <div :style="{ height: `${headerSpacerHeight}px` }" aria-hidden="true" />

    <header
      ref="headerEl"
      class="fixed left-0 right-0 top-0 z-40 bg-surface-dark/80 backdrop-blur-md transition-transform duration-200 pt-[env(safe-area-inset-top)]"
      :class="isHeaderHidden ? '-translate-y-full' : 'translate-y-0'"
    >
      <nav aria-label="Main navigation" class="border-b border-surface-border">
        <div class="max-w-5xl mx-auto px-6 py-4 md:py-5 flex items-center justify-between gap-4">
          <RouterLink to="/" class="text-xl font-bold text-surface-light" @click="closeMobileMenu">
            Gleb.Y
          </RouterLink>

          <div class="hidden md:flex items-center gap-2 text-base shrink-0">
            <RouterLink
              to="/"
              class="nav-link inline-flex min-h-11 items-center px-3 py-2 rounded-lg"
              active-class="text-surface-light"
            >
              portfolio
            </RouterLink>
            <RouterLink
              to="/news"
              class="nav-link inline-flex min-h-11 items-center px-3 py-2 rounded-lg"
              active-class="text-surface-light"
            >
              news
            </RouterLink>

            <RouterLink
              v-if="auth.isAuthenticated"
              to="/admin"
              class="nav-link-accent inline-flex min-h-11 items-center px-3 py-2 rounded-lg"
              active-class="text-accent-blue"
            >
              admin
            </RouterLink>
            <RouterLink
              v-else
              to="/tools"
              class="nav-link-accent inline-flex min-h-11 items-center px-3 py-2 rounded-lg"
              active-class="text-accent-blue"
            >
              tools
            </RouterLink>

            <RouterLink
              v-if="auth.isAuthenticated"
              to="/settings"
              class="nav-link inline-flex min-h-11 items-center px-3 py-2 rounded-lg"
              active-class="text-surface-light"
            >
              settings
            </RouterLink>

            <button
              v-if="auth.isAuthenticated"
              type="button"
              class="nav-link-violet inline-flex min-h-11 items-center px-3 py-2 rounded-lg"
              @click="handleLogout"
            >
              logout
            </button>
            <RouterLink
              v-else
              to="/login"
              class="nav-link-accent inline-flex min-h-11 items-center px-3 py-2 rounded-lg"
              active-class="text-accent-blue"
            >
              login
            </RouterLink>
          </div>

          <button
            type="button"
            class="md:hidden interactive-surface inline-flex min-h-11 min-w-11 items-center justify-center text-surface-light"
            :aria-expanded="mobileOpen"
            aria-controls="nav-mobile-menu"
            aria-label="Toggle navigation menu"
            @click="toggleMobileMenu"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              class="size-5"
              aria-hidden="true"
            >
              <path v-if="!mobileOpen" stroke-linecap="round" d="M4 7h16M4 12h16M4 17h16" />
              <path v-else stroke-linecap="round" d="M6 6l12 12M18 6L6 18" />
            </svg>
          </button>
        </div>
      </nav>

      <NavMobileMenu :open="mobileOpen" @close="closeMobileMenu" />
    </header>
  </div>
</template>
