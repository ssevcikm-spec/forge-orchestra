	# Drift iso_position: hráč NESMÍ brát izo projekci z úrovně.
	#
	# DŘÍV TU BYLA STATICKÁ KONTROLA, KTERÁ MĚŘILA PŘÍTOMNOST TEXTU (naměřeno
	# 2. 10. 2026): hledala `level.iso_position` a `level.has_method("iso_position")`
	# v CELÉM souboru player.gd. Jenže `player.gd:40` obsahuje právě to druhé –
	# v `_physics_process`, který prompt granule `entity.player.api`
	# (roadmap.json:90) PŘIKAZUJE ZACHOVAT. Kontrola byla nastražená: zakazovala
	# legitimní kód a spustila by se přesně ve chvíli, kdy granule dodá `move()`.
	#
	# Vad bylo víc a každá se měří jinak:
	#   * `level.gd` metodu `iso_position` VŮBEC NEMÁ (je jen v _retired/world.gd),
	#     takže větev v `_physics_process` je mrtvá a test o izometrii netvrdil nic;
	#   * kontrola byla podmíněná `has_method("move")`, takže se dnes tiše
	#     přeskakovala (a `move()` v repu není).
	#
	# Nová kontrola kód ZAVOLÁ a změří, na kom se ptal (AGENTS.md: „brána, která
	# se ptá na přítomnost, neměří chování").
	if player != null:
		var player_skript = player.get_script()
		_check(player_skript != null, "player.gd jde načíst (dřív se nenačtený přeskočil)")
		if player_skript != null and player.has_method("move"):
			var uroven_spy := TestUrovenBezIzo.new()
			uroven_spy.name = "UrovenBezIzo"
			player.level = uroven_spy
			player.move(Vector2(1, 0))
			_check(uroven_spy.izo_pokusu == 0,
				"player.move() nebere izo projekci z úrovně (pokusů: %d)"
				% uroven_spy.izo_pokusu)
			uroven_spy.free()
		else:
			# Není to tichý přeskok: kontrola, která se nemá čeho chytit, to řekne.
			print("[test]      player: `move()` v player.gd není – kontrola izo "
				+ "projekce se NEMĚŘÍ (dodá ji granule entity.player.api)")
