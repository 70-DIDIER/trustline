import { cn } from "@/lib/utils";
import Link from "next/link";
import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "outline" | "ghost" | "danger";
type Size = "md" | "lg";

const VARIANT: Record<Variant, string> = {
  primary: "bg-brand hover:bg-[var(--color-primary-hover)] text-on-brand",
  outline: "border border-strong bg-transparent hover:bg-surface-2 text-body",
  ghost: "bg-transparent hover:bg-surface-2 text-body",
  danger: "bg-[var(--danger)] hover:brightness-110 text-white",
};

const SIZE: Record<Size, string> = {
  md: "px-4 py-2.5 text-sm",
  lg: "px-6 py-3.5 text-[0.95rem]",
};

const base =
  "inline-flex items-center justify-center gap-2 rounded-sm font-semibold transition-colors duration-150 disabled:opacity-50 disabled:pointer-events-none whitespace-nowrap";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

export function Button({ variant = "primary", size = "md", className, ...props }: ButtonProps) {
  return <button className={cn(base, VARIANT[variant], SIZE[size], className)} {...props} />;
}

interface ButtonLinkProps {
  href: string;
  variant?: Variant;
  size?: Size;
  className?: string;
  children: React.ReactNode;
  external?: boolean;
}

export function ButtonLink({ href, variant = "primary", size = "md", className, children, external }: ButtonLinkProps) {
  const classes = cn(base, VARIANT[variant], SIZE[size], className);
  if (external) {
    return (
      <a href={href} target="_blank" rel="noopener noreferrer" className={classes}>
        {children}
      </a>
    );
  }
  return (
    <Link href={href} className={classes}>
      {children}
    </Link>
  );
}
