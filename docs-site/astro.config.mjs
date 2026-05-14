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
            { label: "Agent Guide", slug: "agents" },
            { label: "AI Integration & Skills", slug: "ai" },
            { label: "Workflows", slug: "workflows" },
          ],
        },
        {
          label: "Reference",
          items: [
            { label: "Commands", slug: "commands" },
            { label: "JSON Results", slug: "json-results" },
            { label: "MCP And Plugins", slug: "mcp" },
            { label: "Data Sources", slug: "data-sources" },
            { label: "Trust", slug: "trust" },
            { label: "Disclaimer", slug: "disclaimer" },
          ],
        },
        {
          label: "Namespaces",
          items: [
            { label: "sources", slug: "namespaces/sources" },
            { label: "filings", slug: "namespaces/filings" },
            { label: "document", slug: "namespaces/document" },
            { label: "market", slug: "namespaces/market" },
            { label: "calendar", slug: "namespaces/calendar" },
            { label: "sector", slug: "namespaces/sector" },
            { label: "industry", slug: "namespaces/industry" },
            { label: "screen", slug: "namespaces/screen" },
            { label: "symbol", slug: "namespaces/symbol" },
            { label: "fundamentals", slug: "namespaces/fundamentals" },
            { label: "news", slug: "namespaces/news" },
            { label: "price", slug: "namespaces/price" },
            { label: "transcripts", slug: "namespaces/transcripts" },
            { label: "kpi", slug: "namespaces/kpi" },
            { label: "ir", slug: "namespaces/ir" },
            { label: "formula", slug: "namespaces/formula" },
            { label: "valuation", slug: "namespaces/valuation" },
            { label: "estimates", slug: "namespaces/estimates" },
            { label: "research", slug: "namespaces/research" },
            { label: "backtest", slug: "namespaces/backtest" },
          ],
        },
      ],
    }),
  ],
});
