# Code-Anlage 5 für die Masterarbeit von Frederic Horn
# Betrachten vieler Beispiele für die Gruppe der Ordnung 5

import random
import gurobipy as gp
from gurobipy import GRB
import itertools

ordnung = 5
anz_bsp = 10

# Generiert zufällige Abbildung [n] -> G, die nicht 0 als Komponentensumme hat
def generiere_zufaelliges_nicht_ct(n):
    array = [random.randint(0, ordnung - 1) for _ in range(n - 1)]

    # 4 als Summe fest, für übersichtlichere Ausgabe. Kann verändert werden, muss jedoch mit kmm unten übereinstimmen.
    letzter_eintrag = (4 - (sum(array) % ordnung)) % ordnung
    array.append(letzter_eintrag)

    return array

# Generiert eine zufällige Richtung für ein gegebenes nicht-CT
def generiere_zufaelliges_c(nicht_ct):
    n = len(nicht_ct)
    c = []

    for i in range(n):
        for _ in range(ordnung):
            c.append(0 if _ == nicht_ct[i] else random.randint(1, 80) / 10)

    return c

# Berechne xi als c-minimierenden Inzidenzvektor üer allen Z_5-zyklischen Transversalen
def berechne_xi(c, nicht_ct):
    s = sum(nicht_ct) % ordnung
    n = len(nicht_ct)
    
    # Minimale Korrekturmenge (mit Nullen) 
    kmm = [
        ([0] * (n - 4)) + ([k_te_wurzel_aus_n(4, s)] * 4),
        ([0] * (n - 3)) + ([k_te_wurzel_aus_n(3, s)] * 3),
        ([0] * (n - 2)) + ([k_te_wurzel_aus_n(2, s)] * 2),
        ([0] * (n - 1)) + ([s]),
        ([0] * (n - 3)) + (
        [k_te_wurzel_aus_n(2, s), k_te_wurzel_aus_n(4, s), k_te_wurzel_aus_n(4, s)]),
        ([0] * (n - 2)) + ([k_te_wurzel_aus_n(3, s), k_te_wurzel_aus_n(4, s)])
    ]
    
    # Reihenfolge ist jetzt wichtig
    kor_vektoren = []
    for mm in kmm:
        kor_vektoren.extend(list(list(_) for _ in list(itertools.permutations(mm))))

    kor_vektoren = list(filter(lambda cor: len(cor) <= n, kor_vektoren))

    bester_wert = 100000000
    bester_kor_vek = []
    
    for kor in kor_vektoren:
        aktueller_wert = 0
        for i in range(len(nicht_ct)):
            aktueller_wert += c[ordnung * i + ((nicht_ct[i] - kor[i]) % 5)]
        if aktueller_wert < bester_wert:
            bester_wert = aktueller_wert
            bester_kor_vek = kor

    xi = []
    for i in range(len(nicht_ct)):
        for j in range(5):
            xi.append(1 if j == (nicht_ct[i] - bester_kor_vek[i]) % 5 else 0)

    return [bester_kor_vek, xi]

# Berechnet i, sodass i*k=n im zyklischen Ring über Z_5
# Möglich für 1<=k<=5, da jedes nicht-Null Element in Z_5 ein Erzeuger ist
def k_te_wurzel_aus_n(k, n):
    for i in range(1, ordnung):
        if i * k % ordnung == n:
            return i

# Generiere rekursiv alle nicht-zyklischen Transversale
def generiere_all_nicht_ct(n, aktuelles_array=[]):
    if len(aktuelles_array) == n:
        if sum(aktuelles_array) % ordnung != 0:
            return [aktuelles_array]
        else:
            return []

    arrays = []
    for i in range(ordnung):
        neues_array = aktuelles_array + [i]
        arrays.extend(generiere_all_nicht_ct(n, neues_array))

    return arrays

