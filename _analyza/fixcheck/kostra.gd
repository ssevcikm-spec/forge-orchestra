extends Node
# Zkušební kostra: napodobuje `game.gd` s registrem `component(id) -> Node`
# (docs/ARCHITEKTURA.md:145). Slouží jen k měření save.gd/hud.gd.

var komponenty := {}


func component(id: String):
	return komponenty.get(id)


func pridej(id: String, uzel: Node) -> void:
	komponenty[id] = uzel


func odeber(id: String) -> void:
	komponenty.erase(id)
