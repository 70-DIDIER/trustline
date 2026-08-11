// Lint léger sans dépendance : vérifie la syntaxe de chaque fichier .js de src/
// via `node --check`. (Pas de eval, pas de code distant : tout est local.)
import { readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { execFileSync } from "node:child_process";

function walk(dir) {
  const out = [];
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) out.push(...walk(p));
    else if (p.endsWith(".js")) out.push(p);
  }
  return out;
}

const files = walk("src");
let failed = 0;
for (const f of files) {
  try {
    execFileSync(process.execPath, ["--check", f], { stdio: "pipe" });
    process.stdout.write(`  ✓ ${f}\n`);
  } catch (e) {
    failed++;
    process.stdout.write(`  ✗ ${f}\n${e.stderr?.toString() || e.message}\n`);
  }
}
if (failed) {
  console.error(`\n${failed} fichier(s) en erreur.`);
  process.exit(1);
}
console.log(`\n${files.length} fichiers OK — aucune erreur de syntaxe.`);
