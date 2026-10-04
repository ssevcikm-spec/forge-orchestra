extends SceneTree
# Měření OPRAVENÝCH save.gd a hud.gd — proti zkušební kostře s registrem
# `component(id)`, tedy proti témuž rozhraní, jaké bude mít `game.gd` po
# granuli engine.shell. Obsahuje i NEGATIVNÍ kontroly: kdyby se „tiše neuložilo"
# vrátilo, musí to spadnout tady, ne v produkci.

class Kostra:
	extends Node
	var komponenty := {}
	func component(id: String):
		return komponenty.get(id)
	func pridej(id: String, uzel: Node) -> void:
		komponenty[id] = uzel
	func odeber(id: String) -> void:
		komponenty.erase(id)

class Atributy:
	extends Node
	var Str := 13
	var Dex := 17
	var Int := 21

class Skilly:
	extends Node
	var dovednosti: Dictionary = {"tezba": 7, "drevorubectvi": 1, "kovarstvi": 2, "boj_na_blizko": 3}
	func hodnota(skill: String) -> int:
		return dovednosti.get(skill, 0)
	func add(skill: String, n: int) -> void:
		if dovednosti.has(skill):
			dovednosti[skill] = clamp(dovednosti[skill] + n, 0, 100)

class Svet:
	extends Node
	var zavolano := 0
	var posledni_cell = null
	func gather(cell) -> bool:
		zavolano += 1
		posledni_cell = cell
		return true

class Uzel:
	extends Node
	var resource_id := "iron_ore"
	var difficulty := 10
	var cell := Vector2i(1, 1)

class Ekonomika:
	extends Node
	var _gold := 42
	func gold(_hrac) -> int:
		return _gold

class Hrac:
	extends Node2D          # jako scripts/player.gd: bez `hp`, bez výbavy

class HracSHp:
	extends Node2D
	var hp := 30
	var equipped := "zelezny mec"

var chyby := 0
var _hotovo := false


