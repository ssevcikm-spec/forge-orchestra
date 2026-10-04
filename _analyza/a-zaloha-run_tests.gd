extends SceneTree
## Testy projektu – spouští se bez okna i bez grafické karty:
##
##     godot --headless --path <projekt> --script res://tests/run_tests.gd
##
## Když všechny kontroly projdou, skončí s kódem 0. Každé selhání kód zvýší,
## takže se výsledek dá použít v CI i v ručním ověření.
##
## POZOR – HLÍDAČ: testy musí skončit VŽDY. Když se nepodaří načíst skript hry
## (typicky chyba v kódu od agenta), GDScript přeruší běh _run() a na quit()
## se nikdy nedostane – proces pak visí, dokud ho nezabije CI. Naměřeno: 14
## minut čekání v GitHub Actions místo okamžitého selhání. Proto běží hlídač,
## který po HARD_LIMIT_SECONDS skončí sám (a řekne, že šlo o zaseknutí).
##
## Žebříček limitů (musí na sebe navazovat): hlídač 90 s < vnější `timeout 150`
## v CI < timeout kroku 3 min. Když zamrzne samotný engine (nekonečná smyčka),
## hlídač se nedostane ke slovu – proto je tam i ten vnější.

const HARD_LIMIT_SECONDS := 90.0

var failures := 0
var checks := 0
var _deadline := 0.0
var _done := false


func _initialize() -> void:
	_deadline = Time.get_ticks_msec() / 1000.0 + HARD_LIMIT_SECONDS
	_run()


func _process(_delta: float) -> bool:
	"""Hlídač: kdyby se _run() zasekl nebo přerušil, stejně se skončí."""
	if _done:
		return true
	if Time.get_ticks_msec() / 1000.0 > _deadline:
		print("[test] FAIL překročen tvrdý limit %.0f s – testy se zasekly."
			% HARD_LIMIT_SECONDS)
		print("[test]      Nejpravděpodobnější příčina: skript hry se nepodařilo "
			+ "načíst (chyba v kódu), takže se _run() přerušil.")
		failures += 1
		_finish()
	return false


func _check(ok: bool, label: String) -> void:
	checks += 1
	if ok:
		print("[test] OK   ", label)
	else:
		failures += 1
		print("[test] FAIL ", label)


