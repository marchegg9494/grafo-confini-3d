"""
Genera index.html: il grafo 3D interattivo degli Stati confinanti.

1. scarica da Wikipedia la tabella dei confini terrestri
2. per ogni Stato legge i confinanti e i km di ogni confine
3. costruisce il grafo con NetworkX e tiene la componente connessa più grande
4. inserisce nodi e archi (in JSON) nel template HTML

Uso:  python genera_grafo.py
"""

import json
import re
import ssl
import urllib.request
from pathlib import Path

import networkx as nx
from bs4 import BeautifulSoup

URL = "https://en.wikipedia.org/wiki/List_of_countries_and_territories_by_land_borders"
CARTELLA = Path(__file__).parent

# Nomi diversi per lo stesso Stato nelle diverse colonne della tabella
ALIAS = {"People's Republic of China": "China"}

# Righe che duplicano un altro Stato: "France, Metropolitan" ripete i confini
# europei già presenti nella riga "France"
RIGHE_ESCLUSE = {"France, Metropolitan"}

# Su Mac il Python di python.org non trova i certificati SSL: certifi li fornisce
try:
    import certifi
    CONTESTO_SSL = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    CONTESTO_SSL = None


def scarica(url):
    # Wikipedia rifiuta le richieste senza User-Agent
    richiesta = urllib.request.Request(url, headers={"User-Agent": "grafo-confini-3d"})
    with urllib.request.urlopen(richiesta, timeout=30, context=CONTESTO_SSL) as risposta:
        return risposta.read()


def nome(testo):
    testo = testo.strip()
    return ALIAS.get(testo, testo)


def leggi_confini(html):
    """Restituisce {(Stato, confinante): km} leggendo la tabella di Wikipedia."""
    tabella = BeautifulSoup(html, "html.parser").select("table.wikitable.sortable")[0]
    confini = {}

    for tr in tabella.find_all("tr"):
        celle = tr.find_all("td")
        if not celle:                    # riga di intestazione
            continue

        # il nome è il primo link con del testo (prima può esserci il link
        # della bandiera, e le stringhe iniziali della cella possono essere vuote)
        stato = nome(next(a.get_text() for a in celle[0].find_all("a") if a.get_text().strip()))
        if stato in RIGHE_ESCLUSE:
            continue

        # sesta colonna: "Austria: 430 km (270 mi) France: 488 km ..."
        # Il confinante è il primo link dopo il km precedente, escludendo le
        # note [1], [a], ... e i link tra parentesi, es. "Greenland (Denmark)".
        # Numero e "km" sono in tag diversi: accumulo il testo e cerco "<numero> km".
        attuale, testo, parentesi = None, "", 0
        for pezzo in celle[5].descendants:
            if pezzo.name == "a":
                t = pezzo.get_text().strip()
                if attuale is None and parentesi == 0 and t and "[" not in t:
                    attuale, testo = nome(t), ""
            elif pezzo.name is None and pezzo.parent.name != "a":   # testo fuori dai link
                parentesi += pezzo.count("(") - pezzo.count(")")
                if attuale:
                    testo += " " + pezzo
                    km = re.search(r"([\d,]+(?:\.\d+)?)\s*km", testo)
                    if km:
                        confini[(stato, attuale)] = float(km.group(1).replace(",", ""))
                        attuale = None
    return confini


def costruisci_grafo(confini):
    g = nx.Graph()
    for (a, b), km in confini.items():
        if a == b or b in RIGHE_ESCLUSE:
            continue
        # ogni confine compare due volte (A->B e B->A): tengo i km della prima
        if not g.has_edge(a, b):
            g.add_edge(a, b, km=km)
    return g


def main():
    print("Scarico", URL)
    confini = leggi_confini(scarica(URL))
    g = costruisci_grafo(confini)

    componenti = sorted(nx.connected_components(g), key=len, reverse=True)
    h = g.subgraph(componenti[0])
    print(f"Grafo: {g.number_of_nodes()} Stati, {g.number_of_edges()} confini, "
          f"{len(componenti)} componenti; la più grande ha {h.number_of_nodes()} Stati")

    dati = {
        "nodes": [{"id": n, "grado": h.degree(n)} for n in sorted(h)],
        "links": [{"source": a, "target": b, "km": km} for a, b, km in h.edges(data="km")],
    }
    template = (CARTELLA / "template.html").read_text(encoding="utf-8")
    pagina = template.replace("__DATI__", json.dumps(dati, ensure_ascii=False))
    (CARTELLA / "index.html").write_text(pagina, encoding="utf-8")
    print("Scritto", CARTELLA / "index.html")


if __name__ == "__main__":
    main()