func _process(_delta: float) -> bool:
	if _hotovo:
		return true
	_hotovo = true

	var kostra := Kostra.new()
	kostra.name = "Main"
	root.add_child(kostra)
	var atributy := Atributy.new()
	var skilly := Skilly.new()
	var ekonomika := Ekonomika.new()
	var hrac := Hrac.new()
	hrac.position = Vector2(48, 96)
	for u in [[atributy, "Attributes"], [skilly, "Skills"], [ekonomika, "Economy"], [hrac, "Player"]]:
		kostra.add_child(u[0])
		kostra.pridej(u[1], u[0])

	# ---------- 1. save() ----------
	print("=== 1. save() s registrem (komponenty existují) ===")
	var ukladani = load("res://save.gd").new()
	kostra.add_child(ukladani)
	_kontrola(ukladani.save() == true, "save() vrátí true")

	var cfg := ConfigFile.new()
	_kontrola(cfg.load("user://save.cfg") == OK, "save.cfg jde načíst")
	_kontrola(cfg.get_value("attributes", "Str", -1) == 13, "uložena síla (Str=13)")
	_kontrola(cfg.get_value("attributes", "Dex", -1) == 17, "uložena obratnost (Dex=17)")
	var dov = cfg.get_value("skills", "dovednosti", {})
	_kontrola(dov is Dictionary and dov.get("tezba", -1) == 7, "uloženy dovednosti (tezba=7)")
	_kontrola(cfg.get_value("economy", "gold", -1) == 42, "uloženo zlato (42)")
	_kontrola(cfg.get_value("player", "position", Vector2.ZERO) == Vector2(48, 96), "uložena pozice hráče")

	# ---------- 2. load() ----------
	print("\n=== 2. load() po změně stavu ===")
	atributy.Str = 1
	atributy.Dex = 1
	skilly.dovednosti["tezba"] = 0
	ekonomika._gold = 0
	hrac.position = Vector2.ZERO
	_kontrola(ukladani.load() == true, "load() vrátí true")
	_kontrola(atributy.Str == 13 and atributy.Dex == 17, "atributy se vrátily (13/17)")
	_kontrola(skilly.hodnota("tezba") == 7, "dovednost se vrátila (tezba=7)")
	_kontrola(ekonomika._gold == 42, "zlato se vrátilo (42)")
	_kontrola(hrac.position == Vector2(48, 96), "pozice se vrátila (48, 96)")

	# ---------- 3. HUD ----------
	print("\n=== 3. HUD čte z registru ===")
	var hud = load("res://hud.gd").new()
	kostra.add_child(hud)
	_kontrola(hud._label != null, "label existuje")
	_kontrola(hud.get_child_count() == 1, "label je PŘIDANÝ do lišty (ne jen vytvořený)")
	_kontrola(hud._label.is_visible_in_tree(), "label je viditelný ve scéně")
	_kontrola(hud._label.position == Vector2(10, 10), "label je v rohu (10, 10)")
	print("  --- text lišty ---")
	print(hud._label.text)
	print("  --- konec textu ---")
	var t: String = hud._label.text
	_kontrola(t.contains("Str: 13"), "lišta ukazuje sílu z registru (13)")
	_kontrola(t.contains("Zlato: 42"), "lišta ukazuje zlato z registru (42)")
	_kontrola(t.contains("tezba: 7"), "lišta ukazuje dovednost (tezba: 7)")

	# ---------- 4. HUD s hráčem, který MÁ hp a výbavu ----------
	print("\n=== 4. HUD, když hráč má hp a výbavu ===")
	var hrac2 := HracSHp.new()
	kostra.add_child(hrac2)
	kostra.pridej("Player", hrac2)
	hud.update()
	_kontrola(hud._label.text.contains("HP: 30"), "HP se přečte přes vlastnost `hp`")
	_kontrola(hud._label.text.contains("zelezny mec"), "výbava se přečte přes vlastnost `equipped`")

	# ---------- 5. NEGATIVNÍ KONTROLA: bez registru se nesmí tvářit jako úspěch ----------
	print("\n=== 5. Negativní kontrola: save.gd BEZ kostry (dřív vracel true) ===")
	var samotne = load("res://save.gd").new()
	root.add_child(samotne)
	_kontrola(samotne.save() == false, "save() vrátí false, když není co uložit")

	# ---------- 6. NEGATIVNÍ KONTROLA: část komponent chybí ----------
	print("\n=== 6. Negativní kontrola: chybí Economy (musí to ohlásit) ===")
	kostra.odeber("Economy")
	var cfg2 := ConfigFile.new()
	cfg2.load("user://save.cfg")
	DirAccess.remove_absolute(ProjectSettings.globalize_path("user://save.cfg"))
	_kontrola(ukladani.save() == true, "save() i tak projde (zbytek uložit jde)")
	var cfg3 := ConfigFile.new()
	cfg3.load("user://save.cfg")
	_kontrola(not cfg3.has_section("economy"), "sekce economy se opravdu neuložila")
	_kontrola(cfg3.has_section("attributes"), "atributy se uložily")

	# ---------- 7. HUD bez kostry nesmí spadnout ----------
	print("\n=== 7. Negativní kontrola: HUD bez kostry ===")
	var hud2 = load("res://hud.gd").new()
	root.add_child(hud2)
	_kontrola(hud2._label != null, "lišta se i bez registru vytvoří (nuly, žádná chyba)")

	# ---------- 8. mining.gd (#30) — registr místo /root a Godot 4 API ----------
	print("\n=== 8. mining.gd: registr komponent + Godot 4 API (žádné `has()`) ===")
	var svet := Svet.new()
	kostra.add_child(svet)
	kostra.pridej("World", svet)
	skilly.dovednosti["tezba"] = 55
	var tezba_skript = load("res://mining.gd").new()
	kostra.add_child(tezba_skript)
	var uzel := Uzel.new()
	uzel.difficulty = 5
	var vynos = tezba_skript.gather(uzel)
	_kontrola(vynos == 6, "výtěžek 1 + (55-5)/10 = 6 (došlo se až na Skills)")
	_kontrola(skilly.hodnota("tezba") == 56, "skill se zvedl o 1 (55 → 56)")
	_kontrola(svet.zavolano == 1, "world.gather(cell) se zavolalo")
	_kontrola(svet.posledni_cell == Vector2i(1, 1), "předalo se správné pole")

	var drevo := Uzel.new()
	drevo.resource_id = "wood"
	drevo.difficulty = 5
	skilly.dovednosti["drevorubectvi"] = 30
	_kontrola(tezba_skript.gather(drevo) == 3, "dřevo jde na drevorubectvi: 1 + (30-5)/10 = 3")

	var bez_registru = load("res://mining.gd").new()
	root.add_child(bez_registru)
	_kontrola(bez_registru.gather(Uzel.new()) == 0, "bez registru vrátí 0 a OHLÁSÍ to (žádná tichá nula)")

	print("\n[test] %d kontrol, %d chyb" % [pocet, chyby])
	quit(chyby)
	return true


var pocet := 0

func _kontrola(podminka: bool, popis: String) -> void:
	pocet += 1
	if podminka:
		print("  OK    %s" % popis)
	else:
		print("  CHYBA %s" % popis)
		chyby += 1
