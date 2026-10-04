extends SceneTree
# Měření už SLUČNÉHO mining.gd (#30): jeho cesta ke službám je `/root/Skills`
# a `/root/World`, ale `project.godot` nemá ani jeden autoload a `scripts/world.gd`
# byl smazán (c651368). Testy přitom kontrolují jen `has_method("gather")`.


class Uzel:
	extends Node
	var resource_id := "iron_ore"
	var difficulty := 10
	var cell := Vector2i(1, 1)


var _hotovo := false


func _process(_delta: float) -> bool:
	if _hotovo:
		return true
	_hotovo = true

	print("=== mining.gd ze main (#30) ===")
	print("  /root/Skills existuje: %s" % str(root.get_node_or_null("Skills") != null))
	print("  /root/World existuje:  %s" % str(root.get_node_or_null("World") != null))
	var sc = load("res://mining.gd")
	print("  skript jde načíst: %s" % str(sc != null))
	var m = sc.new()
	root.add_child(m)
	var v = m.gather(Uzel.new())
	print("  gather(uzel s rudou, obtížnost 10) vrátilo: %s" % str(v))
	print("  (očekávání podle zadání granule: 1 + (skill 0 - 10)/10 → 0 při skillu 0;")
	print("   ale se skillem 100 musí vrátit víc — proto se ptám, jestli vůbec došlo na Skills)")
	quit(0)
	return true
