<script setup lang="ts">
import ToastContainer from "@/components/ui/ToastContainer.vue";
import WeatherBar from "@/components/weather/WeatherBar.vue";
</script>

<template>
  <div class="page-tool-grid mb-8 min-w-0">
    <ToastContainer variant="tile" />
    <WeatherBar wrapper-class="page-tile md:col-start-3" card-class="page-weather-tile-card" />
  </div>
</template>