# Generiere eine Liste aller hypothetischen Facetten - die Vollständigkeit dieser wird geprüft.
def generiere_alle_facetten(n):
    nicht_ct_liste = generiere_all_nicht_ct(n)
    facetten_liste = []

    for nicht_ct in nicht_ct_liste:
        xi_star = sum(nicht_ct) % ordnung
        facette_typ_1 = []
        facette_typ_2 = []
        for i in range(n):
            for j in range(ordnung):
                if j == nicht_ct[i]:
                    facette_typ_1.append(0)
                    facette_typ_2.append(0)
                elif j == (nicht_ct[i] - xi_star) % ordnung:
                    facette_typ_1.append(4)
                    facette_typ_2.append(6)
                elif ((nicht_ct[i] - j) * 2) % ordnung == xi_star:
                    facette_typ_1.append(2)
                    facette_typ_2.append(3)
                elif ((nicht_ct[i] - j) * 3) % ordnung == xi_star:
                    facette_typ_1.append(3)
                    facette_typ_2.append(2)
                elif ((nicht_ct[i] - j) * 4) % ordnung == xi_star:
                    facette_typ_1.append(1)
                    facette_typ_2.append(4)

        facetten_liste.append(facette_typ_1)
        facetten_liste.append(facette_typ_2)

    return (facetten_liste)

# Berechne das Skalarprodukt zweier Vektoren
def skalar_produkt(liste1, liste2):
    if len(liste1) != len(liste2):
        raise ValueError("Listen müssen die gleiche Länge haben!")

    return sum(x * y for x, y in zip(liste1, liste2))

# Prüfe, ob xi eine facettendefinierende Ungleichung mit Gleichheit erfüllt
def pruefe_facette_xi(facette, xi, rhs):
    return skalar_produkt(facette, xi) == rhs

# Filtere die Facetten-Liste, sodass nur noch die übrig bleiben, die von xi mit Gleichheit erfüllt werden
def pruef_gleichheit(facetten_liste, xi):
    gueltige_facetten_liste = []
    for facette in facetten_liste:
        if pruefe_facette_xi(facette, xi, max(facette)):
            gueltige_facetten_liste.append(facette)
    return gueltige_facetten_liste

# Ergänze die Facettenliste um die Nicht-Negativitäts-Ungleichungen und die Block-Gleichungen
def ergaenze_facetten(n, gueltige_facetten, xi):
    alle_gueltigen_ugl = gueltige_facetten

    # Block-Gleichungen werden als zwei Block-Ungleichungen modelliert
    for i in range(n):
        pos_block = []
        neg_block = []
        zer = [0] * ordnung
        pl = [1] * ordnung
        mi = [-1] * ordnung
        pos_block.extend(zer * i)
        pos_block.extend(pl)
        pos_block.extend(zer * (n - 1 - i))
        neg_block.extend(zer * i)
        neg_block.extend(mi)
        neg_block.extend(zer * (n - 1 - i))
        alle_gueltigen_ugl.append(pos_block)
        alle_gueltigen_ugl.append(neg_block)

    # Nicht-Negativitäts-Ungleichungen
    for i in range(len(xi)):
        if xi[i] == 0:
            l1 = [0] * i
            l1.extend([1])
            l1.extend([0] * (ordnung * n - i - 1))
            alle_gueltigen_ugl.append(l1)

    return (alle_gueltigen_ugl)


def minimiere_differenz(c, ugls):
    n = len(c)
    m = len(ugls)

    modell = gp.Model("minimiere_differenz")

    # Die Linearkombination von mit Gleichheit erfüllten Ungleichungen mit nichtnegativen Koeffizienten
    a = modell.addVars(n, name="a")

    # Koeffizienten der Linearkombination
    λ = modell.addVars(len(ugls), name="λ")

    # Binärvariablen, die angeben, ob die Ungleichung sogar mit positivem Koeffizienten eingeflossen ist
    λ_bin = modell.addVars(m, vtype=GRB.BINARY, name="λ_bin")

    for j in range(m):
        modell.addConstr(λ[j] <= 100 * λ_bin[j])

    # Summe der Fehlerquadrate in den Komponenten der Differenz c-a wird minimiert
    obj_expr = sum((c[i] - a[i]) * (c[i] - a[i]) for i in range(n))
    modell.setObjective(obj_expr, GRB.MINIMIZE)

    # Anzahl der echt positiven Koeffizienten wird beschränkt, um keine Nullsummen bei den
    # Block-Ungleichungen zuzulassen und um infinitesimale Beiträge zu minimieren
    modell.addConstr(sum(λ_bin[j] for j in range(m)) <= 16)

    # a = Linearkombination
    for column in range(n):
        expr = gp.LinExpr()
        for i in range(len(ugls)):
            expr += ugls[i][column] * λ[i]
        modell.addConstr(expr, GRB.EQUAL, a[column])

    # Nicht-Negativität der Koeffizienten
    for i in range(len(ugls)):
        expr = gp.LinExpr()
        expr += λ[i]
        modell.addConstr(expr, GRB.GREATER_EQUAL, 0)

    modell.optimize()

    if modell.status == GRB.OPTIMAL:
        optimal_λ = [λ[i].x for i in range(len(ugls))]
        return optimal_λ
    else:
        return None

