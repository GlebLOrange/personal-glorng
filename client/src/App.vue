<script setup lang="ts">
import { storeToRefs } from "pinia";

import NavBar from "@/components/layout/NavBar.vue";
import FooterBar from "@/components/layout/FooterBar.vue";
import ScrollControls from "@/components/layout/ScrollControls.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import ToastContainer from "@/components/ui/ToastContainer.vue";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const { sessionError } = storeToRefs(auth);

async function retrySession(): Promise<void> {
  try {
    await auth.resolveSession();
  } catch {
    // sessionError updated in the store
  }
}
</script>

<template>
  <div class="min-h-screen flex flex-col font-sans">
    <a href="#main-content" class="skip-link">Skip to main content</a>
    <NavBar />
    <main id="main-content" class="flex-1" tabindex="-1">
      <div v-if="sessionError" class="mx-auto max-w-lg px-4 pt-6">
        <ErrorState
          :message="sessionError"
          show-retry
          retry-label="retry session"
          @retry="retrySession"
        />
      </div>
      <RouterView />
      <ScrollControls />
    </main>
    <FooterBar />
    <ToastContainer variant="overlay" />
  </div>
</template>
