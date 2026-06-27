import type { App } from "vue";
import * as CookieConsent from "vanilla-cookieconsent";
import "vanilla-cookieconsent/dist/cookieconsent.css";

import { isFirebaseAnalyticsEnabled } from "@/constants/firebase";
import { isSentryEnabled } from "@/constants/sentry";
import router from "@/router";

let hasLoadedFirebaseAnalytics = false;
let hasLoadedSentry = false;

function applyConsent(app: App): void {
  if (isSentryEnabled) {
    if (CookieConsent.acceptedCategory("monitoring")) {
      hasLoadedSentry = true;
      void import("@/instrument").then(({ initSentry }) => initSentry(app));
    } else if (hasLoadedSentry) {
      void import("@/instrument").then(({ disableSentry }) => disableSentry());
    }
  }

  if (isFirebaseAnalyticsEnabled) {
    if (CookieConsent.acceptedCategory("analytics")) {
      hasLoadedFirebaseAnalytics = true;
      void import("@/services/firebase").then(({ initFirebaseAnalytics }) =>
        initFirebaseAnalytics(router),
      );
    } else if (hasLoadedFirebaseAnalytics) {
      void import("@/services/firebase").then(({ disableFirebaseAnalytics }) =>
        disableFirebaseAnalytics(),
      );
    }
  }
}

export function setupCookieConsent(app: App): void {
  const categories: CookieConsent.CookieConsentConfig["categories"] = {
    necessary: {
      enabled: true,
      readOnly: true,
    },
  };

  if (isSentryEnabled) {
    categories.monitoring = {
      autoClear: {
        cookies: [{ name: /^sentry/ }],
      },
    };
  }

  if (isFirebaseAnalyticsEnabled) {
    categories.analytics = {
      autoClear: {
        cookies: [{ name: /^_ga/ }, { name: "_gid" }],
      },
    };
  }

  const preferenceSections = [
    {
      title: "Strictly necessary",
      description:
        "These cookies are essential for the site to function (authentication, session management).",
      linkedCategory: "necessary",
    },
    ...(isFirebaseAnalyticsEnabled
      ? [
          {
            title: "Analytics",
            description:
              "Firebase Analytics helps us understand how visitors interact with the site.",
            linkedCategory: "analytics",
            cookieTable: {
              headers: {
                name: "Name",
                domain: "Domain",
                description: "Description",
              },
              body: [
                {
                  name: "_ga",
                  domain: "google.com",
                  description: "Distinguishes unique users for Firebase Analytics.",
                },
                {
                  name: "_gid",
                  domain: "google.com",
                  description: "Distinguishes unique users for Firebase Analytics (24h).",
                },
              ],
            },
          },
        ]
      : []),
    ...(isSentryEnabled
      ? [
          {
            title: "Error monitoring",
            description:
              "Sentry captures errors and performance data to help us fix issues faster.",
            linkedCategory: "monitoring",
          },
        ]
      : []),
  ];

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

    categories,

    onConsent: () => applyConsent(app),
    onChange: () => applyConsent(app),

    language: {
      default: "en",
      translations: {
        en: {
          consentModal: {
            title: "Cookie preferences",
            description:
              isFirebaseAnalyticsEnabled && isSentryEnabled
                ? "This site uses cookies for analytics and error monitoring to improve your experience. You can choose which categories to allow."
                : isFirebaseAnalyticsEnabled
                  ? "This site uses cookies for analytics to improve your experience. You can choose which categories to allow."
                  : isSentryEnabled
                    ? "This site uses cookies for error monitoring to improve your experience. You can choose which categories to allow."
                    : "This site uses essential cookies only.",
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
            sections: preferenceSections,
          },
        },
      },
    },
  });
}
