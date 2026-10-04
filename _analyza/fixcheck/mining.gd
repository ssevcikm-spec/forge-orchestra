extends Node
# Těžba a dřevorubectví — výtěžek podle skillu a obtížnosti suroviny.
#
# ODKUD BERE SLUŽBY (rozhodnuto 2. 10. 2026): z registru kostry —
# `game.gd` vystavuje `component(id) -> Node` (docs/ARCHITEKTURA.md:145).
# Původní verze sahala na `/root/Skills` a `/root/World`, tedy na autoloady,
# které v projektu NEJSOU (`project.godot` nemá ani jeden) a `scripts/world.gd`
# byl navíc smazán při izometrické migraci (c651368).
#
# Naměřeno 2. 10. 2026 (Godot 4.7.2): `gather()` spadlo hned na prvním uzlu —
# `Object.has()` v Godotu 4 NEEXISTUJE (je to Godot 3 API), takže se ani
# nedošlo na hledání skillu. Testy to nevidí: kontrolují jen
# `has_method("gather")`, ne že funkce něco udělá.
#
# Godot 4: vlastnost se ptá přes `"jmeno" in uzel`, ne `uzel.has("jmeno")`.

func gather(node: Node) -> int:
	var resource_id: String = ""
	var difficulty: int = 0
	var cell = null

	if node.has_method("get_resource_id"):
		resource_id = node.get_resource_id()
	elif "resource_id" in node:
		resource_id = node.resource_id
	else:
		push_error("mining.gd: uzel nemá 'resource_id'")
		return 0

	if node.has_method("get_difficulty"):
		difficulty = node.get_difficulty()
	elif "difficulty" in node:
		difficulty = node.difficulty
	else:
		push_error("mining.gd: uzel nemá 'difficulty'")
		return 0

	if node.has_method("get_cell"):
		cell = node.get_cell()
	elif "cell" in node:
		cell = node.cell

	var skill_name: String = "tezba"
	match resource_id:
		"iron_ore", "stone":
			skill_name = "tezba"
		"wood":
			skill_name = "drevorubectvi"

	var skilly = _komponenta("Skills")
	if skilly == null:
		push_error("mining.gd: komponenta Skills není v registru – nevím, jaký je skill")
		return 0

	var hodnota: int = skilly.hodnota(skill_name)
	var vynos: int = int(max(0, 1 + (hodnota - difficulty) / 10))

	skilly.add(skill_name, 1)

	var svet = _komponenta("World")
	if svet != null and svet.has_method("gather"):
		svet.gather(cell)

	return vynos


func _komponenta(id: String):
	"""Komponenta z registru kostry (rodič umí `component(id)`), jinak null."""
	var kostra := get_parent()
	if kostra != null and kostra.has_method("component"):
		return kostra.component(id)
	return null
