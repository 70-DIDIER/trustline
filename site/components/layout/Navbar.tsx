"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { Logo } from "@/components/ui/Logo";

const LINKS = [
  { href: "/", label: "Accueil" },
  { href: "/verifier", label: "Vérifier" },
  { href: "/signaler", label: "Signaler" },
  { href: "/alertes", label: "Alertes" },
  { href: "/statistiques", label: "Statistiques" },
  { href: "/apprendre", label: "Apprendre" },
];

export default function Navbar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={cn(
        "sticky top-0 z-40 border-b bg-[rgba(255,255,255,0.92)] backdrop-blur transition-[height,border-color] duration-200",
        scrolled ? "border-base" : "border-transparent"
      )}
    >
      <div
        className={cn(
          "mx-auto flex max-w-content items-center justify-between gap-4 px-5 transition-[height] duration-200 sm:px-8",
          scrolled ? "h-16" : "h-20"
        )}
      >
        <Link href="/" className="flex-none">
          <Logo priority width={148} className="sm:w-[158px]" />
        </Link>

        <nav className="hidden items-center gap-1 lg:flex" aria-label="Navigation principale">
          {LINKS.map((l) => {
            const active = pathname === l.href;
            return (
              <Link
                key={l.href}
                href={l.href}
                className={cn(
                  "rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  active ? "text-body" : "text-secondary hover:text-body"
                )}
                aria-current={active ? "page" : undefined}
              >
                {l.label}
              </Link>
            );
          })}
        </nav>

        <div className="hidden lg:block">
          <Link
            href="/verifier"
            className="inline-flex items-center gap-2 rounded-md bg-brand px-4 py-2 text-sm font-semibold text-on-brand transition-colors hover:bg-[var(--color-primary-hover)]"
          >
            Vérifier maintenant
          </Link>
        </div>

        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          aria-label={open ? "Fermer le menu" : "Ouvrir le menu"}
          className="grid h-10 w-10 place-items-center rounded-md border border-base text-body lg:hidden"
        >
          {open ? (
            <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" /></svg>
          ) : (
            <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5"><path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" /></svg>
          )}
        </button>
      </div>

      {open ? (
        <div className="border-t border-base bg-app px-5 py-4 lg:hidden">
          <nav className="flex flex-col gap-1" aria-label="Navigation mobile">
            {LINKS.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                className={cn(
                  "rounded-md px-3 py-2.5 text-sm font-medium",
                  pathname === l.href ? "bg-surface text-body" : "text-secondary"
                )}
              >
                {l.label}
              </Link>
            ))}
          </nav>
          <Link
            href="/verifier"
            className="mt-3 flex items-center justify-center rounded-md bg-brand px-4 py-2.5 text-sm font-semibold text-on-brand"
          >
            Vérifier maintenant
          </Link>
        </div>
      ) : null}
    </header>
  );
}
