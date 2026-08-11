import { Hero } from "@/components/home/Hero";
import { ScamStory } from "@/components/home/ScamStory";
import { StatsStory } from "@/components/home/StatsStory";
import { HowItWorks } from "@/components/home/HowItWorks";
import { LiveDemo } from "@/components/home/LiveDemo";
import { AlertsSection } from "@/components/home/AlertsSection";
import { EducationTeaser } from "@/components/home/EducationTeaser";
import { ExtensionSection } from "@/components/home/ExtensionSection";
import { ConfidenceSection } from "@/components/home/ConfidenceSection";
import { InstitutionalTeaser } from "@/components/home/InstitutionalTeaser";
import { FinalCta } from "@/components/home/FinalCta";

export default function Home() {
  return (
    <main>
      {/* Arc narratif : entrée → menace → échelle → mécanique → essai →
          communauté → apprentissage → outil → confiance → ressources → action */}
      <Hero />
      <ScamStory />
      <StatsStory />
      <HowItWorks />
      <LiveDemo />
      <AlertsSection />
      <EducationTeaser />
      <ExtensionSection />
      <ConfidenceSection />
      <InstitutionalTeaser />
      <FinalCta />
    </main>
  );
}
