// Sélecteurs DOM isolés par plateforme (§35). Si une plateforme change son DOM,
// on corrige ICI uniquement. Les content scripts n'utilisent jamais de sélecteur
// codé en dur ailleurs. Tout est encapsulé dans window.TL.selectors.
(function () {
  "use strict";
  const TL = (window.TL = window.TL || {});

  // --- WhatsApp Web ---
  const whatsapp = {
    // Bulles de message contenant du texte, dans la zone de conversation.
    findVisibleMessages() {
      const nodes = document.querySelectorAll('div.message-in span.selectable-text, div.message-out span.selectable-text');
      return [...nodes].filter((n) => n.innerText && n.innerText.trim().length > 3);
    },
    messageContainer(el) {
      return el.closest("div.message-in, div.message-out") || el.parentElement;
    },
    messageText(el) {
      return el.innerText || "";
    },
  };

  // --- Abstraction fournisseur d'email (Gmail / Outlook) ---
  function makeMailProvider(cfg) {
    return {
      isOpenEmail: () => !!document.querySelector(cfg.body),
      findEmailBody: () => document.querySelector(cfg.body),
      findEmailBodyText: () => {
        const b = document.querySelector(cfg.body);
        return b ? b.innerText || "" : "";
      },
      findEmailSender: () => {
        const s = document.querySelector(cfg.sender);
        return s ? (s.getAttribute("email") || s.getAttribute("title") || s.innerText || "").trim() : "";
      },
      findEmailSubject: () => {
        const s = document.querySelector(cfg.subject);
        return s ? (s.innerText || "").trim() : "";
      },
      findEmailLinks: () => {
        const b = document.querySelector(cfg.body);
        if (!b) return [];
        return [...b.querySelectorAll("a[href]")].map((a) => a.href).filter((h) => /^https?:/i.test(h));
      },
      anchor: () => document.querySelector(cfg.anchor) || document.querySelector(cfg.subject),
    };
  }

  const gmail = makeMailProvider({
    body: 'div.a3s.aiL, div.a3s',
    sender: 'span.gD, span[email]',
    subject: 'h2.hP',
    anchor: 'h2.hP',
  });

  const outlook = makeMailProvider({
    body: 'div[aria-label="Message body"], div.allowTextSelection, div[role="document"]',
    sender: 'span[title*="@"], span.OZZZK',
    subject: 'div[role="heading"], span.Ssu1I',
    anchor: 'div[role="heading"]',
  });

  // --- Web générique ---
  const web = {
    findVisibleLinks() {
      const anchors = [...document.querySelectorAll('a[href^="http"]')];
      return anchors.filter((a) => {
        const r = a.getBoundingClientRect();
        return r.width > 0 && r.height > 0;
      });
    },
    hasSensitiveForm() {
      return !!document.querySelector('input[type="password"], input[name*="pin" i], input[name*="otp" i], input[autocomplete="one-time-code"]');
    },
  };

  TL.selectors = { whatsapp, gmail, outlook, web };
})();
