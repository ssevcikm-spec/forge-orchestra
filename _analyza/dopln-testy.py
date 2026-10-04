"""Doplní do tests/run_tests.gd FUNKČNÍ kontroly místo `has_method`.

Co to řeší (naměřeno 2. 10. 2026): testy se ptaly jen `has_method("save")`
a soubor, který se nenačetl, se TIŠE PŘESKOČIL (`if sc != null`). Proto prošly
PR #28/#29/#30 zeleným CI, i když `hud.gd` spadl v `_ready()` na `margin_left`,
`save.gd` uložil jen pozici hráče a vrátil `true` a `mining.gd` spadl na
`node.has()`.

Zapisuje se bajty (žádný převod konců řádků) a každý vzor musí sednout 1×.
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CESTA = Path(r"C:\Users\Ssevc\Local-Deepseek\_analyza\merge-scratch\tests\run_tests.gd")

STARY_MININING = '''	var mining_sc = load("res://scripts/mining.gd")
	if mining_sc != null:
		var mn = _instantiate("těžba", "res://scripts/mining.gd")
		_check(mn.has_method("gather"), "mining.gd poskytuje gather(node)")
		_zavri(mn)
'''

NOVY_MINING = '''	# ------------------------------------------------------------ těžba ----
	# FUNKČNÍ kontrola, ne jen `has_method`. Naměřeno 2. 10. 2026: `mining.gd`
	# volal `node.has()` (Godot 3 API, v Godot 4 neexistuje) a služby hledal na
	# `/root/Skills`, což v projektu není (žádný autoload) – `gather()` tedy
	# VŽDY spadlo. Testy to neviděly, protože se ptaly jen na přítomnost metody.
	var mining_sc = load("res://scripts/mining.gd")
	_check(mining_sc != null, "mining.gd jde načíst (dřív se nenačtený přeskočil)")
	if mining_sc != null:
		var kostra_t = _kostra_registru()
		root.add_child(kostra_t)
		var skilly_t = TestSkilly.new()
		skilly_t.dovednosti["tezba"] = 55
		kostra_t.add_child(skilly_t)
		kostra_t.pridej("Skills", skilly_t)
		var svet_t = TestSvet.new()
		kostra_t.add_child(svet_t)
		kostra_t.pridej("World", svet_t)

		var mn = mining_sc.new()
		kostra_t.add_child(mn)
		var ruda = TestUzelSuroviny.new()
		ruda.resource_id = "iron_ore"
		ruda.difficulty = 5
		var vynos = mn.gather(ruda)
		_check(vynos == 6, "mining.gather() vrátí 1+(55-5)/10 = 6 (naměřeno: %s)" % str(vynos))
		_check(int(skilly_t.hodnota("tezba")) == 56,
			"mining.gather() zvedne dovednost o 1 (55 → %d)" % int(skilly_t.hodnota("tezba")))
		_check(svet_t.zavolano == 1,
			"mining.gather() oznámí světu gather(cell) (volání: %d)" % svet_t.zavolano)

		var drevo = TestUzelSuroviny.new()
		drevo.resource_id = "wood"
		drevo.difficulty = 5
		skilly_t.dovednosti["drevorubectvi"] = 30
		_check(mn.gather(drevo) == 3, "dřevo jde na dovednost drevorubectvi")

		# Negativní kontrola: bez registru se gather() nesmí tvářit jako úspěch.
		var mn_bez = mining_sc.new()
		root.add_child(mn_bez)
		_check(mn_bez.gather(TestUzelSuroviny.new()) == 0,
			"mining.gather() bez registru vrátí 0 a ohlásí to (žádná tichá nula)")
		_zavri(mn_bez)
		_zavri(ruda)
		_zavri(drevo)
		_zavri(kostra_t)
'''

STARE_SAVE_HUD = '''	var save_sc = load("res://scripts/save.gd")
	if save_sc != null:
		var sv = _instantiate("ukládání", "res://scripts/save.gd")
		_check(sv.has_method("save") and sv.has_method("load"), "save.gd poskytuje save/load")
		_zavri(sv)

	var hud_sc = load("res://scripts/hud.gd")
	if hud_sc != null:
		var hu = _instantiate("HUD", "res://scripts/hud.gd")
		_check(hu.has_method("update"), "hud.gd poskytuje update()")
		_zavri(hu)
'''

NOVY_SAVE_HUD = '''	# ------------------------------------------------- ukládání a HUD ----
	# FUNKČNÍ kontroly. Dřív tu bylo jen `has_method("save")` a nenačtený soubor
	# se tiše přeskočil – proto prošly PR #28 a #29 zeleným CI, i když:
	#   * `save.gd` hledal komponenty ve skupinách, které nikdo nezakládá →
	#     uložil jen pozici hráče (35 B) a PŘESTO vrátil `true`,
	#   * `hud.gd` spadl v `_ready()` na `margin_left` (Godot 4 zná `offset_*`)
	#     a na `has_property()` → lišta se vůbec nepřidala do scény.
	# Teď se funkce OPRAVDU zavolají, a to proti zkušební kostře s registrem
	# `component(id)` (docs/ARCHITEKTURA.md:145) – stejné rozhraní, jaké bude
	# mít `game.gd` po granuli engine.shell.
	var save_sc = load("res://scripts/save.gd")
	_check(save_sc != null, "save.gd jde načíst (dřív se nenačtený přeskočil)")
	var hud_sc = load("res://scripts/hud.gd")
	_check(hud_sc != null, "hud.gd jde načíst (dřív se nenačtený přeskočil)")

	if save_sc != null and hud_sc != null:
		# Aby testy nepřepsaly rozehranou pozici hráče, uložený soubor se na konci
		# vrátí do původního stavu (nebo se smaže, když předtím nebyl).
		var existoval_pred := FileAccess.file_exists("user://save.cfg")
		var ulozeny_pred := PackedByteArray()
		if existoval_pred:
			ulozeny_pred = FileAccess.get_file_as_bytes("user://save.cfg")

		var kostra = _kostra_registru()
		root.add_child(kostra)
		var atr = TestAtributy.new()
		atr.Str = 13
		atr.Dex = 17
		atr.Int = 21
		var skl = TestSkilly.new()
		skl.dovednosti["tezba"] = 7
		var eko = TestEkonomika.new()
		eko._gold = 42
		var hrac_t = TestHrac.new()
		hrac_t.position = Vector2(48, 96)
		for dvojice in [[atr, "Attributes"], [skl, "Skills"], [eko, "Economy"], [hrac_t, "Player"]]:
			kostra.add_child(dvojice[0])
			kostra.pridej(dvojice[1], dvojice[0])

		var sv = save_sc.new()
		kostra.add_child(sv)
		_check(sv.save() == true, "save() uloží stav a vrátí true")
		var cfg := ConfigFile.new()
		var nacteno := cfg.load("user://save.cfg")
		_check(nacteno == OK, "save.cfg jde načíst")
		if nacteno == OK:
			_check(int(cfg.get_value("attributes", "Str", -1)) == 13,
				"save() uloží atributy (Str=%d)" % int(cfg.get_value("attributes", "Str", -1)))
			_check(int(cfg.get_value("economy", "gold", -1)) == 42,
				"save() uloží zlato (%d)" % int(cfg.get_value("economy", "gold", -1)))
			var dov = cfg.get_value("skills", "dovednosti", {})
			_check(dov is Dictionary and int(dov.get("tezba", -1)) == 7, "save() uloží dovednosti")
			_check(cfg.has_section_key("player", "position"), "save() uloží pozici hráče")

		# Změň stav a načti ho zpět – ověří se tím i `load()`, ne jen zápis.
		atr.Str = 1
		skl.dovednosti["tezba"] = 0
		eko._gold = 0
		hrac_t.position = Vector2.ZERO
		_check(sv.load() == true, "load() vrátí true")
		_check(atr.Str == 13 and eko._gold == 42 and int(skl.hodnota("tezba")) == 7
			and hrac_t.position == Vector2(48, 96),
			"load() vrátí uložený stav (Str=%d, zlato=%d, tezba=%d)"
				% [atr.Str, eko._gold, int(skl.hodnota("tezba"))])

		# Negativní kontrola: bez registru se `save()` NESMÍ tvářit jako úspěch.
		var sv_bez = save_sc.new()
		root.add_child(sv_bez)
		_check(sv_bez.save() == false,
			"save() bez registru komponent vrátí false (dřív vracel true nad prázdnem)")
		_zavri(sv_bez)

		# HUD: musí se opravdu přidat do scény a ukázat hodnoty z registru.
		var hu = hud_sc.new()
		kostra.add_child(hu)
		_check(hu.get_child_count() == 1,
			"hud.gd přidá label do scény (dětí: %d)" % hu.get_child_count())
		if hu._label != null:
			var text_l: String = str(hu._label.text)
			_check(text_l.contains("Str: 13"), "HUD ukazuje atributy z registru")
			_check(text_l.contains("Zlato: 42"), "HUD ukazuje zlato z registru")
			_check(text_l.contains("tezba: 7"), "HUD ukazuje dovednosti z registru")
		else:
			_check(false, "hud.gd nemá label – spadl v _ready()?")

		if existoval_pred:
			var f = FileAccess.open("user://save.cfg", FileAccess.WRITE)
			if f != null:
				f.store_buffer(ulozeny_pred)
				f.close()
		else:
			DirAccess.remove_absolute(ProjectSettings.globalize_path("user://save.cfg"))
		_zavri(kostra)
'''

POMOCNE = '''

func _kostra_registru():
	"""Zkušební kostra s `component(id)` – totéž rozhraní, jaké bude mít
	`game.gd` (docs/ARCHITEKTURA.md:145). Komponenty berou služby z registru
	na svém RODIČI; tímhle se to ověří, aniž by testy pouštěly celou hru."""
	var k = TestKostra.new()
	k.name = "TestKostra"
	return k


class TestKostra:
	extends Node
	var komponenty := {}

	func component(id: String):
		return komponenty.get(id)

	func pridej(id: String, uzel: Node) -> void:
		komponenty[id] = uzel


class TestAtributy:
	extends Node
	var Str := 10
	var Dex := 10
	var Int := 10


class TestSkilly:
	extends Node
	var dovednosti: Dictionary = {"tezba": 0, "drevorubectvi": 0, "kovarstvi": 0, "boj_na_blizko": 0}

	func hodnota(skill: String) -> int:
		return int(dovednosti.get(skill, 0))

	func add(skill: String, n: int) -> void:
		if dovednosti.has(skill):
			dovednosti[skill] = clamp(int(dovednosti[skill]) + n, 0, 100)


class TestEkonomika:
	extends Node
	var _gold := 0

	func gold(_player) -> int:
		return _gold


class TestHrac:
	extends Node2D


class TestSvet:
	extends Node
	var zavolano := 0
	var posledni_cell = null

	func gather(cell) -> bool:
		zavolano += 1
		posledni_cell = cell
		return true


class TestUzelSuroviny:
	extends Node
	var resource_id := "iron_ore"
	var difficulty := 10
	var cell := Vector2i(1, 1)
'''

bajty = CESTA.read_bytes()
text = bajty.decode("utf-8")
crlf = text.count("\r\n")
lf = text.count("\n") - crlf
print(f"konce řádků v souboru: CRLF={crlf}, LF={lf} → {'CRLF' if crlf > lf else 'LF'}")

def na_konce(s: str) -> str:
    return s.replace("\n", "\r\n") if crlf > lf else s

chyby = 0
for stary, novy, popis in [
    (STARY_MININING, NOVY_MINING, "těžba: funkční kontrola místo has_method"),
    (STARE_SAVE_HUD, NOVY_SAVE_HUD, "ukládání + HUD: funkční kontroly místo has_method"),
]:
    stary_k = na_konce(stary)
    if text.count(stary_k) != 1:
        print(f"CHYBA: {popis} — vzor nalezen {text.count(stary_k)}× (musí být 1×)")
        chyby += 1
        continue
    text = text.replace(stary_k, na_konce(novy))
    print(f"OK    {popis}")

if chyby:
    print("NIC SE NEZAPSALO")
    sys.exit(1)

# Pomocné stuby na konec souboru (za `_zavri`) — jen když tam ještě nejsou.
if "class TestKostra:" in text:
    print("POZOR: stuby už v souboru jsou, nepřidávám je znovu")
else:
    text = text.rstrip("\r\n") + na_konce(POMOCNE)
    print("OK    stuby komponent + _kostra_registru() na konec souboru")

CESTA.write_bytes(text.encode("utf-8"))
print(f"\nZapsáno: {len(text.encode('utf-8'))} B")
