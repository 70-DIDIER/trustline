// Configuration des canaux TrustLine. Les URLs de téléchargement sont surchargeables
// via variables d'environnement — jamais codées en dur ailleurs dans l'app.

export const EXTENSION_URL = process.env.NEXT_PUBLIC_EXTENSION_URL || "/trustline-extension.zip";
export const ANDROID_APK_URL = process.env.NEXT_PUBLIC_ANDROID_APK_URL || "";
export const USSD_CODE = process.env.NEXT_PUBLIC_USSD_CODE || "*XXX#";
export const SMS_NUMBER = process.env.NEXT_PUBLIC_SMS_NUMBER || "";

export interface Canal {
  id: string;
  titre: string;
  resume: string;
  disponible: boolean;
  action: { label: string; href: string } | null;
  detail: string;
}

export const CANAUX: Canal[] = [
  {
    id: "android",
    titre: "Application Android",
    resume: "Protection des appels et des SMS directement sur votre téléphone.",
    disponible: Boolean(ANDROID_APK_URL),
    action: ANDROID_APK_URL ? { label: "Télécharger l'APK", href: ANDROID_APK_URL } : null,
    detail: "En cours de finalisation pour ce hackathon — pas encore publiée.",
  },
  {
    id: "chrome",
    titre: "Extension Chrome",
    resume: "Vérification des sites et des liens avant de saisir la moindre donnée.",
    disponible: true,
    action: { label: "Télécharger l'extension (.zip)", href: EXTENSION_URL },
    detail:
      "Après téléchargement : chrome://extensions → activer le mode développeur → « Charger l'extension non empaquetée ».",
  },
  {
    id: "ussd",
    titre: "USSD",
    resume: "Accès à la vérification même sans smartphone, ni connexion internet.",
    disponible: Boolean(process.env.NEXT_PUBLIC_USSD_CODE),
    action: null,
    detail: process.env.NEXT_PUBLIC_USSD_CODE
      ? `Composez ${USSD_CODE} depuis n'importe quel téléphone.`
      : "Code USSD en cours d'attribution auprès des opérateurs — non actif pour cette démonstration.",
  },
  {
    id: "sms",
    titre: "SMS",
    resume: "Transférez un message suspect par SMS pour recevoir un verdict.",
    disponible: Boolean(SMS_NUMBER),
    action: null,
    detail: SMS_NUMBER
      ? `Transférez le message suspect au ${SMS_NUMBER}.`
      : "Passerelle SMS en cours de configuration — non active pour cette démonstration.",
  },
];
