# Code-Anlage 1 für die Masterarbeit von Frederic Horn

# Berechnung aller minimaler Korrekturmultimengen für zykische Gruppen
# Der Algorithmus ist beschrieben im Beweis von Lemma 3.
# Es findet eine Berechnung von M_{Z_{m},ω}^{m} statt.
# Für M_{Z_{m},ω}^{n} mit n!=m beachte Lemma 2.5 und 2.6.

# Erweitert rekursiv einen Teilvektor 'kv' mit allen möglichen Kombinationen
# aus Gruppenelementen in Z_{'ordnung'}, sodass die Komponentensumme 'omega' beträgt
def alleKorrekturvektorenRek(ordnung, omega, kv):

    # Im allgemeinen Fall wird der betrachtete Teilvektor um alle möglichen Elemente erweitert
    if len(kv) < ordnung - 1:
        ListeAllerKv = []

        for i in range(ordnung):
            ListeAllerKv.extend(alleKorrekturvektorenRek(ordnung, omega, kv + [i]))
        return ListeAllerKv

    # Im Fall, dass nur noch ein Element fehlt, wird das letzte Element bestimmt, das benötigt
    # wird, um die Komponentensumme 'omega' zu erreichen
    if len(kv) == ordnung - 1:
        return [kv + [(omega - sum(kv)) % ordnung]]


# Erzeugt rekursiv eine Liste aller Korrekturvektoren (KV)
def alleKorrekturvektoren(ordnung, omega):
    ListeAllerKv = []

    # Es werden zunächst alle Elemente der Gruppe als mögliches erstes Element betrachtet
    for i in range(ordnung):
        # Diese einelementigen Listen werden durch die rekursive Funktion zu KV erweitert
        ListeAllerKv.extend(alleKorrekturvektorenRek(ordnung, omega, [i]))

    return ListeAllerKv

# Erzeugt aus einem Korrekturvektor 'kv' die zugehörige, aufsteigend sortierte Korrekturmultimenge
def kvZuKmm(ordnung, kv):
    zaehler = []

    for i in range(ordnung):
        zaehler.append(kv.count(i))

    return zaehler[1:]

# Hilfsfunktion zum entfernen von Duplikaten
def entferneDuplikate(listeVonListen):
    # Wandelt jede innere Liste in ein Tupel um
    listeVonTupeln = [tuple(innereListe) for innereListe in listeVonListen]

    # Wandelt die Liste in eine Menge um, um Duplikate zu entfernen
    einzigartigeTupel = set(listeVonTupeln)

    # Wandelt die Tupel zurück in Listen um
    einzigartigeListen = [list(inneresTupel) for inneresTupel in einzigartigeTupel]

    return einzigartigeListen

# Hilfsfunktion zum Bestimmen, ob eine Liste eine andere dominiert
def dominiert(liste_a, liste_b):
    # Überprüft, ob die Listen die gleiche Länge haben
    if len(liste_a) != len(liste_b):
        raise ValueError("Die Listen müssen die gleiche Länge haben.")

    # Vergleicht die Elemente in den Listen komponentenweise
    # Wenn jedes Element in liste_a größer oder gleich dem entsprechenden Element in liste_b ist,
    # wird True zurückgegeben, ansonsten False
    return all(a >= b for a, b in zip(liste_a, liste_b))

# Hilfsfunktion zum Entfernen aller Werte an den Stellen 'indices' aus einer Liste
def entferne_elemente_an_indizes(liste, indizes):
    # Erstellen einer Menge von Indizes für eine schnellere Mitgliedschaftsprüfung
    setIndizes = set(indizes)

    # Erstellen einer neuen Liste mit den Elementen, deren Indizes nicht in der Menge sind
    neueListe = [element for index, element in enumerate(liste) if index not in setIndizes]

    return neueListe

# Entfernt alle Kmm, die andere Kmm dominieren
def entferneDominierendeKmm(ListeKmm):
    zuLoeschen = []

    # prfüfe, ob eine andere Kmm dominiert wird, wenn dann speichere den Index
    for i in range(len(ListeKmm)):
        for j in range(len(ListeKmm)):
            if i == j: continue
            if dominiert(ListeKmm[j], ListeKmm[i]):
                zuLoeschen.append(j)

    # entferne alle Einträge an den Indizes, die dominierende Kmm enthalten
    return entferne_elemente_an_indizes(ListeKmm, zuLoeschen)

# Hilfsfunktion, wandelt die Kmm in die gängige Schreibweise um
def zaehlerformZuMultimengenform(kmmZ):
    kmm = []

    for i in range(len(kmmZ)):
        kmm.extend([i+1]*kmmZ[i])

    return kmm

def berechnen():
    # Odnung der zyklischen Gruppe (m)
    # Es sei m > 1
    ordnung = 5

    # ω in [m-1]
    omega = 4

    # Liste aller Korrekturvektoren
    ListeKv = alleKorrekturvektoren(ordnung, omega)

    # Liste aller Korrekurmultimengen (Kmm) in der Zählerschreibweise
    ListeKmm = list(map(lambda kv: kvZuKmm(ordnung, kv), ListeKv))

    # Liste aller Kmm ohne Duplikate
    ListeODKmm = entferneDuplikate(ListeKmm)

    # Liste aller Kmm, die keine andere Kmm dominieren
    ListeOhneDominierende = entferneDominierendeKmm(ListeODKmm)

    # Minimale Kmm
    MinimaleKmm = list(map(zaehlerformZuMultimengenform, ListeOhneDominierende))

    print(MinimaleKmm)

# Aufruf der Berechnung
berechnen()