func _run() -> void:
	await process_frame

	var packed := load("res://main.tscn")
	_check(packed != null, "main.tscn jde načíst")
	if packed == null:
		_finish()
		return

	var main = packed.instantiate()
	root.add_child(main)
	await process_frame
	await process_frame

	# Když se skript hry vůbec nenačetl (parse error), nemá cenu pokračovat:
	# volání na null by přerušilo tenhle běh a testy by nikdy neskončily.
	var main_script = main.get_script()
	_check(main_script != null, "skript hry jde načíst (žádná chyba v kódu)")
	if main_script == null:
		_finish()
		return

	var player = main.get_node_or_null("Player")
	_check(player != null, "scéna vytvořila uzel Player")

	var expected := 5
	var consts = main_script.get_script_constant_map()
	if consts.has("COIN_COUNT"):
		expected = consts["COIN_COUNT"]
	# S úrovní určuje počet mincí mapa, ne konstanta.
	var ct = main.get("coin_total")
	if ct != null:
		expected = int(ct)
	var coins := get_nodes_in_group("coin")
	_check(coins.size() == expected,
		"počet mincí odpovídá očekávání (%d, nalezeno %d)" % [expected, coins.size()])

	var hud = main.get_node_or_null("Hud")
	_check(hud != null, "HUD s výsledkem existuje")
	if hud != null:
		_check(String(hud.text).contains("0"), "HUD ukazuje počáteční skóre: '%s'" % hud.text)

	if player != null and coins.size() > 0:
		var before: int = main.score
		main._on_coin_touched(player, coins[0])
		await process_frame
		_check(main.score == before + 1,
			"sebrání mince zvýší skóre (%d -> %d)" % [before, main.score])

	# Všechno, co je v projektu k dispozici, musí jít načíst.
	var missing := 0
	var loaded := 0
	for dir_path in ["res://assets/sprites", "res://assets/audio/sfx",
					 "res://assets/audio/music", "res://assets/tiles", "res://assets/ui",
					 "res://assets/levels"]:
		var d := DirAccess.open(dir_path)
		if d == null:
			continue
		for f in d.get_files():
			if f.ends_with(".import") or f.begins_with("."):
				continue
			var res_path: String = str(dir_path) + "/" + str(f)
			if ResourceLoader.exists(res_path) and load(res_path) != null:
				loaded += 1
			else:
				missing += 1
				print("[test]      nelze načíst: ", res_path)
	_check(missing == 0, "všechny assety jdou načíst (%d OK, %d chybí)" % [loaded, missing])

	# Animace: co je v assets/animations.json, se musí dát načíst jako SpriteFrames.
	# Tohle je zároveň ověření, že ručně zapisovaný formát .tres sedí.
	var anim_file := "res://assets/animations.json"
	if FileAccess.file_exists(anim_file):
		var parsed = JSON.parse_string(FileAccess.get_file_as_string(anim_file))
		var anims: Array = []
		if parsed is Dictionary:
			anims = parsed.get("animations", [])
		_check(anims.size() > 0, "animations.json obsahuje %d animací" % anims.size())
		for a in anims:
			var res: String = str(a.get("sprite_frames_resource", ""))
			_check(ResourceLoader.exists(res), "resource animace existuje: %s" % res)
			if not ResourceLoader.exists(res):
				continue
			var res_frames = load(res)
			_check(res_frames is SpriteFrames, "načte se jako SpriteFrames: %s" % res)
			if res_frames is SpriteFrames:
				var nm: String = str(a.get("name", ""))
				_check(res_frames.has_animation(nm), "animace '%s' je v resource" % nm)
				if res_frames.has_animation(nm):
					var n: int = res_frames.get_frame_count(nm)
					var expected_frames: int = (a.get("frames", []) as Array).size()
					_check(n == expected_frames,
						"počet framů animace '%s' sedí (%d)" % [nm, n])

	# ------------------------------------------------------------- úroveň ----
	# Mapa se testuje vlastnostmi, ne vzhledem: musí se z ní dát projít všude,
	# mince musí ležet na průchozích políčkách a zeď musí hráče zastavit.
	if FileAccess.file_exists("res://assets/levels/main.json"):
		_check(true, "úroveň main.json je v projektu")
		var lvl = main.get_node_or_null("Level")
		_check(lvl != null, "mapa je postavená ve scéně")
		if lvl != null:
			_check(lvl.is_walkable_cell(lvl.spawn_cell.x, lvl.spawn_cell.y),
				"spawn je na průchozím políčku %s" % str(lvl.spawn_cell))
			_check(lvl.reachable_count() == lvl.walkable_count(),
				"z každého políčka se dá dojít na spawn (%d z %d)"
				% [lvl.reachable_count(), lvl.walkable_count()])
			_check(lvl.get_child_count() == lvl.width * lvl.height,
				"mapa má dlaždici pro každé políčko (%d)" % lvl.get_child_count())

			# Vrstvy: mapa musí být nad pozadím (jinak ji celoobrazovková tráva
			# schová) a hráč nad mapou. Testy dřív prošly, i když mapa nebyla
			# vidět – dlaždice ve scéně byly, jen se kreslily pod pozadím.
			var bg_node = main.get_node_or_null("Background")
			var bg_z: int = bg_node.z_index if bg_node != null else -99
			if bg_node != null:
				_check(lvl.z_index > bg_z,
					"mapa se kreslí nad pozadím (mapa %d, pozadí %d)" % [lvl.z_index, bg_z])
			if player != null:
				_check(player.z_index > lvl.z_index + 1,
					"hráč se kreslí nad mapou (hráč %d, zeď %d)"
					% [player.z_index, lvl.z_index + 1])

			var bad_markers := 0
			for kind in ["coin", "exit", "spawn"]:
				for pos in lvl.marker_positions(kind):
					if not lvl.is_walkable_at(pos):
						bad_markers += 1
			_check(bad_markers == 0, "všechny značky leží na průchozích políčkách")

			if player != null:
				_check(lvl.is_walkable_at(player.position),
					"hráč startuje na průchozím políčku %s" % str(player.position))

				# Najdi zeď vedle průchozího políčka a zkus do ní vstoupit.
				var from_cell := Vector2i(-1, -1)
				var wall_cell := Vector2i(-1, -1)
				for y in lvl.height:
					for x in lvl.width:
						if not lvl.is_walkable_cell(x, y):
							continue
						for d in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
							var n: Vector2i = Vector2i(x, y) + d
							if n.x > 0 and n.y > 0 and n.x < lvl.width - 1 and n.y < lvl.height - 1 \
									and not lvl.is_walkable_cell(n.x, n.y):
								from_cell = Vector2i(x, y)
								wall_cell = n
								break
						if wall_cell.x >= 0:
							break
					if wall_cell.x >= 0:
						break
				_check(wall_cell.x >= 0, "našla se zeď sousedící s chodbou")
				if wall_cell.x >= 0:
					var back: Vector2 = player.position
					player.position = lvl.cell_center(from_cell.x, from_cell.y)
					var moved: Vector2 = player._step(lvl.cell_center(wall_cell.x, wall_cell.y))
					_check(lvl.cell_at(moved) != wall_cell,
						"hráč se nedostane do zdi %s (skončil v %s)"
						% [str(wall_cell), str(lvl.cell_at(moved))])
					_check(lvl.is_walkable_at(moved),
						"i po nárazu do zdi zůstane hráč na průchozím políčku")
					player.position = back

	# ---------------------------------------------------------- dlaždice ----
	# Dlaždice a UI musí být nejen na disku, ale i VE SCÉNĚ.
	# Tohle je regresní test na konkrétní vadu: pozadí se sice načetlo, ale mělo
	# nulovou velikost, takže se vůbec nevykreslilo (odhalil to až vision model
	# nad snímkem hry). Test to teď pozná sám.
	if ResourceLoader.exists("res://assets/tiles/grass.png"):
		var bg = main.get_node_or_null("Background")
		_check(bg != null, "dlaždicové pozadí je ve scéně")
		if bg != null:
			_check(bg.size.x > 0.0 and bg.size.y > 0.0,
				"pozadí má nenulovou velikost (%s)" % str(bg.size))

	if ResourceLoader.exists("res://assets/ui/panel.png"):
		_check(main.get_node_or_null("HudPanel") != null, "UI panel je ve scéně")

	# Hudba: soubor na disku nestačí, musí hrát a mít zapnutou smyčku.
	if DirAccess.open("res://assets/audio/music") != null:
		var music = main.get_node_or_null("Music")
		_check(music != null, "hudba je ve scéně")
		if music != null and music.stream is AudioStreamWAV:
			_check(music.stream.loop_mode == AudioStreamWAV.LOOP_FORWARD,
				"hudba má zapnutou smyčku")
			# Konec smyčky musí odpovídat CELÉ délce skladby, jinak se hudba
			# uřízne (přesně to se stalo, když se počet vzorků počítal z bajtů).
			var expected_loop_end: int = int(music.stream.get_length() * music.stream.mix_rate)
			_check(abs(music.stream.loop_end - expected_loop_end) <= 2,
				"konec smyčky sedí s délkou skladby (%d vs %d)" % [music.stream.loop_end, expected_loop_end])

	# ------------------------------------------------------------ entity ----
	# Když hra nějaké entity vytváří, musí být OPRAVDU ve scéně. Tahle kontrola
	# je tady proto, že chyba uvnitř funkce _make_* (třeba přiřazení vlastnosti,
	# kterou Area2D nemá) funkci přeruší, uzel se vůbec nepřidá – a testy to
	# nezjistí, protože se ptají jen na mince. Přesně takhle přišla hra v PR #9
	# o nepřátele a CI přitom hlásilo úspěch.
	var enemies := get_nodes_in_group("enemy")
	if main.has_method("_make_enemy"):
		_check(enemies.size() > 0, "hra vytvořila nepřátele (nalezeno %d)" % enemies.size())
	if main.has_method("_make_chest"):
		_check(get_nodes_in_group("chest").size() > 0, "hra vytvořila truhlu")

	if enemies.size() > 0:
		var before: Array = []
		for e in enemies:
			before.append(e.position)
		# POZOR: v headless režimu se snímky vykreslují maximální rychlostí,
		# takže „30 snímků" je jen pár milisekund a nepřítel se posune
		# o setiny pixelu (naměřeno 0,0 px). Měří se proto SKUTEČNÝ čas.
		var t0 := Time.get_ticks_msec()
		while Time.get_ticks_msec() - t0 < 400:
			await process_frame
		var elapsed := float(Time.get_ticks_msec() - t0) / 1000.0
		var moved := 0.0
		for i in enemies.size():
			moved += before[i].distance_to(enemies[i].position)
		_check(moved > 0.5,
			"nepřátelé se hýbou (celkem %.1f px za %.2f s)" % [moved, elapsed])

		var lvl_node = main.get_node_or_null("Level")
		if lvl_node != null:
			var mimo := 0
			for e in enemies:
				if not lvl_node.is_walkable_at(e.position):
					mimo += 1
			_check(mimo == 0, "nepřátelé zůstávají na průchozích políčkách (%d mimo)" % mimo)

	# -------------------------------------------------- volitelné funkce ----
	# Testy, které se samy zapnou, až hra danou funkci dostane. Rozhoduje se
	# podle zdrojového textu skriptu: dokud v něm funkce není, kontrola se
	# přeskočí (šablona je bez nich); jakmile ji agent přidá, začne platit.
	# Důvod: PR #9 prošel se zeleným CI, a přitom se část scény vůbec nevytvořila.
	var zdroj := FileAccess.get_file_as_string("res://scripts/game.gd")

	if zdroj.contains("Minimap"):
		var mini = main.get_node_or_null("Minimap")
		_check(mini != null, "miniatura mapy je ve scéně")
		if mini != null:
			# „Miniatura" musí být opravdu malá a v rohu. Test na pouhou
			# nenulovou velikost nestačil: TextureRect má výchozí minimální
			# velikost rovnou textuře, takže se nastavených 120×64 tiše zahodilo
			# a miniatura (480×256) zakryla celou obrazovku.
			_check(mini.size.x > 0.0 and mini.size.y > 0.0,
				"miniatura má nenulovou velikost (%s)" % str(mini.size))
			_check(mini.size.x <= 240.0 and mini.size.y <= 140.0,
				"miniatura je malá, ne přes celou obrazovku (%s)" % str(mini.size))
			var vp_rozmer := get_root().get_visible_rect().size
			_check(mini.position.x > vp_rozmer.x / 2.0 and mini.position.y > vp_rozmer.y / 2.0,
				"miniatura je v pravém dolním rohu (%s)" % str(mini.position))

	if zdroj.contains("WinLabel"):
		var win = main.get_node_or_null("WinLabel")
		_check(win != null, "výherní hlášení je ve scéně")
		if win != null:
			_check(not win.visible, "výherní hlášení je na začátku skryté")

	if zdroj.contains("_spin_coins"):
		var mince := get_nodes_in_group("coin")
		if mince.size() > 0:
			var sirky: Array = []
			for c in mince:
				sirky.append(c.scale.x)
			var t_spin := Time.get_ticks_msec()
			while Time.get_ticks_msec() - t_spin < 300:
				await process_frame
			var zmena := 0.0
			for i in mince.size():
				zmena += abs(sirky[i] - mince[i].scale.x)
			_check(zmena > 0.01, "mince se otáčejí (změna šířky %.3f)" % zmena)

	# -------------------------------------------- vlastnosti, ne jen uzly ----
	# U každé funkce od agentů se testuje i CHOVÁNÍ, ne jen to, že uzel existuje.
	# Důvod: uzel může existovat a přesto nic nedělat (u miniatury se zase
	# nastavila jiná velikost, než jaká se požadovala).

	if main.get("lives") != null:
		_check(String(hud.text).contains("Životy"),
			"HUD ukazuje životy: '%s'" % hud.text)
		if enemies.size() > 0:
			var zivoty_pred: int = int(main.lives)
			main._on_enemy_touched(player, enemies[0])
			await process_frame
			_check(int(main.lives) == zivoty_pred - 1,
				"dotek nepřítele ubere život (%d -> %d)" % [zivoty_pred, int(main.lives)])

	if main.has_method("_save_best"):
		var puvodni_best: int = int(main.best)
		main.best = 12345
		main._save_best()
		var cfg := ConfigFile.new()
		var chyba: int = cfg.load("user://best.cfg")
		_check(chyba == OK and int(cfg.get_value("hra", "skore", -1)) == 12345,
			"nejlepší skóre se ukládá do user://best.cfg (chyba %d)" % chyba)
		main.best = puvodni_best
		main._save_best()

	if zdroj.contains("MinimapDot"):
		var mini_uzel = main.get_node_or_null("Minimap")
		var tecka = mini_uzel.get_node_or_null("MinimapDot") if mini_uzel != null else null
		_check(tecka != null, "tečka hráče je na miniatuře mapy")
		if tecka != null and player != null:
			var pozice_pred: Vector2 = tecka.position
			player.position += Vector2(40, 20)
			await process_frame
			await process_frame
			_check(tecka.position != pozice_pred,
				"tečka se posune s hráčem (%s -> %s)" % [str(pozice_pred), str(tecka.position)])
			player.position -= Vector2(40, 20)

	var hudba = main.get_node_or_null("Music")
	if hudba != null and zdroj.contains("stream_paused"):
		var pauza_pred: bool = hudba.stream_paused
		var klavesa := InputEventKey.new()
		klavesa.keycode = KEY_M
		klavesa.pressed = true
		main._input(klavesa)
		await process_frame
		_check(hudba.stream_paused != pauza_pred, "klávesa M vypne/zapne hudbu")

	var vyhra = main.get_node_or_null("WinLabel")
	var truhly := get_nodes_in_group("chest")
	if vyhra != null and truhly.size() > 0 and player != null:
		# Truhla má DVA možné významy a test je bere oba: buď rovnou vyhraje
		# (původní chování), nebo odemkne/posune na další úroveň (jak to navrhl
		# plán „Pokladnice Stínů"). Dřív tu bylo tvrzené „ukáže výherní hlášení",
		# jenže tím se změna, kterou plán chtěl, hlásila jako rozbitá.
		var index_pred_truhla = main.get("aktualni_level_index")
		main._on_chest_touched(player, truhly[0])
		await process_frame
		var posunul_truhla: bool = (index_pred_truhla != null
			and int(main.aktualni_level_index) != int(index_pred_truhla))
		_check(vyhra.visible or posunul_truhla,
			"truhla něco udělá: výherní hlášení, nebo posun dál (výhra %s, posun %s)"
			% [str(vyhra.visible), str(posunul_truhla)])
		if vyhra.visible:
			# Pozor: tenhle skript JE SceneTree, takže se pauza čte přímo z `paused`
			# (get_tree() na sobě samém neexistuje – přesně na tom spadl parse).
			_check(paused, "když hra vyhraje, pauzne se")
			paused = false  # aby zbytek testů mohl běžet

	# -------------------------------------------------- všechny úrovně ----
	# Hra může mít víc úrovní (postup úrovněmi) a musí umět načíst kteroukoli.
	# Kontroluje se každý .json v assets/levels: jde načíst a je celý průchodný.
	# Test se sám rozšíří, když přibude další úroveň.
	var lvls := DirAccess.open("res://assets/levels")
	if lvls != null:
		var skript_levelu = load("res://scripts/level.gd")
		if skript_levelu != null:
			for f in lvls.get_files():
				if not f.ends_with(".json") or f == "manifest.json":
					continue
				var lvl := Node2D.new()
				lvl.set_script(skript_levelu)
				var nacteno: bool = lvl.load_file("res://assets/levels/%s" % f)
				_check(nacteno, "úroveň %s jde načíst" % f)
				if nacteno:
					_check(lvl.reachable_count() == lvl.walkable_count(),
						"úroveň %s je celá průchodná (%d z %d)"
						% [f, lvl.reachable_count(), lvl.walkable_count()])
				lvl.free()

	# -------------------------------------------------- postup úrovněmi ----
	# Když hra umí víc úrovní, musí umět přepnout na další – a ta musí být
	# průchodná. Test se zapne sám, až funkce v kódu je (dřív ne).
	if main.get("aktualni_level_index") != null:
		# Nejdřív se stav NAROVNA: předchozí test s truhlou mohl úroveň posunout
		# (přesně to dělá odemčení východu mincemi), takže by tenhle blok padal
		# na „hra začíná na první úrovni (index 1)" – což nebyla chyba hry, ale
		# závislost testů na pořadí. Testy musí být nezávislé.
		main.aktualni_level_index = 0
		main._add_level()
		await process_frame
		_check(int(main.aktualni_level_index) == 0,
			"hra začíná na první úrovni (index %d)" % int(main.aktualni_level_index))
		var prvni_lvl = main.get_node_or_null("Level")
		_check(prvni_lvl != null and str(prvni_lvl.source).ends_with("/main.json"),
			"první úroveň se načetla z main.json (%s)"
			% (prvni_lvl.source if prvni_lvl != null else "?"))
		main.aktualni_level_index = 1
		main._add_level()
		await process_frame
		var druha_lvl = main.get_node_or_null("Level")
		_check(druha_lvl != null and str(druha_lvl.source).ends_with("/level_2.json"),
			"po přepnutí na index 1 se načte level_2.json (%s)"
			% (druha_lvl.source if druha_lvl != null else "?"))
		if druha_lvl != null:
			_check(druha_lvl.reachable_count() == druha_lvl.walkable_count(),
				"i druhá úroveň je celá průchodná (%d z %d)"
				% [druha_lvl.reachable_count(), druha_lvl.walkable_count()])
		# zpět na první úroveň, aby zbytek testů pracoval s původním stavem
		main.aktualni_level_index = 0
		main._add_level()
		await process_frame

	# -------------------------------------------------- herní smyčka ----
	# Doteď se testovaly jednotlivé funkce. Tohle je poprvé, co se ptáme na
	# CELEK: dá se hra vůbec dohrát? Nasbírat mince → dostat se k východu →
	# postoupit dál (nebo vyhrát). Test je záměrně shovívavý k tomu, jak je
	# odemčení udělané: projde, když se po truhle postoupí na další úroveň,
	# i když se rovnou vyhraje.
	if player != null and main.get("aktualni_level_index") != null:
		var mince_hry := get_nodes_in_group("coin")
		var pocet_minci := mince_hry.size()
		var skore_pred_hry: int = int(main.score)
		var sebrano := 0
		for c in mince_hry:
			if is_instance_valid(c):
				main._on_coin_touched(player, c)
				await process_frame
				sebrano += 1
		# Skóre se bere jako PŘÍRŮSTEK – jeden coin už mohl sebrat dřívější test.
		_check(sebrano > 0 and int(main.score) == skore_pred_hry + sebrano,
			"hráč posbíral všechny mince v úrovni (%d, skóre %d → %d)"
			% [sebrano, skore_pred_hry, main.score])

		var truhly_hry := get_nodes_in_group("chest")
		if truhly_hry.size() > 0:
			var index_pred: int = int(main.aktualni_level_index)
			var skore_pred: int = int(main.score)
			main._on_chest_touched(player, truhly_hry[0])
			await process_frame
			var posunul: bool = int(main.aktualni_level_index) > index_pred
			var vyhra_label = main.get_node_or_null("WinLabel")
			var vyhral: bool = vyhra_label != null and vyhra_label.visible
			_check(posunul or vyhral,
				"po truhle se postoupí dál nebo se vyhraje (index %d → %d, výhra %s)"
				% [index_pred, int(main.aktualni_level_index), str(vyhral)])
			paused = false

	# -------------------------------------------------- restart hry ----
	# Restart musí uvést hru do STARTU, ne jen schovat hlášení: skóre na nulu,
	# plné životy, první úroveň, hráč na spawnu – a hlavně se to musí projevit
	# v HUD (jinak obrazovka dál ukazuje staré skóre).
	if main.has_method("_restart_hry"):
		main.score = 7
		main.lives = 1
		if main.get("aktualni_level_index") != null:
			main.aktualni_level_index = 1
			main._add_level()
			await process_frame
		main._restart_hry()
		await process_frame
		_check(int(main.score) == 0, "restart vynuluje skóre (%d)" % int(main.score))
		_check(int(main.lives) == 3, "restart vrátí tři životy (%d)" % int(main.lives))
		if main.get("aktualni_level_index") != null:
			_check(int(main.aktualni_level_index) == 0,
				"restart vrátí na první úroveň (index %d)" % int(main.aktualni_level_index))
		if hud != null:
			_check(String(hud.text).contains("0 /"),
				"HUD po restartu ukazuje nulu: '%s'" % hud.text)
		var lvl_po = main.get_node_or_null("Level")
		if lvl_po != null and player != null:
			var spawn_bod: Vector2 = lvl_po.cell_center(lvl_po.spawn_cell.x, lvl_po.spawn_cell.y)
			_check(player.position.distance_to(spawn_bod) < 24.0,
				"hráč je po restartu na spawnu (%.0f px od něj)"
				% player.position.distance_to(spawn_bod))

	# --------------------------------------------------- UO (ARCHITEKTURA) ----
	# Failing-first testy granulí z docs/ARCHITEKTURA.md. Každá kontrola se
	# zapne sama, až soubor granule v projektu JE – dokud granule neexistuje,
	# přeskočí se a CI zůstává zelené i uprostřed vlny. Kontroly se drží
	# smluvních `provides` (nikdy soukromých polí).

	var attrs_sc = load("res://scripts/attributes.gd")
	if attrs_sc != null:
		var attrs = _instantiate("atributy", "res://scripts/attributes.gd")
		if attrs.has_method("get") and attrs.has_method("derived"):
			_check(int(attrs.get("Str")) == 10 and int(attrs.get("Dex")) == 10
				and int(attrs.get("Int")) == 10,
				"atributy začínají na 10 (%s/%s/%s)"
				% [str(attrs.get("Str")), str(attrs.get("Dex")), str(attrs.get("Int"))])
			var odvozene = attrs.derived()
			_check(odvozene is Dictionary and odvozene.has("damage") and odvozene.has("hit_chance")
				and odvozene.has("attack_speed") and odvozene.has("mana") and odvozene.has("carry"),
				"derived() vrací damage, hit_chance, attack_speed, mana i carry")
		_zavri(attrs)

	var skills_sc = load("res://scripts/skills.gd")
	if skills_sc != null:
		var sk = _instantiate("skilly", "res://scripts/skills.gd")
		if sk.has_method("get") and sk.has_method("add"):
			# POZOR – `get()` SE DVĚMA ARGUMENTY ZABIJE CELÝ BĚH TESTŮ.
			# Naměřeno 30. 9. 2026 (běh #128, granule core.skills): skript si
			# definoval vlastní `get(skill: String) -> int`, čímž přebil
			# `Object.get()`. Volání `sk.get("tezba", 0)` (s defaultem) vyhodí
			# fatální `Invalid call to function 'get' … Expected 1 argument(s)`,
			# GDScript přeruší _run() – a protože se nikdy nedojde na _finish(),
			# testy visí do tvrdého limitu 90 s (reprodukováno: 90.7 s, 26
			# kontrol, 1 selhání). V logu je pak jen „testy se zasekly".
			# Volá se proto s JEDNÍM argumentem, přesně jako to dělá smlouva.
			var t0 = sk.get("tezba")
			var k0 = sk.get("kovarstvi")
			if t0 == null or k0 == null:
				# Vlastní get() na neznámý klíč vrátí null – stejně jako když
				# skript get() nemá a odpovídá enginový Object.get(). Kontrola
				# se přeskočí, místo aby spadla na `int(null)`.
				print("[test]      skilly: get() nevrátil hodnoty pro 'tezba'/" +
					"'kovarstvi' – kontrola začátků na 0 se přeskakuje")
			else:
				_check(int(t0) == 0 and int(k0) == 0, "skilly začínají na 0")
				sk.add("tezba", 150)
				_check(int(sk.get("tezba")) == 100,
					"skill je shora omezený na 100 (má %s)" % str(sk.get("tezba")))
				sk.add("tezba", -500)
				_check(int(sk.get("tezba")) == 0,
					"skill neklesne pod 0 (má %s)" % str(sk.get("tezba")))
		_zavri(sk)

	# ---------------------------------------------------------- izometrie ----
	# DŘÍV TU BYL TEST `world.gd`, KTERÝ SE OVĚŘOVAL SÁM PROTI SOBĚ:
	# `w.cell_at(w.iso_position(2,3))` projde vždy, protože obě funkce používají
	# stejnou konstantu – i kdyby byl výsledek nesmyslný. Navíc `world.gd` nebyl
	# v projektu NIKDE instancovaný (jen tady), takže test hlídal mrtvý kód a
	# tvrdil o něm, že je v pořádku.
	#
	# Izometrie se teď testuje tam, kde skutečně je – na `level.gd`, který mapu
	# kreslí. Ověřuje se VLASTNOST projekce (2:1), ne shoda funkce se sebou samou.
	var level_sc := load("res://scripts/level.gd")
	if level_sc != null:
		var lv = _instantiate("level", "res://scripts/level.gd")
		if lv.has_method("je_izometricka") and lv.has_method("cell_center") and lv.has_method("cell_at"):
			_check(lv.je_izometricka(),
				"level.gd se hlásí jako izometrický (podle assets/spec.json)")
			# 2:1 znamená, že sousední buňka v ose X ujde 2× víc do strany než dolů.
			var c00: Vector2 = lv.cell_center(0, 0)
			var c10: Vector2 = lv.cell_center(1, 0)
			var c01: Vector2 = lv.cell_center(0, 1)
			var dx: float = abs(c10.x - c00.x)
			var dy: float = abs(c10.y - c00.y)
			_check(is_equal_approx(dx, 2.0 * dy) and dy > 0.0,
				"izo projekce 2:1 – krok (1,0) je %s (dx=%.1f, dy=%.1f)" % [str(c10 - c00), dx, dy])
			# A hlavně: zpětný převod musí sedět na SKUTEČNÝCH dlaždicích,
			# ne jen sám na sebe – bere se pozice vzniklé z projekce.
			#
			# POZOR na `:=`: `lv` je z `load()` bez typu, takže `lv.cell_at(...)`
			# nemá známý návratový typ a `var zpet := ...` spadne na
			# „Cannot infer the type" (CONVENTIONS.md §1). Typ se píše výslovně.
			var zpet: Vector2i = lv.cell_at(c10)
			_check(zpet == Vector2i(1, 0),
				"cell_at je zpětný převod cell_center pro (1,0) (%s)" % str(zpet))
			var zpet2: Vector2i = lv.cell_at(c01)
			_check(zpet2 == Vector2i(0, 1),
				"cell_at je zpětný převod cell_center pro (0,1) (%s)" % str(zpet2))
		_zavri(lv)

	var item_sc = load("res://scripts/item.gd")
	if item_sc != null:
		var it = _instantiate("předmět", "res://scripts/item.gd")
		_check(it.has_method("use") and it.has_method("repair") and it.has_method("broken"),
			"item.gd poskytuje use/repair/broken")
		var d0 = it.get("trvanlivost")
		if d0 == null:
			d0 = it.get("durability")
		if d0 != null and it.has_method("use") and it.has_method("repair"):
			it.use()
			var d1 = it.get("trvanlivost") if it.get("trvanlivost") != null else it.get("durability")
			_check(int(d1) < int(d0) or it.broken(),
				"use() snižuje trvanlivost (%s → %s)" % [str(d0), str(d1)])
			it.repair()
			_check(not it.broken(), "repair() obnoví předmět")
		_zavri(it)

	# --------------------------------------------------------------- boj ----
	# FUNKČNÍ kontrola, ne jen `has_method`. Naměřeno 2. 10. 2026: `combat.gd`
	# volal `attacker.has("zbran")` a `defender.has("armor_rating")` — to je
	# **Godot 3 API**, které v Godotu 4 NEEXISTUJE. Bylo to ale uvnitř `if hit:`,
	# takže to spadlo jen při zásahu (≈ 50 %). Test se ptal jen
	# `has_method("resolve")`, takže vadu neviděl — a `resolve()` nikdo nezavolal.
	#
	# Teď se `resolve()` VOLÁ a ověřuje se `{hit, damage}`.
	#
	# ⚠ POZOR NA TVAR ATRAPY (naměřeno při psaní tohohle testu): `TestAtributy`
	# v tomhle souboru má `hodnota()`? **NEMÁ** — vystavuje `Str`/`Dex` rovnou
	# (proto testy výš čtou atributy přes `Object.get("Str")`). První verze testu
	# se ptala `cb.resolve()` s atrapou, která `hodnota()` neměla, a `combat.gd`
	# na tom spadl: `Nonexistent function 'hodnota' in base 'Node (TestAtributy)'`.
	# Atrapa tady proto schválně `hodnota()` NEMÁ — test tím měří i to, že si
	# combat poradí s TVAREM, jaký má `attributes.gd` doopravdy.
	var combat_sc = load("res://scripts/combat.gd")
	if combat_sc == null:
		# Soubor, který součástí hry být MÁ, musí při nenačtení SELHAT.
		_check(false, "combat.gd jde načíst (dřív se nenačtený přeskočil)")
	else:
		var kostra_b = _kostra_registru()
		root.add_child(kostra_b)

		var atr_b = TestBojAtributy.new()
		atr_b.Str = 10
		atr_b.Dex = 10
		kostra_b.add_child(atr_b)
		kostra_b.pridej("Attributes", atr_b)

		var skl_b = TestBojSkilly.new()
		skl_b.boj_na_blizko = 0
		kostra_b.add_child(skl_b)
		kostra_b.pridej("Skills", skl_b)

		var cb = combat_sc.new()
		if not (cb is Node):
			_check(false, "combat.gd vrací potomka Node (ne RefCounted)")
		else:
			kostra_b.add_child(cb)
			var utocnik_b = TestBojovnik.new()
			kostra_b.add_child(utocnik_b)

			var mec_b = TestZbran.new()
			mec_b.damage = 3
			utocnik_b.vybrana_zbran = mec_b

			var obrance_b = TestBojovnik.new()
			obrance_b.armor_rating = 1
			kostra_b.add_child(obrance_b)

			# HIT i MISS: `hit_chance` je 0,5, takže jeden seed nestačí — a bez
			# obou větví by se netestovala polovina funkce. Semínka se hledají
			# z pevného rozsahu, takže výsledek je reprodukovatelný.
			var zasah_b = null
			var minut_b = null
			for s in range(1, 41):
				seed(s)
				var v = cb.resolve(utocnik_b, obrance_b)
				if v.get("hit", false):
					if zasah_b == null:
						zasah_b = v
				elif minut_b == null:
					minut_b = v
				if zasah_b != null and minut_b != null:
					break

			_check(zasah_b != null and minut_b != null,
				"combat.resolve() umí zásah i minutí (zásah: %s, minutí: %s)"
				% [str(zasah_b), str(minut_b)])
			# Zásah: 1 + Str/10 (2) + zbraň (3) − zbroj (1) = 4.
			# Kdyby se četla zbraň nebo zbroj přes `has()`, spadlo by to tady.
			_check(zasah_b != null and int(zasah_b.get("damage", -1)) == 4,
				"zásah: damage = 1 + Str/10 + zbraň − zbroj = 4 (naměřeno: %s)"
				% str(zasah_b.get("damage", -1) if zasah_b != null else "žádný zásah"))
			_check(minut_b != null and int(minut_b.get("damage", -1)) == 0,
				"minutí: damage je 0, ne zásah naslepo (naměřeno: %s)"
				% str(minut_b.get("damage", -1) if minut_b != null else "žádné minutí"))

			# Druhý tvar smlouvy: atributy s `hodnota(attr)` — tak vypadá
			# `attributes.gd`. A tady je **LÉK NA NÁLEZ H2/H12**, naměřený
			# 2. 10. 2026 a doložený mutací (M3: vypuštění větve `hodnota()`):
			#
			# `combat._cislo()` má DVĚ větve — napřed `komponenta.hodnota(klic)`,
			# teprve pak vlastnost téhož jména. Aby test poznal, KTEROU z nich
			# použil, musí atrapa dát **různá čísla pro každou větev**. Když se
			# atrapa ptá na `hodnota("Str")` a vlastnost `Str` je 10, musí vyjít
			# **13** — číslo, které umí dát JEN větev `hodnota()`:
			#   hodnota("Str") = 100  →  1 + 100/10 = 11  →  +3 zbraň −1 zbroj = 13
			#   vlastnost  Str =  10  →  1 +  10/10 =  2  →  +3 zbraň −1 zbroj =  4
			# Kdyby se ptalo na vlastnost, vyjde 4 a kontrola SPADNE. Atrapa
			# **v rozporu se sebou samou** je to, co z větve dělá měřenou věc.
			#
			# (Předchozí verze tvrdila jen `damage > 0`; to splní i hodnota 4,
			# takže mutace M3 prošla — nález H12. Proto je tu teď rovnost.)
			var atr_h = TestAtributyHodnota.new()
			kostra_b.add_child(atr_h)
			kostra_b.pridej("Attributes", atr_h)
			var skl_h = TestSkillyHodnota.new()
			kostra_b.add_child(skl_h)
			kostra_b.pridej("Skills", skl_h)
			var pres_hodnota = null
			for s in range(1, 41):
				seed(s)
				var v3 = cb.resolve(utocnik_b, obrance_b)
				if v3.get("hit", false):
					pres_hodnota = v3
					break
			_check(pres_hodnota != null and int(pres_hodnota.get("damage", -1)) == 13,
				"combat.resolve() čte atributy větví hodnota(attr): atrapa v rozporu (hodnota 100 vs vlastnost 10) musí dát damage = 13, ne 4 (zásah: %s)"
				% str(pres_hodnota))
			# A TWŘENÝ DŮKAZ, ŽE SE TA VĚTEV OPRAVDU POUŽILA: kdyby combat
			# větví `hodnota()` neprošel, atrapa `TestAtributyHodnota` by taky
			# zůstala na nule — a to se pozná podle čítače uvnitř atrapy.
			_check(atr_h.vetev_hodnota >= 1,
				"atrapa potvrzuje, že resolve() volal hodnota(attr) (volání: %d)"
				% atr_h.vetev_hodnota)

			# `zbran` je starší název téhož — kdo ji má, nesmí být potrestaný.
			utocnik_b.vybrana_zbran = null
			utocnik_b.zbran = mec_b
			seed(1)
			var v2 = cb.resolve(utocnik_b, obrance_b)
			_check(typeof(v2) == TYPE_DICTIONARY and v2.has("hit") and v2.has("damage"),
				"combat.resolve() snese i vlastnost `zbran` (vrací {hit, damage})")

			# Zbraň NENÍ v stromu (do uzlu se přidávat nemusí), takže se musí
			# uvolnit ručně — jinak zůstane na konci běhu jako leak. Naměřeno:
			# bez tohohle řádku hlásil Godot 5 leaků místo 3.
			mec_b.free()

		_zavri(cb)
		_zavri(kostra_b)

	# ------------------------------------------------------------ těžba ----
	# FUNKČNÍ kontrola, ne jen `has_method`. Naměřeno 2. 10. 2026: `mining.gd`
	# volal `node.has()` (Godot 3 API, v Godot 4 neexistuje) a služby hledal na
	# `/root/Skills`, což v projektu není (žádný autoload) – `gather()` tedy
	# VŽDY spadlo. Testy to neviděly, protože se ptaly jen na přítomnost metody.
	var mining_sc = load("res://scripts/mining.gd")
	_check(mining_sc != null, "mining.gd jde načíst (dřív se nenačtený přeskočil)")
	if mining_sc != null:
		var kostra_t = _kostra_registru()
		root.add_child(kostra_t)
		var skilly_t = TestSkilly.new()
		skilly_t.dovednosti["tezba"] = 55
		kostra_t.add_child(skilly_t)
		kostra_t.pridej("Skills", skilly_t)
		var svet_t = TestSvet.new()
		kostra_t.add_child(svet_t)
		kostra_t.pridej("World", svet_t)

		var mn = mining_sc.new()
		kostra_t.add_child(mn)
		var ruda = TestUzelSuroviny.new()
		ruda.resource_id = "iron_ore"
		ruda.difficulty = 5
		var vynos = mn.gather(ruda)
		_check(vynos == 6, "mining.gather() vrátí 1+(55-5)/10 = 6 (naměřeno: %s)" % str(vynos))
		_check(int(skilly_t.hodnota("tezba")) == 56,
			"mining.gather() zvedne dovednost o 1 (55 → %d)" % int(skilly_t.hodnota("tezba")))
		_check(svet_t.zavolano == 1,
			"mining.gather() oznámí světu gather(cell) (volání: %d)" % svet_t.zavolano)

		var drevo = TestUzelSuroviny.new()
		drevo.resource_id = "wood"
		drevo.difficulty = 5
		skilly_t.dovednosti["drevorubectvi"] = 30
		_check(mn.gather(drevo) == 3, "dřevo jde na dovednost drevorubectvi")

		# Negativní kontrola: bez registru se gather() nesmí tvářit jako úspěch.
		var mn_bez = mining_sc.new()
		root.add_child(mn_bez)
		_check(mn_bez.gather(TestUzelSuroviny.new()) == 0,
			"mining.gather() bez registru vrátí 0 a ohlásí to (žádná tichá nula)")
		_zavri(mn_bez)
		_zavri(ruda)
		_zavri(drevo)
		_zavri(kostra_t)

	var crafting_sc = load("res://scripts/crafting.gd")
	if crafting_sc != null:
		var cr = _instantiate("výroba", "res://scripts/crafting.gd")
		_check(cr.has_method("smelt") and cr.has_method("forge") and cr.has_method("repair"),
			"crafting.gd poskytuje smelt/forge/repair")
		_zavri(cr)

	var economy_sc = load("res://scripts/economy.gd")
	if economy_sc != null:
		var ec = _instantiate("ekonomika", "res://scripts/economy.gd")
		_check(ec.has_method("price") and ec.has_method("buy") and ec.has_method("sell"),
			"economy.gd poskytuje price/buy/sell")
		_zavri(ec)

	var npc_sc = load("res://scripts/npc.gd")
	if npc_sc != null:
		var np = _instantiate("npc", "res://scripts/npc.gd")
		_check(np.has_method("trade"), "npc.gd poskytuje trade(player)")
		_zavri(np)

	var enemy_sc = load("res://scripts/enemy.gd")
	if enemy_sc != null:
		var en = _instantiate("nepřítel", "res://scripts/enemy.gd")
		_check(en.has_method("attack") and en.has_method("drop_loot"),
			"enemy.gd poskytuje attack/drop_loot")
		_zavri(en)

	var offline_sc = load("res://scripts/offline.gd")
	if offline_sc != null:
		var of = _instantiate("offline", "res://scripts/offline.gd")
		_check(of.has_method("resolve"), "offline.gd poskytuje resolve(char, job, hodiny)")
		_zavri(of)

	var assist_sc = load("res://scripts/assist.gd")
	if assist_sc != null:
		var asist = _instantiate("asistence", "res://scripts/assist.gd")
		_check(asist.has_method("add_rule") and asist.has_method("evaluate"),
			"assist.gd poskytuje add_rule/evaluate")
		_zavri(asist)

	# ------------------------------------------------- ukládání a HUD ----
	# FUNKČNÍ kontroly. Dřív tu bylo jen `has_method("save")` a nenačtený soubor
	# se tiše přeskočil – proto prošly PR #28 a #29 zeleným CI, i když:
	#   * `save.gd` hledal komponenty ve skupinách, které nikdo nezakládá →
	#     uložil jen pozici hráče (35 B) a PŘESTO vrátil `true`,
	#   * `hud.gd` spadl v `_ready()` na `margin_left` (Godot 4 zná `offset_*`)
	#     a na `has_property()` → lišta se vůbec nepřidala do scény.
	# Teď se funkce OPRAVDU zavolají, a to proti zkušební kostře s registrem
	# `component(id)` (docs/ARCHITEKTURA.md:145) – stejné rozhraní, jaké bude
	# mít `game.gd` po granuli engine.shell.
	var save_sc = load("res://scripts/save.gd")
	_check(save_sc != null, "save.gd jde načíst (dřív se nenačtený přeskočil)")
	var hud_sc = load("res://scripts/hud.gd")
	_check(hud_sc != null, "hud.gd jde načíst (dřív se nenačtený přeskočil)")

	if save_sc != null and hud_sc != null:
		# Aby testy nepřepsaly rozehranou pozici hráče, uložený soubor se na konci
		# vrátí do původního stavu (nebo se smaže, když předtím nebyl).
		var existoval_pred := FileAccess.file_exists("user://save.cfg")
		var ulozeny_pred := PackedByteArray()
		if existoval_pred:
			ulozeny_pred = FileAccess.get_file_as_bytes("user://save.cfg")

		var kostra = _kostra_registru()
		root.add_child(kostra)
		var atr = TestAtributy.new()
		atr.Str = 13
		atr.Dex = 17
		atr.Int = 21
		var skl = TestSkilly.new()
		skl.dovednosti["tezba"] = 7
		var eko = TestEkonomika.new()
		eko._gold = 42
		var hrac_t = TestHrac.new()
		hrac_t.position = Vector2(48, 96)
		for dvojice in [[atr, "Attributes"], [skl, "Skills"], [eko, "Economy"], [hrac_t, "Player"]]:
			kostra.add_child(dvojice[0])
			kostra.pridej(dvojice[1], dvojice[0])

		var sv = save_sc.new()
		kostra.add_child(sv)
		_check(sv.save() == true, "save() uloží stav a vrátí true")
		var cfg := ConfigFile.new()
		var nacteno := cfg.load("user://save.cfg")
		_check(nacteno == OK, "save.cfg jde načíst")
		if nacteno == OK:
			_check(int(cfg.get_value("attributes", "Str", -1)) == 13,
				"save() uloží atributy (Str=%d)" % int(cfg.get_value("attributes", "Str", -1)))
			_check(int(cfg.get_value("economy", "gold", -1)) == 42,
				"save() uloží zlato (%d)" % int(cfg.get_value("economy", "gold", -1)))
			var dov = cfg.get_value("skills", "dovednosti", {})
			_check(dov is Dictionary and int(dov.get("tezba", -1)) == 7, "save() uloží dovednosti")
			_check(cfg.has_section_key("player", "position"), "save() uloží pozici hráče")

		# Změň stav a načti ho zpět – ověří se tím i `load()`, ne jen zápis.
		atr.Str = 1
		skl.dovednosti["tezba"] = 0
		eko._gold = 0
		hrac_t.position = Vector2.ZERO
		_check(sv.load() == true, "load() vrátí true")
		_check(atr.Str == 13 and eko._gold == 42 and int(skl.hodnota("tezba")) == 7
			and hrac_t.position == Vector2(48, 96),
			"load() vrátí uložený stav (Str=%d, zlato=%d, tezba=%d)"
				% [atr.Str, eko._gold, int(skl.hodnota("tezba"))])

		# Negativní kontrola: bez registru se `save()` NESMÍ tvářit jako úspěch.
		var sv_bez = save_sc.new()
		root.add_child(sv_bez)
		_check(sv_bez.save() == false,
			"save() bez registru komponent vrátí false (dřív vracel true nad prázdnem)")
		_zavri(sv_bez)

		# HUD: musí se opravdu přidat do scény a ukázat hodnoty z registru.
		var hu = hud_sc.new()
		kostra.add_child(hu)
		_check(hu.get_child_count() == 1,
			"hud.gd přidá label do scény (dětí: %d)" % hu.get_child_count())
		if hu._label != null:
			var text_l: String = str(hu._label.text)
			_check(text_l.contains("Str: 13"), "HUD ukazuje atributy z registru")
			_check(text_l.contains("Zlato: 42"), "HUD ukazuje zlato z registru")
			_check(text_l.contains("tezba: 7"), "HUD ukazuje dovednosti z registru")
		else:
			_check(false, "hud.gd nemá label – spadl v _ready()?")

		if existoval_pred:
			var f = FileAccess.open("user://save.cfg", FileAccess.WRITE)
			if f != null:
				f.store_buffer(ulozeny_pred)
				f.close()
		else:
			DirAccess.remove_absolute(ProjectSettings.globalize_path("user://save.cfg"))
		_zavri(kostra)

	# Data (data.content): 4 skilly sjednocené napříč hrou – žádná alchymie.
	var skills_data: Array = []
	if FileAccess.file_exists("res://assets/data/skills.json"):
		var parsed_skills = JSON.parse_string(FileAccess.get_file_as_string("res://assets/data/skills.json"))
		if parsed_skills is Array:
			skills_data = parsed_skills
	_check(not skills_data.is_empty(), "skills.json je pole s dovednostmi")
	var ids_skillu: Array = []
	for s in skills_data:
		if s is Dictionary:
			ids_skillu.append(str(s.get("id", "")))
	var cekane_skilly := ["tezba", "drevorubectvi", "kovarstvi", "boj_na_blizko"]
	var maji_vsechny := true
	for c in cekane_skilly:
		if not ids_skillu.has(c):
			maji_vsechny = false
	_check(maji_vsechny, "dovednosti jsou sjednocené: %s" % str(ids_skillu))

	# Migrace monolitu (engine.shell): game.gd = kostra s registrem, alchymie pryč.
	if main.has_method("component"):
		var chybejici_komponenty := 0
		for nm in ["Skills", "Attributes", "World", "Hud"]:
			if main.component(nm) == null:
				chybejici_komponenty += 1
		_check(chybejici_komponenty == 0,
			"kostra instancuje komponenty z registru (%d chybí)" % chybejici_komponenty)
		_check(not zdroj.contains("alchymie") and not zdroj.contains("cas_dne"),
			"monolit je pryč: game.gd už nezná alchymii ani denní cyklus")

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

	_finish()


