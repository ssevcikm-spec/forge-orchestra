# A3 — CO BRÁNY UDĚLAJÍ S NOVÝMI GRANULEMI (surový záznam z měření)

**Co tenhle dokument JE:** surový záznam měření k Úkolu A3 ze
`NEXT-SESSION-INSTRUKCE.md`. **Co NENÍ:** analýza ani návrh.

**Datum měření:** 2. 10. 2026 · **kód hry:** `main` = `194735d`

Reprodukce (měřeno na kopii, klon uživatele se nemění):

```powershell
$env:APPDATA = "$PWD\_analyza\godot-appdata"
& orchestra\tools\godot\Godot_v4.7.2-stable_win64_console.exe --headless --path <projekt> --script res://tests/run_tests.gd
```

## 1) `main` tak, jak je

```
[test] 59 kontrol, 0 selhání
(exit=0)
```

## 2) `main` + třířádkový `move()` (nic jiného se nezměnilo)

Vložený kód **není** implementace smlouvy — nemá `hp`, `inventory` ani
`die()`. Je to nejmenší metoda se správným jménem, která zapne
podmíněný blok v `tests/run_tests.gd` (`if player.has_method("move")`).

```
[test] FAIL player volá izo projekci přes world, ne přes level
[test] 60 kontrol, 1 selhání
(exit=1)
```

## Co z toho plyne

- Rozdíl **59/0 → 60/1** je jediná kontrola, která se dřív vůbec
  nespustila. Blok se **tiše přeskakoval** — a `59 kontrol, 0 selhání`
  vypadá stejně jako naměřená nula.
- Ta kontrola je **falešný poplach na legitimním kódu**: zakazuje
  řetězec `level.iso_position`, který `scripts/player.gd:40` obsahuje
  odjakživa — a `level.gd` `iso_position` vůbec nemá, takže větev je
  mrtvá. Test tedy netvrdí nic o izometrii; měří přítomnost řetězce.
- **Žádná** kontrola nevolá `hp`, `inventory`, `die()`, `snapshot()` ani
  `restore()` — brána tyhle smlouvy vůbec neotevře.
- `world.gd` v `main` **není** (přesunut do `_retired/`); `TestsSvet`
  v testech je **atrapa**, která `gather()` jen počítá. Reálný
  `world.gd` tedy nezavolá nic.
