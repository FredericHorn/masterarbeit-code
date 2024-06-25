# Code-Anlage 4 für die Masterarbeit von Frederic Horn

# Bestimmung der Isomorphieklassen eingegebener Ungleichungen.

import ast

# Betrachtete Gruppenordnung
ordnung = 3

# String, der alle Ungleichungen enthält. Ausgabe von Code-Anlage 3 (polymake)
# Hier für Z_3, n=3
eingabe_string = """2 1 2 0 0 -2 -1 0 -2 -1
1 0 0 0 0 -1 -1 0 0 0
0 1 0 0 0 0 0 0 0 0
1 2 1 0 0 -1 -2 0 -1 1
2 1 -1 0 0 1 -1 0 -2 -1
1 0 0 0 0 0 0 0 -1 -1
4 -1 -2 0 0 -1 -2 0 -1 -2
2 1 -1 0 0 -2 -1 0 1 -1
1 2 1 0 0 -1 1 0 -1 -2
-1 1 2 0 0 1 2 0 1 -1
0 0 0 0 0 0 1 0 0 0
1 -1 1 0 0 -1 1 0 -1 1
0 0 1 0 0 0 0 0 0 0
2 -2 -1 0 0 -2 -1 0 1 2
1 -1 1 0 0 -1 -2 0 2 1
-1 1 -1 0 0 1 2 0 1 2
-2 2 1 0 0 2 1 0 2 1
0 0 0 0 0 0 0 0 0 1
-1 1 2 0 0 1 -1 0 1 2
1 -1 -2 0 0 2 1 0 -1 1
0 0 0 0 0 1 0 0 0 0
2 -2 -1 0 0 1 2 0 -2 -1
1 -1 1 0 0 2 1 0 -1 -2
1 -1 -1 0 0 0 0 0 0 0
2 -2 -1 0 0 1 -1 0 1 -1
1 -1 -2 0 0 -1 1 0 2 1
0 0 0 0 0 0 0 0 1 0"""

###############################################################################

# Vorbereiten der Eingabe.

# Eingegebener String wird als Matrix interpretiert
def string_zu_matrix(input_string):
    zeilen = input_string.strip().split('\n')
    matrix = []
    for zeile in zeilen:
        elemente = list(map(int, zeile.split()))
        matrix.append(elemente)
    return matrix

# Die Werte der ersten Spalte sind die rechten Seiten mit vertauschtem Vorzeichen. Diese werden hier extrahiert.
def extrahiere_und_entferne_erste_Spalte(matrix):
    erste_spalte = []
    for zeile in matrix:
        erste_spalte.append(zeile.pop(0))
    return erste_spalte

# Ungleichungsdefinierende Vektoren werden wieder mit der rechten Seite zusammengefügt.
def zu_ungleichungs_liste(matrix, erste_spalte):
    ungleichungs_liste = []
    for i in range(len(matrix)):
        ungleichungs_liste.append([matrix[i], -erste_spalte[i]])
    return ungleichungs_liste

# Erstellt aus der String-Eingabe eine Liste aller Ungleichungen im gewünschten Format.
def eingabe_zu_ungleichungs_liste(eingabe):
    matrix = string_zu_matrix(eingabe)
    erste_spalte = extrahiere_und_entferne_erste_Spalte(matrix)
    ungleichungs_liste = zu_ungleichungs_liste(matrix, erste_spalte)
    return ungleichungs_liste

################################################################################

# Hilfsmethoden