func _finish() -> void:
	_done = true
	print("\n[test] %d kontrol, %d selhání" % [checks, failures])
	quit(failures)


func _instantiate(oblast: String, cesta: String):
	"""Vytvoří instanci skriptu granule a varuje, když není potomkem Node.

	POZOR – PROČ TO EXISTUJE (naměřeno 30. 9. 2026, běh #122): když soubor
	deklaruje `class_name GameItem` a zároveň uvnitř definuje `class GameItem`,
	vnořená třída přebije globální jméno. `new()` pak vrátí vnořenou třídu –
	nemá smluvní metody – a když je potomkem RefCounted, spadne na `free()`.
	Chyba v _run() přeruší CELÝ běh testů, takže se nikdy nedojde na _finish(),
	testy visí do tvrdého limitu 90 s a v logu je jen „testy se zasekly".
	Příčina je přitom neviditelná. Tenhle pomocník ji vysype do logu hned.
	"""
	var sc = load(cesta)
	if sc == null:
		return null
	var obj = sc.new()
	if obj == null:
		print("[test]      %s: %s.new() vrátil null" % [oblast, cesta])
		return null
	if not (obj is Node):
		print("[test]      %s: %s nevrací potomka Node, ale %s – půjde zavřít"
			% [oblast, cesta, obj.get_class()])
		print("[test]      → pravděpodobně vnořená `class` stíní `class_name`,"
			+ " nebo soubor nezačíná `extends Node`")
	return obj


