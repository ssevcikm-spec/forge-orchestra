

class TestBojAtributy:
	extends Node
	"""Atributy pro `combat.resolve()` — SCHVÁLNĚ BEZ `hodnota()`.

	Přesně tak vypadá cesta, kterou atributy čtou ostatní testy: `TestAtributy`
	v tomhle souboru `hodnota()` nemá a vystavuje `Str`/`Dex` rovnou.
	Kdyby si combat poradil jen s `hodnota()`, tenhle test to odhalí.
	"""
	var Str := 10
	var Dex := 10


class TestBojSkilly:
	extends Node
	"""Dovednosti pro `combat.resolve()` — taky bez `hodnota()` (viz výš)."""
	var boj_na_blizko := 0


class TestBojovnik:
	extends Node2D
	"""Útočník i obránce pro `combat.resolve()`.

	Vlastnosti musí být DEKLAROVANÉ ve skriptu — do uzlu z `Node2D.new()` se
	vlastnost přidat nedá (CONVENTIONS.md §1b) a `combat.gd` se na ně ptá
	přes `"jmeno" in uzel`.
	"""
	var vybrana_zbran = null
	var zbran = null
	var armor_rating := 0


class TestZbran:
	extends Node
	"""Zbraň v ruce: jediné, co z ní `combat.resolve()` čte, je `damage`."""
	var damage := 0
