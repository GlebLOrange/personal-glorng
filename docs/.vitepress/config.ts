import { defineConfig } from "vitepress";

export default defineConfig({
  title: "gLOrng",
  description: "Developer portfolio and personal platform documentation",
  ignoreDeadLinks: true,
  themeConfig: {
    nav: [
      { text: "Guide", link: "/guide/getting-started" },
      { text: "Operations", link: "/operations/deployment" },
      { text: "Reference", link: "/reference/platform" },
    ],
    sidebar: {
      "/guide/": [
        {
          text: "Guide",
          items: [
            { text: "Getting started", link: "/guide/getting-started" },
            { text: "Architecture", link: "/guide/architecture" },
            { text: "Development", link: "/guide/development" },
            { text: "Frontend", link: "/guide/frontend" },
            { text: "Contributing", link: "/guide/contributing" },
          ],
        },
      ],
      "/operations/": [
        {
          text: "Operations",
          items: [
            { text: "Deployment", link: "/operations/deployment" },
            { text: "Database", link: "/operations/database" },
            { text: "Backup & restore", link: "/operations/backup-restore" },
            { text: "Cloudflare", link: "/operations/cloudflare" },
            { text: "DevOps checklist", link: "/operations/devops-checklist" },
          ],
        },
      ],
      "/reference/": [
        {
          text: "Reference",
          items: [
            { text: "Platform overview", link: "/reference/platform" },
            { text: "API & tools", link: "/reference/api-tools" },
            { text: "Postman", link: "/reference/postman" },
            { text: "Configuration", link: "/reference/configuration" },
            {
              text: "Integration automation",
              link: "/reference/integration-automation",
            },
            { text: "Security", link: "/reference/security" },
            { text: "Testing", link: "/reference/testing" },
          ],
        },
      ],
      "/specs/": [
        {
          text: "Specs",
          items: [
            { text: "News", link: "/specs/news" },
            {
              text: "Platform hardening",
              link: "/specs/platform-hardening",
            },
          ],
        },
      ],
    },
    socialLinks: [
      {
        icon: "github",
        link: "https://github.com/GlebLOrange/portfolio-glorng",
      },
    ],
  },
});