# Ausgabe einer Ungleichung im LaTeX-Format
def print_ugl(ugl):
    res = ""
    for i in range(len(ugl[0])):
        res += " & "
        if ugl[0][i] != 0:
            if ugl[0][i] >= 0:
                res += " + "
            else:
                res += " - "
            res += str(abs(ugl[0][i])) + " x^{" + str(i // ordnung) + "}_{" + str(i % ordnung) + "}"
    res += " & \geq " + str(ugl[1]) + " \\\\"
    return res

# Ermöglicht die Implementierung anderer Summen als bei zyjlischen Gruppen
# Hier nur für zyklische Gruppen
def spezielle_summe(tup, ord):
    return sum(tup) % ord

# Erzegt alle zyklischen Transversale rekursiv
def generiere_alle_ct(n, aktuelle_liste=[]):
    if len(aktuelle_liste) == n:
        if spezielle_summe(aktuelle_liste, ordnung) == 0:
            return [aktuelle_liste]
        else:
            return []

    cts = []
    for i in range(ordnung):
        neues_st = aktuelle_liste + [i]
        cts.extend(generiere_alle_ct(n, neues_st))

    return cts

# Prüft, ob die Eingabe n eine Primzahl ist.
def ist_prim(n):
    if n <= 1:
        return False
    elif n <= 3:
        return True
    elif n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


# Erzeugt eine Liste aller Automorphimen der Gruppe.
# Nur für zyklische Gruppen mit Ordnung, die prim oder vier ist.
def alle_automorphismen(ordnung):
    
    if ordnung == 4:
        return [[0, 1, 2, 3], [0, 3, 2, 1]]
    
    if not ist_prim(ordnung):
        return None
    
    auto_liste = []
    
    # Die Eins kann auf jedes Element, das nicht Null ist abbilden.
    for i in range(1, ordnung):
        auto = [k * i % ordnung for k in range(ordnung)]
        auto_liste.append(auto)
    return auto_liste


################################################################################

# Entferne isomorphe Ungleichungen, bringe alle in Normalform

# Addiere Block-Gleichungen, um alle Einträge positiv zu machen, aber den kleinsten gleich Null
def ugl_liste_0_gewichte(eingabe_liste_ugl):
    # Erstelle eine Kopie
    liste_ugl = [elem[:] for elem in eingabe_liste_ugl]
    for ugl in liste_ugl:
        for i in range(len(ugl[0])):
            if i % ordnung == 0:
                koeff_block_gleichungen = min(ugl[0][i:i+ordnung])
                for j in range(ordnung):
                    ugl[0][i + j] -= koeff_block_gleichungen
                ugl[1] -= koeff_block_gleichungen
    return liste_ugl

# Wende auf allen ungleichungsdefinierenden Vektoren die Block-Vertauschung und den Block-Isomorphismus an,
# die den lexikographisch kleinsten ungleichungsdefinierenden Vektor erzeugen.
def ugl_liste_sortieren(ugl_liste):
    neue_ugl_liste = []

    automorphismen = alle_automorphismen(ordnung)

    for ugl in ugl_liste:

        angewandte_automorphismen_liste = [[] for i in range(len(automorphismen))]

        n = round(len(ugl[0]) / ordnung)
        for i in range(n):
            for k in range(len(automorphismen)):
                # Tupel sind Teilvektoren, die die Koeffizienten eines Blockes enthalten
                tupel = [ugl[0][ordnung * i]]
                for j in range(1, ordnung):
                    tupel.append(ugl[0][ordnung * i + automorphismen[k][j]])
                angewandte_automorphismen_liste[k].append(tupel)

        # Lexikographische Sortierung der Blöcke
        for tuplel_liste in angewandte_automorphismen_liste:
            tuplel_liste.sort()

        # Lexikographische Sortierung der Automorphismen
        angewandte_automorphismen_liste.sort()

        neue_ugl = [[], ugl[1]]
        for i in range(n):
            for j in range(ordnung):
                neue_ugl[0].append(angewandte_automorphismen_liste[0][i][j])

        neue_ugl_liste.append(neue_ugl)

    return neue_ugl_liste

# Wende eine Block-Translation auf eine Ungleichung an
def shift_ugl(ugl, alle_ct_liste, i):
    komplette_geshiftete_ugl = []
    geshiftete_ugl = [0] * len(ugl[0])
    for j in range(len(ugl[0]) // ordnung):
        for k in range(ordnung):
            geshiftete_ugl[ordnung * j + (k + alle_ct_liste[i][j]) % ordnung] = ugl[0][ordnung * j + k]
    komplette_geshiftete_ugl.append(geshiftete_ugl)
    komplette_geshiftete_ugl.append(ugl[1])
    return komplette_geshiftete_ugl

# Wandle die Liste aller Ungleichungen in eine Liste um, die für jede ursprüngliche Ungleichung jede mögliche
# geschiftete Ungleichung enthält
def erweitere_ugl_liste_alle_ct(ugl_liste):
    alle_ct_liste = generiere_alle_ct(len(ugl_liste[0][0]) // ordnung)

    erweiterte_ugl_liste = []

    for ugl in ugl_liste:
        for i in range(len(alle_ct_liste)):
            erweiterte_ugl_liste.append(shift_ugl(ugl, alle_ct_liste, i))

    return erweiterte_ugl_liste

# Finde den Index eines Elements in einer Liste
def finde_element_index(lst, element):
    for index, wert in enumerate(lst):
        if wert == element:
            return index
    return -1

# Gehe die Liste aller Ungleichungen mit allen angewandten Shiftings iterativ durch.
# Prüfe ob die Anwendung irgendeines Shiftings zu einer bereits bekannten Ungleichung führt.
# Wenn ja, so ergänze die bekannte Ungleichung zur neuen Liste, ansonsten die Grundform der
# neuen Ungleichnung. (Wiederholungen werden später entfernt)
def kollabiere_erweiterte_liste(ugl_liste, len_ugl_liste):
    ct_anzahl = len(generiere_alle_ct(len(ugl_liste[0][0]) // ordnung))
    kollabierte_liste = []
    ausgewaehlte_shiftings = []
    for i in range(len_ugl_liste):
        for j in range(ct_anzahl):
            k = finde_element_index(ugl_liste[0:ct_anzahl * i], ugl_liste[ct_anzahl * i + j])
            if k == -1 or k % ct_anzahl != 0:
                if j == range(ct_anzahl)[-1]:
                    kollabierte_liste.append(ugl_liste[ct_anzahl * i])
                    ausgewaehlte_shiftings.append(0)
            else:
                kollabierte_liste.append(ugl_liste[ct_anzahl * (k // ct_anzahl)])
                ausgewaehlte_shiftings.append(j)
                break
    return kollabierte_liste, ausgewaehlte_shiftings


################################################################################

# Ausführung.

ugl_liste = eingabe_zu_ungleichungs_liste(eingabe_string)
len_ugl_liste = len(ugl_liste)

erweiterte_liste = erweitere_ugl_liste_alle_ct(ugl_liste)
null_gewicht_liste = ugl_liste_0_gewichte(erweiterte_liste)
sorted_list = ugl_liste_sortieren(null_gewicht_liste)


ugl_liste_ohne_symmetrie, ausgewaehlte_shiftings = kollabiere_erweiterte_liste(sorted_list, len_ugl_liste)

# Wandle Liste in Dictionary um, um Wiederholungen zu entfernen
dict = {}
for index, wert in enumerate(ugl_liste_ohne_symmetrie):
    # Wandle Liste in String um, damit sie hashable ist
    wert_str = str(wert)
    if wert_str not in dict:
        dict[wert_str] = [index]
    else:
        dict[wert_str].append(index)

# Ausgabe der Facetten-Schemata
for key in dict.keys():
    res = ast.literal_eval(key)
    print(print_ugl(res))
    print(len(dict[key]))


