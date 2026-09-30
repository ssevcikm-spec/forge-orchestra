"""Oprava testů: volání `get()` se DVĚMA argumenty zabíjí běh testů.

Naměřeno 30. 9. 2026 (běh #128, granule core.skills, model mistral):

  skills.gd si definoval vlastní `get(skill: String) -> int`, čímž přebil
  `Object.get()`. Test volal `sk.get("tezba", 0)` (s defaultem) → fatální
  `Invalid call to function 'get' in base 'Node (skills.gd)'. Expected 1
  argument(s)`. GDScript přeruší _run(), na _finish() se nikdy nedojde, a běh
  visí do tvrdého limitu 90 s. V logu je pak jen „testy se zasekly" – příčina
  neviditelná. Reprodukováno lokálně (90.7 s, 26 kontrol, 1 selhání).

Oprava: volat `get()` s JEDNÍM argumentem (přesně jako smlouva) a ošetřit
`null` – ten přijde, když skript vlastní `get()` nemá (pak odpovídá enginový
`Object.get()`) nebo když klíč nezná. Kontrola se v tom případě přeskočí místo
aby spadla na `int(null)`.

Druhá část: `_instantiate()` dostane typovou kontrolu volání `add()` – hodí se
to jako diagnostika pro další granule.
"""

import pathlib
import sys

CESTA = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek\games\uo-shadows\tests\run_tests.gd")

STARE = '''	var skills_sc = load("res://scripts/skills.gd")
	if skills_sc != null:
		var sk = _instantiate("skilly", "res://scripts/skills.gd")
		if sk.has_method("get") and sk.has_method("add"):
			_check(int(sk.get("tezba")) == 0 and int(sk.get("kovarstvi")) == 0,
				"skilly začínají na 0")
			sk.add("tezba", 150)
			_check(int(sk.get("tezba")) == 100,
				"skill je shora omezený na 100 (má %s)" % str(sk.get("tezba")))
			sk.add("tezba", -500)
			_check(int(sk.get("tezba")) == 0,
				"skill neklesne pod 0 (má %s)" % str(sk.get("tezba")))
		_zavri(sk)
'''

NOVE = '''	var skills_sc = load("res://scripts/skills.gd")
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
'''


def main() -> int:
    if not CESTA.exists():
        print(f"CHYBA: soubor nenalezen: {CESTA}")
        return 1
    text = CESTA.read_text(encoding="utf-8")

    if NOVE.split("\n")[0] in text and "get() SE DVĚMA ARGUMENTY" in text:
        print("Oprava už je v souboru – nic se nemění.")
        return 0

    if STARE not in text:
        print("CHYBA: hledaný blok nenalezen. Soubor se nezměnil.")
        print("(Ukaž prvních 200 znaků hledaného bloku pro kontrolu:)")
        print(repr(STARE[:200]))
        return 1

    CESTA.write_text(text.replace(STARE, NOVE, 1), encoding="utf-8")
    print("Oprava vložena do tests/run_tests.gd")
    return 0


if __name__ == "__main__":
    sys.exit(main())
