<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

import WeatherBar from "@/components/weather/WeatherBar.vue";
import ToolIcon from "@/components/icons/ToolIcon.vue";
import { Card } from "@/components/ui/card";
import { usePermissions } from "@/composables/usePermissions";
import { WEATHER_ROUTE_NAME } from "@/constants/weather";

const route = useRoute();
const { isSuperuser } = usePermissions();

const isWeatherPage = computed(() => route.name === WEATHER_ROUTE_NAME);

const showUsersTile = computed(
  () => isSuperuser.value && route.name === "admin",
);
</script>

<template>
  <div v-if="!isWeatherPage" class="page-tool-grid mb-8 min-w-0">
    <RouterLink v-if="showUsersTile" to="/admin/users" class="page-tile">
      <Card hoverable class="page-tile-card h-full">
        <ToolIcon slug="users" class="mb-3 h-8 w-8 text-surface-light" />
        <h3 class="text-surface-light font-bold break-words">users</h3>
      </Card>
    </RouterLink>

    <WeatherBar
      wrapper-class="page-tile md:col-start-3"
      card-class="page-weather-tile-card"
    />
  </div>
</template>
