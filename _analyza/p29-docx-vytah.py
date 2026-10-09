# P29: vytah textu z prilozeneho konceptu (docx) do .txt pro cteni a analyzu.
# Vstup:  C:\Users\Ssevc\Desktop\Gemini architektonika.docx
# Vystup: _analyza\p29-gemini-architektonika.txt  (kandidat: _analyza\_archiv\)
# Pozn.: jen CTE cizi soubor na plose, nikam nezapisuje.
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn

VSTUP = Path(r"C:\Users\Ssevc\Desktop\Gemini architektonika.docx")
VYSTUP = Path(__file__).with_name("p29-gemini-architektonika.txt")


def bloky(doc):
    """Iteruje telo dokumentu ve skutecnem poradi (odstavce i tabulky)."""
    telo = doc.element.body
    for child in telo.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, doc)
        elif child.tag == qn("w:tbl"):
            yield Table(child, doc)


def main():
    if not VSTUP.exists():
        print("CHYBA: vstup neexistuje:", VSTUP)
        return 1
    doc = Document(str(VSTUP))
    radky = []
    for b in bloky(doc):
        if isinstance(b, Paragraph):
            t = b.text.rstrip()
            if t:
                styl = b.style.name if b.style is not None else "?"
                if styl.lower().startswith("heading"):
                    radky.append("")
                    radky.append("### [%s] %s" % (styl, t))
                else:
                    radky.append(t)
        else:
            radky.append("")
            radky.append("--- TABULKA ---")
            for row in b.rows:
                bunky = [c.text.replace("\n", " / ").strip() for c in row.cells]
                radky.append(" | ".join(bunky))
            radky.append("--- KONEC TABULKY ---")
            radky.append("")
    text = "\n".join(radky) + "\n"
    VYSTUP.write_text(text, encoding="utf-8", newline="")
    print("zapsano:", VYSTUP)
    print("znaku:", len(text), "radku:", len(text.splitlines()))
    print("odstavcu:", len(doc.paragraphs), "tabulek:", len(doc.tables))
    return 0


if __name__ == "__main__":
    sys.exit(main())
