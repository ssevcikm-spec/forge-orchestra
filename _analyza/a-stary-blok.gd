	# Drift iso_position: hráč smí volat izo projekci jen na světě (world),
	# ne na úrovni. Kontrola se zapne, až hráč dostane smluvní move().
	if player != null and player.has_method("move"):
		var player_zdroj := FileAccess.get_file_as_string("res://scripts/player.gd")
		_check(not player_zdroj.contains("level.iso_position")
			and not player_zdroj.contains("level.has_method(\"iso_position\")"),
			"player volá izo projekci přes world, ne přes level")
