extends SceneTree
# Měření: co dělají skripty z PR #28 (save.gd) a #29 (hud.gd), když je opravdu
# načte Godot — místo aby se o nich jen četlo.
#
# Kontext, který se tím ověřuje: v projektu hry NENÍ žádný autoload a žádný
# uzel se nepřidává do skupin "attributes", "skills", "economy", "world"
# (měřeno greppem: `add_to_group` je jen u "player"/"level"/"coin"/"npc").
# Oba skripty si přitom služby hledají PŘESNĚ přes tyhle skupiny.

func _initialize() -> void:
	print("=== 1. Načtou se skripty vůbec? (parse) ===")
	var chyby := 0
	for dvojice in [["save.gd", "res://save.gd"], ["hud.gd", "res://hud.gd"], ["skills_main.gd (kontrolní vzorek)", "res://skills_main.gd"]]:
		var sc = load(dvojice[1])
		var stav = "OK" if sc != null else "NULL — soubor se NENAČETL (parse chyba)"
		print("  %-34s %s" % [dvojice[0], stav])
		if sc == null:
			chyby += 1

	print("\n=== 2. save.gd: co udělá save(), když ve scéně nejsou skupiny? ===")
	var SaveSc = load("res://save.gd")
	if SaveSc == null:
		print("  save.gd se nenačetl — dál nelze měřit")
	else:
		var sv = SaveSc.new()
		root.add_child(sv)
		print("  instance v tree: %s" % str(sv.is_inside_tree()))
		var vysledek = sv.save()
		print("  save() vrátilo: %s   <-- a co se přitom uložilo?" % str(vysledek))
		var f := FileAccess.open("user://save.cfg", FileAccess.READ)
		if f == null:
			print("  user://save.cfg NEEXISTUJE")
		else:
			var obsah := f.get_as_text()
			print("  --- obsah user://save.cfg (%d znaků) ---" % obsah.length())
			print(obsah if obsah.strip_edges() != "" else "  (PRÁZDNÝ SOUBOR)")
			print("  --- konec souboru ---")
		print("  load() vrátilo: %s" % str(sv.load()))

		print("\n=== 3. save.gd se ČLOVĚKEM založenou skupinou 'player' (jako ve hře) ===")
		var hrac := Node.new()
		hrac.name = "Player"
		hrac.add_to_group("player")
		root.add_child(hrac)
		var sv2 = SaveSc.new()
		root.add_child(sv2)
		print("  save() s hráčem ve skupině → %s" % str(sv2.save()))
		var f2 := FileAccess.open("user://save.cfg", FileAccess.READ)
		if f2 != null:
			print("  --- obsah ---")
			print(f2.get_as_text())
			print("  --- konec ---")

	print("\n=== 4. hud.gd: co ukáže update(), když služby nejsou? ===")
	var HudSc = load("res://hud.gd")
	if HudSc == null:
		print("  hud.gd se nenačetl — dál nelze měřit")
	else:
		var hu = HudSc.new()
		root.add_child(hu)
		print("  label existuje: %s" % str(hu._label != null))
		if hu._label != null:
			print("  --- text, který by hráč viděl ---")
			print(hu._label.text)
			print("  --- konec textu ---")
		print("  odkazy: player=%s attributes=%s skills=%s economy=%s"
			% [str(hu._player), str(hu._attributes), str(hu._skills), str(hu._economy)])

	print("\n=== 5. Bere projekt vůbec v úvahu skupiny, které skripty hledají? ===")
	for g in ["attributes", "skills", "economy", "world", "player"]:
		print("  skupina '%-11s' má %d uzlů" % [g, get_nodes_in_group(g).size()])

	print("\nVÝSLEDEK: chyb při načítání skriptů = %d" % chyby)
	quit(chyby)
