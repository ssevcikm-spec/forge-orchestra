extends SceneTree
# Druhé, OPRAVENÉ měření (první běželo v _initialize, kdy ještě není strom →
# `get_tree()` vracelo null a měřilo se něco jiného, než co se děje ve hře).
# Tady se pracuje v _process, tedy v běžícím stromu – jako ve hře.

var _hotovo := false


func _process(_delta: float) -> bool:
	if _hotovo:
		return true
	_hotovo = true

	print("=== 0. Má Godot 4.7 vůbec to, co skripty volají? ===")
	var l := Label.new()
	var ma_margin := false
	var ma_offset := false
	for p in l.get_property_list():
		if p.name == "margin_left":
			ma_margin = true
		if p.name == "offset_left":
			ma_offset = true
	print("  Label.margin_left existuje: %s   (offset_left: %s)" % [ma_margin, ma_offset])
	var n := Node.new()
	print("  Node.has_property('hp') jde zavolat: %s" % _zkus(n, "has_property", "hp"))
	print("  Node.has_variable('x')  jde zavolat: %s" % _zkus(n, "has_variable", "x"))

	print("\n=== 1. save.gd — hráč ve skupině (jako ve hře), ostatní služby ne ===")
	var SaveSc = load("res://save.gd")
	var hrac := Node2D.new()  # Node2D, ne Node — jen Node2D má `position`
	hrac.name = "Player"
	hrac.add_to_group("player")
	hrac.position = Vector2(48, 96)
	root.add_child(hrac)
	var sv = SaveSc.new()
	root.add_child(sv)
	print("  instance v tree: %s" % str(sv.is_inside_tree()))
	var vysledek = sv.save()
	print("  save() vrátilo: %s" % str(vysledek))
	var f := FileAccess.open("user://save.cfg", FileAccess.READ)
	if f == null:
		print("  user://save.cfg NEEXISTUJE")
	else:
		print("  --- obsah user://save.cfg ---")
		print(f.get_as_text())
		print("  --- konec (uložily se atributy? skilly? zlato? stav světa?) ---")
	print("  load() vrátilo: %s" % str(sv.load()))

	print("\n=== 2. hud.gd — co se stane při instanci ve stromu ===")
	var HudSc = load("res://hud.gd")
	var hu = HudSc.new()
	root.add_child(hu)
	print("  _label po _ready(): %s" % ("vytvořen" if hu._label != null else "NULL (a přitom je přiřazen na řádku 17)"))
	print("  připojen do stromu: %s" % str(hu.get_child_count()))
	print("  odkazy: player=%s attributes=%s skills=%s economy=%s"
		% [hu._player, hu._attributes, hu._skills, hu._economy])
	if hu._label != null:
		print("  --- text pro hráče ---")
		print(hu._label.text)
		print("  --- konec ---")

	print("\n=== 3. Ruční volání update() (kdyby _ready() spadlo) ===")
	hu.update()
	print("  update() proběhlo bez pádu")

	print("\n=== 4. Jak se služby hledají JINDE v projektu (kontext) ===")
	print("  save.gd/hud.gd: get_first_node_in_group('attributes'|'skills'|'economy'|'world'|'player')")
	print("  mining.gd (sloučené #30): get_node_or_null('/root/Skills'), '/root/World'")
	print("  testy: main.component('Skills'|'Attributes'|'World'|'Hud')")
	print("  ve hře zaregistrované skupiny: player (player.gd:17), level/coin/npc (game.gd)")

	quit(0)
	return true


func _zkus(obj: Object, metoda: String, argument: String) -> String:
	if not obj.has_method(metoda):
		return "NE — metoda neexistuje"
	var r = obj.call(metoda, argument)
	return "ano (vrátilo %s)" % str(r)
