<script setup lang="ts">
import NavBar from "@/components/layout/NavBar.vue";
import FooterBar from "@/components/layout/FooterBar.vue";
import ToastContainer from "@/components/ui/ToastContainer.vue";
</script>

<template>
  <div class="min-h-screen flex flex-col font-mono">
    <NavBar />
    <main class="flex-1">
      <RouterView />
    </main>
    <FooterBar />
    <ToastContainer />
  </div>
</template>
