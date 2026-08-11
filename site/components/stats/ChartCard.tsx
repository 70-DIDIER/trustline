import { SectionHeading } from "@/components/ui/SectionHeading";

interface Barre {
  label: string;
  value: number;
}

export function ChartCard({
  title,
  description,
  data,
  tone = "brand",
  source,
  periode,
}: {
  title: string;
  description?: string;
  data: Barre[];
  tone?: "brand" | "blue";
  source?: string;
  periode?: string;
}) {
  const max = Math.max(...data.map((d) => d.value), 1);
  const barColor = tone === "blue" ? "var(--unknown)" : "var(--brand)";

  return (
    <div className="rounded-lg border border-base bg-app p-6">
      <SectionHeading title={title} description={description} />
      <div className="mt-6 flex flex-col gap-3">
        {data.map((d) => (
          <div key={d.label}>
            <div className="mb-1 flex items-center justify-between text-xs">
              <span className="text-body">{d.label}</span>
              <span className="font-mono tabular-nums text-muted">{d.value}</span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-surface-2">
              <div
                className="h-full rounded-full"
                style={{ width: `${Math.max((d.value / max) * 100, 3)}%`, background: barColor }}
              />
            </div>
          </div>
        ))}
      </div>
      {(source || periode) && (
        <p className="mt-5 border-t border-base pt-3 text-[0.7rem] text-muted">
          {source ? <>Source : {source}</> : null}
          {source && periode ? " · " : null}
          {periode ? <>Période : {periode}</> : null}
        </p>
      )}
    </div>
  );
}