# Länge des Vektors
n = 4

# Ausgabe als LaTeX-Code
def print_data_point(data_point):
    print("-----------------------------------\n")
    print("\(\\text{nicht-CT } = " + str(data_point[1]) + "\)\n")
    print("\(c = " + str(data_point[2]) + "\)\n")
    print("\(\\xi = " + str(data_point[3]) + "\)\n")
    print("\(\\text{Abweichung } = " + str(data_point[5]) + "\)\n")
    print("\\begin{itemize}\n")

    for i in range(len(data_point[4])):
        s = "\\item \(" + str(data_point[4][i][0]) + "x "
        if data_point[4][i][1].count(0) <= n:
            s += "\\geq " + str(max(data_point[4][i][1])) + " \\text{ for } ["
            pos_0_1 = data_point[4][i][1].index(0)
            pos_0_2 = data_point[4][i][1].index(0, pos_0_1 + 1)
            pos_0_3 = data_point[4][i][1].index(0, pos_0_2 + 1)
            s += str(pos_0_1 % ordnung) + ", "
            s += str(pos_0_2 % ordnung) + ", "
            s += str(pos_0_3 % ordnung) + "]"

        elif data_point[4][i][1].count(0) >= len(data_point[4][i][1]) - 2:
            pos_1 = data_point[4][i][1].index(1)
            s += "\\geq 1" + " \\text{ im Block } " + str(pos_1 // ordnung) + " \\text{ an } " + str(
                pos_1 % ordnung)

        else:
            val = data_point[4][i][1][-1]
            pos_1 = data_point[4][i][1].index(val) + 1
            s += "= " + str(val) + " \\text{ im blocK } " + str(pos_1 // ordnung)

        s += "\)" + "\n"

        print(s)

    print("\\end{itemize}\n")
    print("\[\]")

# Für eine übersichtliche Ausgabe
kmm = [[4], [2, 2], [3, 1], [1, 1, 1, 1], [1, 1, 2], [3, 3, 3]]
#kmm = [[3], [4, 4], [1, 2], [2, 2, 2, 2], [2, 2, 4], [1, 1, 1]]
#kmm = [[2], [1, 1], [4, 3], [3, 3, 3, 3], [3, 3, 1], [4, 4, 4]]
#kmm = [[1], [3, 3], [2, 4], [4, 4, 4, 4], [4, 4, 3], [2, 2, 2]]

def istAinB(A_or, B_or):
    A = A_or[:]
    B = B_or[:]
    if len(A) == 0:
        return True
    if len(A) > len(B):
        return False
    if A[0] in B:
        el = A[0]
        A.remove(el)
        B.remove(el)
        return istAinB(A, B)
    else:
        return False


def print_data(data):
    for mm in kmm:
        print("\subsection{" + str(mm) + "}\n")
        for data_point in list(filter(lambda l: istAinB(mm, l[0]), data)):
            print_data_point(data_point)

# Ausführung
data = []

for ex in range(anz_bsp):

    dataPoint = []

    nicht_ct = generiere_zufaelliges_nicht_ct(n)
    c = generiere_zufaelliges_c(nicht_ct)

    [korV, xi] = berechne_xi(c, nicht_ct)
    fac_liste = generiere_alle_facetten(n)
    gueltige_ugl = pruef_gleichheit(fac_liste, xi)
    alle_gueltige_ugl = ergaenze_facetten(n, gueltige_ugl, xi)

    dataPoint.append(korV)
    dataPoint.append(nicht_ct)
    dataPoint.append(c)
    dataPoint.append(xi)

    res = minimiere_differenz(c, alle_gueltige_ugl)

    ugl_liste = []

    a = [0] * (ordnung * n)
    for i in range(len(res)):
        gerundet = round(res[i], 4)
        if gerundet > 0:
            ugl_liste.append([gerundet, alle_gueltige_ugl[i]])

            for j in range(len(a)):
                a[j] += gerundet * alle_gueltige_ugl[i][j]

    dataPoint.append(ugl_liste)

    abweichung = 0
    for j in range(len(a)):
        abweichung += (a[j] - c[j]) ** 2

    dataPoint.append(abweichung)

    data.append(dataPoint)

print("")
print("")
print("")
print("")
print("")
print("")
print("")
print("")
print("")
print("")
print("")
print_data(data)