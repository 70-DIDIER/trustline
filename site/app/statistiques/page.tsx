import type { Metadata } from "next";
import { StatistiquesClient } from "./StatistiquesClient";

export const metadata: Metadata = {
  title: "Observatoire",
  description: "Signalements, numéros suivis et analyses effectuées par la communauté TrustLine.",
};

export default function StatistiquesPage() {
  return (
    <main>
      <StatistiquesClient />
    </main>
  );
}