func _zavri(obj) -> void:
	"""Uvolní instanci granule. Nikdy neshodí běh testů."""
	if obj == null:
		return
	if obj is Node:
		obj.free()
	# Potomek RefCounted (Resource, Object) se uvolní sám; `free()` na něm
	# vyhodí chybu a přeruší _run() – což se přesně jednou stalo.

func _kostra_registru():
	"""Zkušební kostra s `component(id)` – totéž rozhraní, jaké bude mít
	`game.gd` (docs/ARCHITEKTURA.md:145). Komponenty berou služby z registru
	na svém RODIČI; tímhle se to ověří, aniž by testy pouštěly celou hru."""
	var k = TestKostra.new()
	k.name = "TestKostra"
	return k


class TestKostra:
	extends Node
	var komponenty := {}

	func component(id: String):
		return komponenty.get(id)

	func pridej(id: String, uzel: Node) -> void:
		komponenty[id] = uzel


class TestAtributy:
	extends Node
	var Str := 10
	var Dex := 10
	var Int := 10


class TestSkilly:
	extends Node
	var dovednosti: Dictionary = {"tezba": 0, "drevorubectvi": 0, "kovarstvi": 0, "boj_na_blizko": 0}

	func hodnota(skill: String) -> int:
		return int(dovednosti.get(skill, 0))

	func add(skill: String, n: int) -> void:
		if dovednosti.has(skill):
			dovednosti[skill] = clamp(int(dovednosti[skill]) + n, 0, 100)


