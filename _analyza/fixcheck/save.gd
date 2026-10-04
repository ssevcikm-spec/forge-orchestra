extends Node
# Ukládání a načtení stavu přes ConfigFile do user://save.cfg.
#
# ODKUD BERE KOMPONENTY (rozhodnuto 2. 10. 2026): z registru kostry —
# `game.gd` vystavuje `component(id) -> Node` (docs/ARCHITEKTURA.md:145).
# Původní verze je hledala ve skupinách "attributes"/"skills"/"economy"/"world",
# které v projektu NIKDO nezakládá. Následek (naměřeno 2. 10. 2026): `save()`
# zapsalo 35 B — jen pozici hráče — a přesto vrátilo `true`. Tichý úspěch nad
# neuloženým stavem je horší než chyba, protože se na něj někdo spolehne:
# když není co uložit, `save()` teď vrátí `false` a ohlásí to.
#
# CO SE UKLÁDÁ: atributy, dovednosti, zlato a pozice hráče — tedy to, co
# komponenty v `main` SKUTEČNĚ poskytují. Inventář a stav uzlů světa uložit
# nelze: `scripts/player.gd` inventář nemá (granule `entity.player` ho nedodala)
# a `scripts/world.gd` v repu není (smazán při izometrické migraci, commit
# c651368). Až je komponenty dostanou, patří sem — a musí se to ohlásit,
# ne tiše vynechat.

const SOUBOR := "user://save.cfg"
const POTREBNE := ["Attributes", "Skills", "Economy", "Player"]


func save() -> bool:
	var cfg := ConfigFile.new()
	var komponenty := {}
	var chybejici: Array = []
	for id in POTREBNE:
		komponenty[id] = _komponenta(id)
		if komponenty[id] == null:
			chybejici.append(id)
	if chybejici.size() == POTREBNE.size():
		push_error("save.gd: nad sebou nemám kostru s component(id) – neuložil jsem nic")
		return false
	if not chybejici.is_empty():
		push_warning("save.gd: chybí komponenty %s – ukládám jen to, co je" % str(chybejici))

	var atributy = komponenty["Attributes"]
	if atributy != null:
		cfg.set_value("attributes", "Str", atributy.Str)
		cfg.set_value("attributes", "Dex", atributy.Dex)
		cfg.set_value("attributes", "Int", atributy.Int)

	var skilly = komponenty["Skills"]
	if skilly != null:
		cfg.set_value("skills", "dovednosti", skilly.dovednosti)

	var ekonomika = komponenty["Economy"]
	var hrac = komponenty["Player"]
	if ekonomika != null and hrac != null:
		cfg.set_value("economy", "gold", ekonomika.gold(hrac))

	if hrac != null and "position" in hrac:
		cfg.set_value("player", "position", hrac.position)

	return cfg.save(SOUBOR) == OK


func load() -> bool:
	var cfg := ConfigFile.new()
	if cfg.load(SOUBOR) != OK:
		return false

	var pouzito := 0
	var atributy = _komponenta("Attributes")
	if atributy != null and cfg.has_section("attributes"):
		atributy.Str = cfg.get_value("attributes", "Str", atributy.Str)
		atributy.Dex = cfg.get_value("attributes", "Dex", atributy.Dex)
		atributy.Int = cfg.get_value("attributes", "Int", atributy.Int)
		pouzito += 1

	var skilly = _komponenta("Skills")
	if skilly != null and cfg.has_section_key("skills", "dovednosti"):
		skilly.dovednosti = cfg.get_value("skills", "dovednosti", skilly.dovednosti)
		pouzito += 1

	var ekonomika = _komponenta("Economy")
	if ekonomika != null and cfg.has_section_key("economy", "gold"):
		# economy.gd veřejný setter nemá (vlastní ho granule sim.economy),
		# proto se sahá na její stav přímo. Až přibude `set_gold()`, patří sem.
		ekonomika.set("_gold", int(cfg.get_value("economy", "gold", 0)))
		pouzito += 1

	var hrac = _komponenta("Player")
	if hrac != null and cfg.has_section_key("player", "position") and "position" in hrac:
		hrac.position = cfg.get_value("player", "position", hrac.position)
		pouzito += 1

	if pouzito == 0:
		push_error("save.gd: soubor uložený je, ale není kam stav vrátit (chybí komponenty)")
		return false
	return true


func _komponenta(id: String):
	"""Komponenta z registru kostry (rodič umí `component(id)`), jinak null."""
	var kostra := get_parent()
	if kostra != null and kostra.has_method("component"):
		return kostra.component(id)
	return null
