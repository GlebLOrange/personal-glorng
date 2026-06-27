<script setup lang="ts">
import * as CookieConsent from "vanilla-cookieconsent";

import { buildContactLinks } from "@/constants/contactMeta";
import { RESUME_FALLBACK } from "@/constants/resumeFallback";
import { isFirebaseAnalyticsEnabled } from "@/constants/firebase";
import { isSentryEnabled } from "@/constants/sentry";

const contactLinks = buildContactLinks(RESUME_FALLBACK.links);

function openPreferences() {
  CookieConsent.showPreferences();
}
</script>

<template>
  <div class="max-w-3xl mx-auto px-6 py-16 text-surface-light">
    <h1 class="text-3xl font-bold mb-2 accent-gradient">Privacy Policy</h1>
    <p class="text-surface-muted text-sm mb-10">Last updated: May 26, 2026</p>

    <section class="mb-10">
      <h2 class="text-xl font-semibold text-accent-blue mb-3">What data is collected</h2>
      <p class="text-surface-sage leading-relaxed mb-3">
        This site collects minimal data to keep things running and to understand how visitors use
        it.
      </p>
      <ul class="list-disc list-inside text-surface-sage space-y-1.5 ml-2">
        <li>
          <strong class="text-surface-light">Authentication cookies</strong> — stored when you log
          in, used to keep your session active.
        </li>
        <li v-if="isFirebaseAnalyticsEnabled">
          <strong class="text-surface-light">Firebase Analytics</strong> — collects anonymous page
          view data (pages visited, time on site, general location). IP addresses are anonymized.
        </li>
        <li v-if="isSentryEnabled">
          <strong class="text-surface-light">Sentry</strong> — captures errors and performance data
          to help fix bugs. May collect IP address and browser info when an error occurs.
        </li>
        <li>
          <strong class="text-surface-light">Spotify now playing</strong> — when enabled, the
          portfolio may show the site owner's currently playing track title, artist, and album art
          via Spotify's API. Visitors do not sign in to Spotify.
        </li>
        <li>
          <strong class="text-surface-light">Date &amp; time &amp; location</strong> — city names
          you save are sent to this site's API to fetch local time and conditions (via wttr.in).
          Saved cities are stored in your browser for guests, or in your account when logged in.
          Browser location is never requested automatically.
        </li>
      </ul>
    </section>

    <section class="mb-10">
      <h2 class="text-xl font-semibold text-accent-blue mb-3">Cookies used</h2>
      <div class="overflow-x-auto">
        <table
          class="w-full text-sm text-left border border-surface-border rounded-lg overflow-hidden"
        >
          <thead class="bg-surface-card text-surface-mid">
            <tr>
              <th class="px-4 py-2 border-b border-surface-border">Cookie</th>
              <th class="px-4 py-2 border-b border-surface-border">Purpose</th>
              <th class="px-4 py-2 border-b border-surface-border">Duration</th>
            </tr>
          </thead>
          <tbody class="text-surface-sage">
            <tr class="border-b border-surface-border">
              <td class="px-4 py-2 font-semibold text-surface-light">cc_cookie</td>
              <td class="px-4 py-2">Stores your cookie consent preferences.</td>
              <td class="px-4 py-2">6 months</td>
            </tr>
            <tr v-if="isFirebaseAnalyticsEnabled" class="border-b border-surface-border">
              <td class="px-4 py-2 font-semibold text-surface-light">_ga</td>
              <td class="px-4 py-2">Distinguishes unique visitors (Firebase Analytics).</td>
              <td class="px-4 py-2">2 years</td>
            </tr>
            <tr v-if="isFirebaseAnalyticsEnabled" class="border-b border-surface-border">
              <td class="px-4 py-2 font-semibold text-surface-light">_gid</td>
              <td class="px-4 py-2">Distinguishes unique visitors (Firebase Analytics).</td>
              <td class="px-4 py-2">24 hours</td>
            </tr>
            <tr v-if="isSentryEnabled">
              <td class="px-4 py-2 font-semibold text-surface-light">sentry-*</td>
              <td class="px-4 py-2">Error tracking and performance monitoring.</td>
              <td class="px-4 py-2">Session</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="mb-10">
      <h2 class="text-xl font-semibold text-accent-blue mb-3">Your choices</h2>
      <p class="text-surface-sage leading-relaxed">
        You can change your cookie preferences at any time by opening the
        <button
          class="text-accent-blue underline underline-offset-2 hover:text-accent-violet transition-colors"
          @click="openPreferences"
        >
          cookie settings</button
        >.
        <span v-if="isFirebaseAnalyticsEnabled && isSentryEnabled">
          Analytics and error monitoring only run if you've given consent.
        </span>
        <span v-else-if="isFirebaseAnalyticsEnabled">
          Analytics only runs if you've given consent.
        </span>
        <span v-else-if="isSentryEnabled">
          Error monitoring only runs if you've given consent.
        </span>
        <span v-else> Optional analytics and error monitoring are currently disabled.</span>
      </p>
    </section>

    <section class="mb-10">
      <h2 class="text-xl font-semibold text-accent-blue mb-3">Third parties</h2>
      <ul class="list-disc list-inside text-surface-sage space-y-1.5 ml-2">
        <li v-if="isFirebaseAnalyticsEnabled">
          <a
            href="https://policies.google.com/privacy"
            target="_blank"
            rel="noopener"
            class="text-accent-blue hover:text-accent-violet transition-colors"
            >Firebase Analytics</a
          >
          — used for anonymous usage statistics.
        </li>
        <li v-if="isSentryEnabled">
          <a
            href="https://sentry.io/privacy/"
            target="_blank"
            rel="noopener"
            class="text-accent-blue hover:text-accent-violet transition-colors"
            >Sentry</a
          >
          — used for error and performance monitoring.
        </li>
      </ul>
    </section>

    <section class="mb-10">
      <h2 class="text-xl font-semibold text-accent-blue mb-3">Contact</h2>
      <p class="text-surface-sage leading-relaxed mb-3">
        Questions about this policy? Reach out through any of these:
      </p>
      <ul class="list-disc list-inside text-surface-sage space-y-1.5 ml-2">
        <li v-for="link in contactLinks" :key="link.id">
          <a
            :href="link.href"
            target="_blank"
            rel="noopener"
            class="text-accent-blue hover:text-accent-violet transition-colors"
            >{{ link.label }}</a
          >
        </li>
      </ul>
    </section>

    <div class="pt-6 border-t border-surface-border">
      <router-link
        to="/"
        class="text-sm text-surface-muted hover:text-accent-blue transition-colors"
      >
        ← Back to home
      </router-link>
    </div>
  </div>
</template>
