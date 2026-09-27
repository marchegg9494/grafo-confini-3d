# Grafo dei confini 3D

Grafo interattivo degli Stati del mondo: ogni nodo è uno Stato, ogni arco un confine terrestre, con i km di ciascun confine. Si naviga come una mappa, e con Shift (o con due dita sul telefono) si ruota in 3D.

**Demo:** https://NOME-UTENTE.github.io/grafo-confini-3d/

## Cosa si può fare

- **Navigare come su una mappa.** Trascinando si sposta la vista, la rotella fa lo zoom verso il puntatore, e con Shift + trascina o col tasto destro si ruota in 3D. Sul telefono un dito sposta la vista e due dita fanno zoom e rotazione.
- **Selezionare uno Stato** con un clic o con la ricerca. Lo Stato si ingrandisce, gli archi verso i confinanti vengono evidenziati e la vista inquadra tutti i vicini. Una scheda elenca i confini dal più lungo al più corto, e si può saltare da uno Stato a un confinante.
- **Rappresentare i km di confine** in tre modi: archi tutti uguali, spessore proporzionale ai km, oppure lunghezza proporzionale ai km. La lunghezza è approssimata: in una simulazione a parte la correlazione tra lunghezza disegnata e km è circa 0,95.
- **Passare alla vista piatta 2D** e scegliere quante etichette mostrare: tutte, solo le principali o nessuna.

## Come funziona

`genera_grafo.py` scarica da Wikipedia la [tabella dei confini terrestri](https://en.wikipedia.org/wiki/List_of_countries_and_territories_by_land_borders), la legge con Beautiful Soup e costruisce il grafo con NetworkX. Tiene la componente connessa più grande e inserisce nodi e archi, in formato JSON, dentro `template.html`. Il risultato è `index.html`, una pagina statica senza server, che usa [3d-force-graph](https://github.com/vasturiano/3d-force-graph) per la disposizione a forze e la grafica 3D.

Durante la lettura dei dati lo script corregge alcuni problemi della tabella:
- i link tra parentesi non contano come confinanti, per esempio "Greenland (Denmark)" non fa confinare il Canada con la Danimarca;
- "People's Republic of China" e "China" diventano un unico nodo;
- la riga "France, Metropolitan" viene esclusa, perché ripete i confini europei della riga "France".

## Rigenerare la pagina

```bash
pip install -r requirements.txt
python genera_grafo.py
```

Poi basta aprire `index.html` nel browser. Serve internet, perché la libreria viene caricata da jsDelivr.

## Licenze

- Codice: MIT (vedi `LICENSE`).
- Dati: presi da Wikipedia, sotto licenza [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). I dati contenuti in `index.html` restano sotto questa licenza.
