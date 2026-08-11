import { Button } from "./Button";

export function LoadingState({ label = "Chargement…" }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 rounded-lg border border-base bg-app px-5 py-6 text-sm text-muted">
      <span
        className="h-4 w-4 animate-spin rounded-full border-2 border-[var(--brand-soft)] border-t-transparent"
        aria-hidden="true"
      />
      {label}
    </div>
  );
}

export function EmptyState({
  title,
  description,
}: {
  title: string;
  description?: string;
}) {
  return (
    <div className="rounded-lg border border-dashed border-base bg-app px-6 py-10 text-center">
      <p className="text-sm font-semibold text-body">{title}</p>
      {description ? <p className="mx-auto mt-1.5 max-w-sm text-sm text-muted">{description}</p> : null}
    </div>
  );
}

export function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="flex flex-col items-start gap-3 rounded-lg border border-base bg-danger-soft px-5 py-5 sm:flex-row sm:items-center sm:justify-between">
      <p className="text-sm text-body">{message}</p>
      {onRetry ? (
        <Button variant="outline" size="md" onClick={onRetry} className="flex-none">
          Réessayer
        </Button>
      ) : null}
    </div>
  );
}
