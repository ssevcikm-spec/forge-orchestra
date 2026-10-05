# -*- coding: utf-8 -*-
"""P16/D — je záloha `_archiv` POUŽITELNÁ? (ne jen spočítaná)

P15 zálohu **vytvořila** a ověřila SHA-256 při zápisu. To ale nedokazuje, že se
z ní dá **obnovit** — a záloha, ze které se obnovit nedá, je horší než žádná,
protože vypadá jako záloha.

Postup (nic se nepřepisuje, nic se nemaže):
  1. `zalohuj-archiv.py --jen-kontrola` → musí hlásit shodu,
  2. **3 soubory z manifestu** (záměrně různé: `.py`, `.mjs`, `.json`, kdyby
     byly po ruce) se obnoví do **VLASTNÍHO** adresáře `p16d-obnovene/`,
  3. porovná se **SHA-256**: obnovený ↔ záloha ↔ ZDROJ (`_analyza/_archiv/`),
  4. zkouška **negativní kontroly**: vezme se hash souboru, který v záloze JE,
     a porovná s jiným souborem → musí se ROZEJÍT (jinak hash nic neměří),
  5. sepíše se, **co záloha NEUMÍ**.
"""

import hashlib
import json
import pathlib
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
ARCHIV = ANALYZA / "_archiv"
STANICE = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek")
ZALOHA = STANICE / "_zalohy" / "forge-orchestra"
OBAL = ANALYZA / "p16d-obnovene"
SKRIPT = ANALYZA / "zalohuj-archiv.py"

kontrol = 0
chyb = 0


def zk(ok, popis, detail=""):
    global kontrol, chyb
    kontrol += 1
    if ok:
        print(f"  OK   {popis}" + (f"  [{detail}]" if detail else ""))
    else:
        chyb += 1
        print(f"  CHYBA {popis}" + (f"  [{detail}]" if detail else ""))


