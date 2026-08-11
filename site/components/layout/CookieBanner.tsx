"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";

export default function CookieBanner() {
  const [visible, setVisible] = useState(true);
  if (!visible) return null;

  return (
    <div className="shadow-soft fixed inset-x-0 bottom-0 z-30 border-t border-base bg-app">
      <div className="mx-auto flex max-w-content flex-wrap items-center justify-between gap-4 px-5 py-4 text-sm sm:px-8">
        <p className="max-w-2xl text-muted">
          TrustLine utilise des cookies strictement nécessaires au fonctionnement du site. Aucun
          cookie publicitaire, aucun traçage tiers.{" "}
          <a href="/a-propos#confidentialite" className="text-brand underline underline-offset-2">
            En savoir plus
          </a>
          .
        </p>
        <div className="flex flex-none gap-2">
          <Button variant="outline" size="md" onClick={() => setVisible(false)}>
            Refuser
          </Button>
          <Button variant="primary" size="md" onClick={() => setVisible(false)}>
            Accepter
          </Button>
        </div>
      </div>
    </div>
  );
}
