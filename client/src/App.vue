<script setup lang="ts">
import NavBar from "@/components/layout/NavBar.vue";
import FooterBar from "@/components/layout/FooterBar.vue";
import ScrollControls from "@/components/layout/ScrollControls.vue";
import ToastContainer from "@/components/ui/ToastContainer.vue";
</script>

<template>
  <div class="min-h-screen flex flex-col font-sans">
    <a href="#main-content" class="skip-link">Skip to main content</a>
    <NavBar />
    <main id="main-content" class="flex-1" tabindex="-1">
      <RouterView />
      <ScrollControls />
    </main>
    <FooterBar />
    <ToastContainer />
  </div>
</template>
