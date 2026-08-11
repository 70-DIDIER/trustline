import { Reveal } from "@/components/ui/Reveal";

const ETAPES = [
  { n: "01", titre: "Vous recevez", desc: "Un SMS, un appel, un lien ou un message qui vous met un doute." },
  { n: "02", titre: "Vous vérifiez", desc: "Vous le collez dans TrustLine — aucun compte, aucune installation." },
  { n: "03", titre: "TrustLine analyse", desc: "Règles explicables et réputation communautaire, en quelques secondes." },
  { n: "04", titre: "Vous décidez", desc: "Un verdict clair, les signaux détectés, et le geste à faire ensuite." },
];

export function HowItWorks() {
  return (
    <section className="border-y border-base bg-surface-alt">
      <div className="mx-auto max-w-content px-5 py-24 sm:px-8 sm:py-28">
        <Reveal className="max-w-xl">
          <span className="font-mono text-xs font-semibold uppercase tracking-[0.16em] text-muted">
            Comment ça marche
          </span>
          <h2 className="text-display-sm mt-4 font-bold text-body">Du doute à la décision, en quatre temps.</h2>
        </Reveal>

        <div className="relative mt-16">
          <div className="absolute left-0 right-0 top-[22px] hidden h-px bg-border lg:block" aria-hidden="true" />
          <div className="grid grid-cols-1 gap-y-10 sm:grid-cols-2 lg:grid-cols-4 lg:gap-6">
            {ETAPES.map((e, i) => (
              <Reveal key={e.n} delay={i * 110} className="relative">
                <span className="relative z-10 inline-flex h-11 w-11 items-center justify-center rounded-full border border-base bg-app font-mono text-sm font-bold text-brand">
                  {e.n}
                </span>
                <h3 className="mt-5 text-base font-bold text-body">{e.titre}</h3>
                <p className="mt-1.5 max-w-[24ch] text-sm leading-relaxed text-secondary">{e.desc}</p>
              </Reveal>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
