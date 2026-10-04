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
			# `attributes.gd`. `TestAtributy` výš má Str=10, Dex=10, takže
			# hit_chance vyjde 0,55 místo 0,5; kdyby combat `hodnota()` neuměl,
			# spadne na `Nonexistent function 'hodnota'`.
			#
			# Pozor na past: TADY SE NESMÍ TVRDIT KONKRÉTNÍ damage. Počet volání
			# `randf()` před touhle kontrolou není pevný, takže „seed(1) → 4" by
			# záviselo na tom, kolik zásahů našly smyčky výš. Měří se proto jen
			# to, co je na cestě nezávislé: zásah nastane a poškození je kladné.
			var atr_h = TestAtributy.new()
			atr_h.Str = 10
			atr_h.Dex = 10
			kostra_b.add_child(atr_h)
			kostra_b.pridej("Attributes", atr_h)
			var skl_h = TestSkilly.new()
			skl_h.dovednosti["boj_na_blizko"] = 0
			kostra_b.add_child(skl_h)
			kostra_b.pridej("Skills", skl_h)
			var pres_hodnota = null
			for s in range(1, 41):
				seed(s)
				var v3 = cb.resolve(utocnik_b, obrance_b)
				if v3.get("hit", false):
					pres_hodnota = v3
					break
			_check(pres_hodnota != null and int(pres_hodnota.get("damage", 0)) > 0,
				"combat.resolve() čte i atributy s hodnota(attr) (zásah: %s)"
				% str(pres_hodnota))

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
