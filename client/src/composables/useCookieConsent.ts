import type { App } from "vue";
import * as CookieConsent from "vanilla-cookieconsent";
import "vanilla-cookieconsent/dist/cookieconsent.css";

import { initSentry } from "@/instrument";
import { initAnalytics } from "@/router";

let sentryInitialized = false;
let analyticsInitialized = false;

function applyConsent(app: App) {
  if (!sentryInitialized && CookieConsent.acceptedCategory("monitoring")) {
    initSentry(app);
    sentryInitialized = true;
  }

  if (!analyticsInitialized && CookieConsent.acceptedCategory("analytics")) {
    const gaId = import.meta.env.VITE_GA_ID;
    if (gaId) {
      initAnalytics(gaId);
      analyticsInitialized = true;
    }
  }
}

export function setupCookieConsent(app: App): void {
  CookieConsent.run({
    guiOptions: {
      consentModal: {
        layout: "bar inline",
        position: "bottom",
        equalWeightButtons: true,
      },
      preferencesModal: {
        layout: "box",
      },
    },

    categories: {
      necessary: {
        enabled: true,
        readOnly: true,
      },
      analytics: {
        autoClear: {
          cookies: [
            { name: /^_ga/ },
            { name: "_gid" },
          ],
        },
      },
      monitoring: {
        autoClear: {
          cookies: [
            { name: /^sentry/ },
          ],
        },
      },
    },

    onConsent: () => applyConsent(app),
    onChange: () => applyConsent(app),

    language: {
      default: "en",
      translations: {
        en: {
          consentModal: {
            title: "Cookie preferences",
            description:
              "This site uses cookies for analytics and error monitoring to improve your experience. You can choose which categories to allow.",
            acceptAllBtn: "Accept all",
            acceptNecessaryBtn: "Reject all",
            showPreferencesBtn: "Manage preferences",
            footer: '<a href="/privacy">Privacy Policy</a>',
          },
          preferencesModal: {
            title: "Cookie preferences",
            acceptAllBtn: "Accept all",
            acceptNecessaryBtn: "Reject all",
            savePreferencesBtn: "Save preferences",
            closeIconLabel: "Close",
            sections: [
              {
                title: "Strictly necessary",
                description:
                  "These cookies are essential for the site to function (authentication, session management).",
                linkedCategory: "necessary",
              },
              {
                title: "Analytics",
                description:
                  "Google Analytics helps us understand how visitors interact with the site.",
                linkedCategory: "analytics",
                cookieTable: {
                  headers: { name: "Name", domain: "Domain", description: "Description" },
                  body: [
                    {
                      name: "_ga",
                      domain: "google.com",
                      description: "Distinguishes unique users.",
                    },
                    {
                      name: "_gid",
                      domain: "google.com",
                      description: "Distinguishes unique users (24h).",
                    },
                  ],
                },
              },
              {
                title: "Error monitoring",
                description:
                  "Sentry captures errors and performance data to help us fix issues faster.",
                linkedCategory: "monitoring",
              },
            ],
          },
        },
      },
    },
  });
}
