// Build : produit dist/ (extension prête à charger) + trustline-extension.zip.
// Aucun bundler : l'extension est en JS natif (ES modules + content scripts
// classiques), chargeable directement — plus robuste pour une démo (pas de build
// à casser). Ce script ne fait que copier les fichiers d'exécution et zipper.
import { rmSync, mkdirSync, cpSync, existsSync } from "node:fs";
import { execFileSync } from "node:child_process";

const DIST = "dist";
const ZIP = "trustline-extension.zip";
const INCLUDE = ["manifest.json", "src", "public"];

rmSync(DIST, { recursive: true, force: true });
rmSync(ZIP, { force: true });
mkdirSync(DIST, { recursive: true });

for (const item of INCLUDE) {
  if (!existsSync(item)) throw new Error(`Manquant : ${item}`);
  cpSync(item, `${DIST}/${item}`, { recursive: true });
}

// Zip du contenu de dist/ (à la racine du zip, pour "Load unpacked" ou upload store).
try {
  execFileSync("zip", ["-r", "-q", `../${ZIP}`, "."], { cwd: DIST, stdio: "inherit" });
  console.log(`✓ dist/ prêt et ${ZIP} généré.`);
} catch {
  console.log(`✓ dist/ prêt. (zip non disponible : chargez le dossier dist/ tel quel.)`);
}