class TestEkonomika:
	extends Node
	var _gold := 0

	func gold(_player) -> int:
		return _gold


class TestHrac:
	extends Node2D


class TestSvet:
	extends Node
	var zavolano := 0
	var posledni_cell = null

	func gather(cell) -> bool:
		zavolano += 1
		posledni_cell = cell
		return true


class TestUzelSuroviny:
	extends Node
	var resource_id := "iron_ore"
	var difficulty := 10
	var cell := Vector2i(1, 1)


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


class TestAtributyHodnota:
	extends Node
	"""Atributy, kde je `hodnota(attr)` **V ROZPORU** s vlastností téhož jména.

	PROČ SCHVÁLNĚ ROZPORNÉ (lék na nález H2/H12, naměřený 2. 10. 2026):
	`combat._cislo()` zkouší nejdřív `hodnota(klic)` a teprve pak vlastnost.
	Atrapa, kde obojí vrací TOTÉŽ číslo, tomu rozdílu **nemůže** nic naučit —
	mutace „vypustit větev hodnota()" (M3) se v ní neprojeví. Tady se projeví:
	`hodnota("Str")` je 100, ale vlastnost `Str` je 10. Správná větev dá
	damage **13**, větev s vlastností by dala **4**.

	Čítač `vetev_hodnota` je druhý, nezávislý důkaz: i kdyby obě větve daly
	stejné číslo, je z něj vidět, KTERÁ se zavolala (nula = nevolala se).
	"""
	var Str := 10
	var Dex := 10
	var vetev_hodnota := 0

	func hodnota(attr: String) -> int:
		vetev_hodnota += 1
		match attr:
			"Str": return 100
			"Dex": return 100
			_: return 0


class TestSkillyHodnota:
	extends Node
	"""Dovednosti pro tutéž sondu — `hodnota()` v rozporu s vlastností.

	`hodnota("boj_na_blizko")` dává 100, vlastnost 0: kdyby combat četl
	vlastnost, vyšlo by damage 4 místo 13. A zároveň platí, že
	`_cislo(skilly, "boj_na_blizko")` **nesmí** spadnout na `Nonexistent
	function` — přesně na tom padal combat před opravou 2. 10. 2026.
	"""
	var boj_na_blizko := 0

	func hodnota(_skill: String) -> int:
		return 100


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
