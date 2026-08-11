import { cn } from "@/lib/utils";

const TONE = {
  neutral: "bg-surface-2 text-muted",
  brand: "bg-trustline-primary/10 text-brand",
  safe: "bg-safe-soft",
  warn: "bg-warn-soft",
  danger: "bg-danger-soft",
} as const;

export function Badge({
  tone = "neutral",
  className,
  children,
}: {
  tone?: keyof typeof TONE;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold",
        TONE[tone],
        className
      )}
    >
      {children}
    </span>
  );
}
