# Code-Anlage 1 für die Masterarbeit von Frederic Horn

# Berechnung aller minimaler Korrekturmultimengen für zykische Gruppen
# und die Kleinsche Vierergruppe (siehe dafür Methode "allgemeine_summe").
# Sowie Berechnung der Eckpunkte für Polymake.
# Es findet eine Berechnung von M_{G,ω}^{n} statt.

from itertools import product
import ast
from collections import Counter


# Summe in der Kleinschen Vierergruppe
# Die Elemente seien benannt durch KV = {0, 1, 2, 3}
# Es soll gelten:
# + | 0 1 2 3
# --/--------
# 0 | 0 1 2 3
# 1 | 1 0 3 2
# 2 | 2 3 0 1
# 3 | 3 2 1 0

def summe_KV(a,b):
    ax = a // 2
    ay = a % 2
    bx = b // 2
    by = b % 2
    return ((ax + bx) % 2) * 2 + (ay + by) % 2


# iteratives Aufaddieren mehrerer Elemente eines Vektors über der Kleinschen Vierergruppe
def summe_tupel_KV(vek, index=0, aktuelle_summe=0):
    if index == len(vek):
        return aktuelle_summe
    else:
        return summe_tupel_KV(vek, index + 1, summe_KV(aktuelle_summe, vek[index]))


# Allgemeine Bildung von Komponentensummen (zyklische Gruppen / Kleinsche Vierergruppe)
def allgemeine_summe(vek, ordnung):
    # Nutzen, wenn die Kleinsche Vierergruppe bei ordnung=4 betrachtet werden soll
    #if ordnung == 4:
    #   return summe_tupel_KV(vek)

    # Addition in der zyklischen Gruppe
    return sum(vek) % ordnung


# Ermittle alle Vektoren unter den Parametern
def alle_vektoren(n, ordnung, ω):
    Liste_Vektoren = []

    for vek in product(list(range(ordnung)), repeat=n):
        if allgemeine_summe(vek, ordnung) == ω:
            Liste_Vektoren.append(vek)

    return Liste_Vektoren


# Erhalte aus einem Vektor über einer Gruppe den zugehörigen binären Inzidenzvektor.
# Zusätzlich ist eine '1' vorne hinzugefügt, für die späteren Berechnungen bei Polymake.
def vektor_zu_homogenen_binaeren_vektor(vek, ordnung):
    binaerer_vektor = [1]
    for i in vek:
        binaerer_vektor.extend(list(map(lambda x: int(x == i), list(range(ordnung)))))
    return binaerer_vektor


# Berechne aus einer Liste von Vektoren die zugehörigen Korrekturmultimengen (Kmm) ohne Wiederholung.
# Zur Vermeidung der Wiederholungen werden die ELemente der Kmm sortiert, in einen "String"
# umgewandelt und durch "set" werden Wiederholungen entfernt. "ast.literal_eval" wandelt
# den "String" wieder in eine "List" um.
def alle_multimengen(Liste_Vektoren):
    mm_menge = set()

    for vek in Liste_Vektoren:
        ohne_0 = list(filter(lambda el: el != 0, vek))
        ohne_0.sort()

        mm_menge.add(str(ohne_0))

    return [ast.literal_eval(ms) for ms in mm_menge]


# Prüft ob die Multimenge "mm" die Supermenge einer Multimenge aus "mm_Liste" ist
def ist_echte_Supermenge(mm, mm_Liste):
    for akt_mm in mm_Liste:
        if ist_echte_multimengen_Teilmenge(akt_mm, mm):
            return True
    return False

# Prüft ob "multimenge1" echt in "multimenge2" enthalten ist
def ist_echte_multimengen_Teilmenge(multimenge1, multimenge2):
    # Konvertiere Multimengen zu "Counter"
    counter1 = Counter(multimenge1)
    counter2 = Counter(multimenge2)

    # Prüfe ob die Vektoren, die die Anzahlen der Elemente in den Multimengen zählen,
    # sich strikt dominieren
    return all(counter1[key] <= counter2[key] for key in counter1) and counter1 != counter2

def berechnen():
    # Ordnung der Gruppe
    ordnung = 5

    # Omega
    ω = 4

    # Anzahl der Blöcke
    n = 4

    # Berechne alle Vektoren mit Komponentensumme ω:
    vek_Liste = alle_vektoren(n, ordnung, ω)

    # Berechne alle Multimengen aus den Vektoren
    mm_Liste = alle_multimengen(vek_Liste)

    # Entferne alle dominierenden Multimengen
    msFilter = list(filter(lambda ms: not ist_echte_Supermenge(ms, mm_Liste), mm_Liste))
    print(msFilter)

    # Berechne alle Inzidenzvektoren
    Inzidenzvektoren = list(map(lambda vek: vektor_zu_homogenen_binaeren_vektor(vek, ordnung), vek_Liste))
    print(str(Inzidenzvektoren))

# Aufruf der Berechnung
berechnen()
