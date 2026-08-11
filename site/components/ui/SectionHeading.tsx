import { cn } from "@/lib/utils";

export function SectionHeading({
  eyebrow,
  title,
  description,
  align = "left",
  className,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  align?: "left" | "center";
  className?: string;
}) {
  return (
    <div className={cn("flex flex-col gap-3", align === "center" && "items-center text-center", className)}>
      {eyebrow ? (
        <span className="font-mono text-xs font-semibold uppercase tracking-[0.14em] text-brand">{eyebrow}</span>
      ) : null}
      <h2 className={cn("font-display text-2xl font-bold tracking-tight text-body sm:text-3xl")}>{title}</h2>
      {description ? (
        <p className={cn("max-w-2xl text-[0.95rem] leading-relaxed text-muted")}>{description}</p>
      ) : null}
    </div>
  );
}
