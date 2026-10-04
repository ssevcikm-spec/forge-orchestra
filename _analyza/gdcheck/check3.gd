extends SceneTree
# Rozlišení: selhává ZÁPIS u mě v prostředí, nebo v kódu save.gd?
# (Pravidlo: nástroj, který „něco uloží", se musí ověřit — a když selže,
#  musí být jasné, čí je to vina.)

func _process(_delta: float) -> bool:
	print("user:// = %s" % ProjectSettings.globalize_path("user://"))
	var cfg := ConfigFile.new()
	cfg.set_value("test", "x", 1)
	var err := cfg.save("user://save.cfg")
	print("přímý ConfigFile.save() → chyba %d (%s)" % [err, error_string(err)])

	var fa := FileAccess.open("user://probe.txt", FileAccess.WRITE)
	print("FileAccess.open('user://probe.txt', WRITE) → %s" % str(fa))
	if fa != null:
		fa.store_string("ahoj")
		fa.close()
		print("  zapsáno, velikost na disku: %d B" % FileAccess.get_file_as_bytes("res://__neexistuje").size())

	print("soubor po zápisu existuje: %s" % str(FileAccess.file_exists("user://save.cfg")))
	quit(0)
	return true
