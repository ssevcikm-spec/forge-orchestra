	var combat_sc = load("res://scripts/combat.gd")
	if combat_sc != null:
		var cb = _instantiate("boj", "res://scripts/combat.gd")
		_check(cb.has_method("resolve"), "combat.gd poskytuje resolve(att, def)")
		_zavri(cb)
