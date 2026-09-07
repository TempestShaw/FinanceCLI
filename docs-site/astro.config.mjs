import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

export default defineConfig({
  site: "https://tempestshaw.github.io",
  base: "/FinanceCLI",
  integrations: [
    starlight({
      title: "Finance CLI",
      description: "Financial research tools for you and your AI agent, with traceable sources and reproducible calculations.",
      customCss: ["./src/styles/custom.css"],
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
            { label: "AI Integration & Skills", slug: "ai" },
            { label: "Quick Start", slug: "quickstart" },
            { label: "Research Examples", slug: "research-examples" },
            { label: "Agent Guide", slug: "agents" },
            { label: "Agent Output Formats", slug: "agent-output-formats" },
            { label: "Workflows", slug: "workflows" },
          ],
        },
        {
          label: "Reference",
          items: [
            { label: "Commands", slug: "commands" },
            { label: "Namespaces", slug: "namespaces" },
            { label: "JSON Results", slug: "json-results" },
            { label: "MCP And Plugins", slug: "mcp" },
            { label: "Data Sources", slug: "data-sources" },
            { label: "Trust", slug: "trust" },
            { label: "Disclaimer", slug: "disclaimer" },
          ],
        },
        {
          label: "Use Cases",
          items: [
            {
              label: "Setup & Planning",
              collapsed: true,
              items: [
                { label: "Sources", slug: "namespaces/sources" },
                { label: "Research", slug: "namespaces/research" },
              ],
            },
            {
              label: "Filings & Documents",
              collapsed: true,
              items: [
                { label: "Filings", slug: "namespaces/filings" },
                { label: "Document", slug: "namespaces/document" },
                { label: "IR", slug: "namespaces/ir" },
              ],
            },
            {
              label: "Market Discovery",
              collapsed: true,
              items: [
                { label: "Symbol", slug: "namespaces/symbol" },
                { label: "Market", slug: "namespaces/market" },
                { label: "Calendar", slug: "namespaces/calendar" },
                { label: "Sector", slug: "namespaces/sector" },
                { label: "Industry", slug: "namespaces/industry" },
                { label: "Screen", slug: "namespaces/screen" },
                { label: "Fundamentals", slug: "namespaces/fundamentals" },
              ],
            },
            {
              label: "News & Evidence",
              collapsed: true,
              items: [
                { label: "Price", slug: "namespaces/price" },
                { label: "Transcripts", slug: "namespaces/transcripts" },
              ],
            },
            {
              label: "Calculators & Backtests",
              collapsed: true,
              items: [
                { label: "Formula", slug: "namespaces/formula" },
                { label: "Valuation", slug: "namespaces/valuation" },
                { label: "Estimates", slug: "namespaces/estimates" },
                { label: "Backtest", slug: "namespaces/backtest" },
              ],
            },
          ],
        },
      ],
    }),
  ],
});
