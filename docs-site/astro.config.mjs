import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

export default defineConfig({
  site: "https://tempestshaw.github.io",
  base: "/FinanceCLI",
  integrations: [
    starlight({
      title: "Finance CLI",
      description: "Public-company research from the terminal.",
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/TempestShaw/FinanceCLI",
        },
      ],
      sidebar: [
        {
          label: "Start",
          items: [
            { label: "Home", slug: "" },
            { label: "Quick Start", slug: "quickstart" },
            { label: "Workflows", slug: "workflows" },
          ],
        },
        {
          label: "Reference",
          items: [
            { label: "Commands", slug: "commands" },
            { label: "Data Sources", slug: "data-sources" },
            { label: "Trust", slug: "trust" },
            { label: "Disclaimer", slug: "disclaimer" },
          ],
        },
      ],
    }),
  ],
});
