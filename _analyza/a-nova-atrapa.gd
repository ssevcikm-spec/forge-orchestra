

class TestUrovenBezIzo:
	extends Node2D
	"""Atrapa úrovně, která izo projekci NEMÁ – a počítá, kdo se na ni ptal.

	Záměrně neimplementuje `iso_position`: `level.gd` ji taky nemá (je jen
	v `_retired/world.gd`). Kdyby se ji `move()` pokusil zavolat, spadne to
	v `move()` samém – a to je vidět (a je to nález, ne ticho).
	"""
	var izo_pokusu := 0
	var walk_dotazu := 0

	func ma_iso() -> bool:
		izo_pokusu += 1
		return false

	func is_walkable_at(_pos: Vector2) -> bool:
		walk_dotazu += 1
		return true
