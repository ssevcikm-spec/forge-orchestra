extends Node

var dovednosti: Dictionary = {"tezba": 0, "drevorubectvi": 0, "kovarstvi": 0, "boj_na_blizko": 0}

func _init() -> void:
    pass

func add(skill: String, n: int) -> void:
    if dovednosti.has(skill):
        dovednosti[skill] = clamp(dovednosti[skill] + n, 0, 100)

func hodnota(skill: String) -> int:
    if dovednosti.has(skill):
        return dovednosti[skill]
    return 0