def sha(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


print("=" * 78)
print("P16/D — je záloha POUŽITELNÁ? (obnova 3 souborů + SHA-256)")
print("=" * 78)
print(f"  záloha: {ZALOHA}")

# ── 1) kontrola manifestu skriptem P15 ─────────────────────────────────────
r = subprocess.run([sys.executable, str(SKRIPT), "--jen-kontrola"],
                   capture_output=True, cwd=str(WS))
v = (r.stdout or b"").decode("utf-8", "replace") \
    + (r.stderr or b"").decode("utf-8", "replace")
print(f"\n--- 1) `zalohuj-archiv.py --jen-kontrola`: exit={r.returncode} ---------")
for l in v.splitlines():
    if l.strip():
        print(f"      {l.strip()[:96]}")
zk(r.returncode == 0, "kontrola zálohy skriptem P15 hlásí shodu", f"exit={r.returncode}")

# ── 2) manifest a jeho nezávislé přečtení ─────────────────────────────────
print("\n--- 2) MANIFEST.json: co v záloze je ---------------------------------")
mj = ZALOHA / "MANIFEST.json"
zk(mj.is_file(), f"{mj.name} existuje")
data = json.loads(mj.read_text(encoding="utf-8"))
print(f"  typ záznamu: {type(data).__name__}, klíčů: "
      f"{len(data) if isinstance(data, dict) else len(data)}")
soubory = data.get("soubory", data) if isinstance(data, dict) else data
if isinstance(soubory, dict):
    polozky = list(soubory.items())
else:
    polozky = [(x.get("cesta") or x.get("soubor") or x.get("name"), x.get("sha256") or x.get("hash"))
               for x in soubory]
print(f"  položek v manifestu: {len(polozky)}; příklad: {polozky[0]}")

# nezávislý počet souborů (rglob) — proti manifestu i proti tvrzení 347
v_zal = sorted(p for p in ZALOHA.rglob("*") if p.is_file()
               and p.name not in ("MANIFEST.json", "MANIFEST.txt"))
v_src = sorted(p for p in ARCHIV.rglob("*") if p.is_file())
print(f"  nezávisle spočítáno: v záloze {len(v_zal)} souborů, "
      f"ve zdroji {len(v_src)}")
zk(len(v_zal) == 347, "tvrzení F: v záloze je 347 souborů (rglob, ne manifest)",
   f"{len(v_zal)}")
zk(len(v_zal) == len(v_src), "a stejně jako ve zdroji `_analyza/_archiv`",
   f"{len(v_zal)} vs {len(v_src)}")
velikost = sum(p.stat().st_size for p in v_zal)
print(f"  velikost zálohy: {velikost} B = {velikost / 1_000_000:.3f} MB (10^6)"
      f" = {velikost / 1024 / 1024:.3f} MiB (2^20)")
zk(abs(velikost / 1_000_000 - 1.58) < 0.02,
   "tvrzení F: 1,58 MB — jednotka je 10^6 B (ve MiB je to 1,50; "
   "NENÍ to rozpor, jen jiná jednotka)", f"{velikost / 1_000_000:.3f} MB")

# ── 3) obnova 3 souborů do VLASTNÍHO adresáře ─────────────────────────────
print("\n--- 3) obnova 3 souborů do `p16d-obnovene/` -------------------------")
if OBAL.exists():
    shutil.rmtree(OBAL)
OBAL.mkdir(parents=True)
# tři RŮZNÉ soubory (podle přípony), ať obnova netestuje jeden kus třikrát
kandidati = []
for vzor in ("*.py", "*.mjs", "*.json", "*.txt"):
    for p in sorted((ZALOHA / "_archiv").glob(vzor)):
        kandidati.append(p)
        break
zk(len(kandidati) >= 3 and len({p.suffix for p in kandidati}) == len(kandidati),
   "vybrány soubory RŮZNÝCH typů (ne tři kopie téhož druhu)",
   str([p.name for p in kandidati]))

obnovene = []
for z in kandidati:
    cil = OBAL / z.name
    shutil.copyfile(z, cil)                 # TO je obnova: kopie ze zálohy
    zdroj = ARCHIV / z.name
    h_z, h_c, h_s = sha(z), sha(cil), (sha(zdroj) if zdroj.is_file() else "CHYBI")
    obnovene.append((z.name, h_z, h_c, h_s))
    print(f"  {z.name:<40} záloha={h_z[:12]} obnoveno={h_c[:12]} zdroj={h_s[:12]}")
    zk(h_c == h_z, f"{z.name}: obnovený soubor má SHODNÝ SHA-256 se zálohou")
    zk(h_z == h_s, f"{z.name}: a záloha má SHODNÝ SHA-256 se ZDROJEM")

# ── 4) negativní kontrola hashe ───────────────────────────────────────────
print("\n--- 4) negativní kontrola: hash musí umět ROZEJÍT --------------------")
a, b = obnovene[0], obnovene[1]
zk(a[1] != b[1], "SHA-256 dvou RŮZNÝCH souborů se liší → hash něco měří",
   f"{a[0]} vs {b[0]}")

# ── 5) co záloha NEUMÍ ───────────────────────────────────────────────────
print("\n--- 5) CO ZÁLOHA NEUMÍ (přiznaná mez) --------------------------------")
chybi_v_zaloze = [p.name for p in v_src if not (ZALOHA / "_archiv" / p.name).is_file()]
print(f"  a) soubor, který v záloze NENÍ, se neobnoví — naměřeno: "
      f"{len(chybi_v_zaloze)} chybějících")
print(f"  b) záloha NEMÁ HISTORII — je to kopie posledního stavu (jeden snapshot);"
      f" starší verze téhož souboru se z ní nedostane")
print(f"  c) záloha je na TÉMŽ STROJI (jiný disk, ne jiné místo) — chrání proti"
      f" pádu `E:`, ne proti ztrátě počítače")
print(f"  d) záloha je RUČNÍ — kdo do `_archiv` sáhne, musí skript spustit"
      f" (žádný cron/hook ji nespouští)")
print(f"  e) zálohuje se JEN `_analyza/_archiv` + `_zaloha*`; zbytek `_analyza`"
      f" (živé nástroje) v záloze NENÍ")
zk(len(chybi_v_zaloze) == 0,
   "a) dnes v záloze nechybí ani jeden soubor zdroje (ale viz mez a–e)")

print("\n" + "=" * 78)
print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb")
print("=" * 78)
sys.exit(1 if chyb else 0)
