# Code-Anlage 2 für die Masterarbeit von Frederic Horn
# Entspricht dem MILP im Abschnitt 6.2.1

# Gurobi wird genutzt, um das gemischt-ganzzahlige lineare Optimierungsproblem zu lösen
import gurobipy as gp
from gurobipy import GRB

# Ordnung der zyklischen Gruppe
g_ord = 7

# Maximale Anzahl der zyklischen Facettenkoeffizienten, die bestimmt werden können
k = 30


# Liste der minimalen Korrekturmultimengen (vorher bestimmt) - muss an die Gruppenordnung und ω angepasst sein!

# m = 3, ω = 2
#L_m_kmm = [[2], [1,1]]

# m = 4, ω = 3
#L_m_kmm = [[3], [2,1], [1,1,1]]

# m = 4, ω = 2
#L_m_kmm = [[2], [1,1], [3,3]]

# m = 5, ω = 4
#L_m_kmm = [[4], [2, 2], [3, 1], [1, 1, 1, 1], [1, 1, 2], [3, 3, 3]]

# m = 7, ω = 6
L_m_kmm = [[6], [1, 5], [2, 4], [3, 3], [1, 1, 4], [1, 2, 3], [2, 2, 2], [3, 5, 5], [4, 4, 5], [1, 1, 1, 3], [1, 1, 2, 2], [1, 4, 4, 4], [5, 5, 5, 5], [1, 1, 1, 1, 2], [4, 4, 4, 4, 4], [1, 1, 1, 1, 1, 1]]



def minimieren(L_m_kmm):
    # Erstelle ein neues Modell
    model = gp.Model("minimieren")

    # Gewichte der k Facettenkoeffizienten
    # Dabei kommt nach k Gewichten immer der zugehörige Wert von ã
    a = model.addVars((g_ord + 1) * k, name="a")

    # {0, 1} - Variablen, die für jedes Paar aus Korrekturmultimenge und Facettenkoeffizienten
    # angeben, ob erstere die zweiteren mit Gleichheit korrigieren
    λ = model.addVars(len(L_m_kmm) * k, vtype=GRB.BINARY, name="λ")

    # Die zu minimierende Variable, die angibt, wie viele
    # nicht-triviale Facettenkoeffizienten in der Lösungsmatrix auftreten
    γ = model.addVars(1, name="γ")

    # Variable, die die nicht-Trivialität der ersten γ Facettenkoeffizienten erzwingt
    z = model.addVars(k, vtype=GRB.BINARY, name="z")

    # Damit wird z[i] > 0 für die ersten γ Facettenkoeffizienten erzwungen
    for i in range(k):
        model.addLConstr(z[i] >= γ[0] / k - i / k)

    # Festlegung von ω, muss mit den Korrekturmultimengen übereinstimmen!
    ω = g_ord - 1

    # Größenbeschränkung der Werte der Facettenkoeffizienten, um numerische Probleme zu vermeiden
    for i in range((g_ord + 1) * k):
        model.addLConstr(a[i] <= 999)

    # Die Facettenkoeffizienten an der Stelle i werden wenigstens auf den Wert z[i] gesetzt
    # Jedoch nicht explizit die Werte von ã[i]
    for l in range(k):
        shift = l * (g_ord + 1)
        model.addLConstr(a[shift + ω] == 0)
        for i in range(g_ord):
            if i == ω: continue
            expr = gp.LinExpr()
            expr += a[shift + i]
            model.addLConstr(expr, GRB.GREATER_EQUAL, z[l])

    # expr erzwingt, dass alle Facettenkoeffizienten korrigierbar sind
    # expr2 erzwingt, dass der entsprechende λ-Wert Null sein muss, wenn nicht mit Gleichheit erfüllt wird
    for l in range(k):
        shift = l * (g_ord + 1)
        shift_kmm = l * len(L_m_kmm)

        for i, kmm in enumerate(L_m_kmm):
            expr = gp.LinExpr()
            expr2 = gp.LinExpr()

            for val in kmm:
                expr += a[shift + (ω - val) % g_ord]
                expr2 -= a[shift + (ω - val) % g_ord]

            expr2 += a[shift + g_ord]

            model.addLConstr(expr, GRB.GREATER_EQUAL, a[shift + g_ord])

            # Ω = 1000 hat sich in der Praxis bewährt
            model.addLConstr(expr2, GRB.GREATER_EQUAL, 1000 * (λ[shift_kmm + i] - 1))

    # Erzwingt, dass jede minimale Korrekturmultimenge wenigstens eines der
    # nicht-trivialen zyklischen Schemata mit Gleichheit korrigiert
    for i in range(len(L_m_kmm)):
        expr = gp.LinExpr()

        for l in range(k):
            expr += λ[l * len(L_m_kmm) + i]

        model.addLConstr(expr, GRB.GREATER_EQUAL, k - γ[0] + 1)

    # Der Wert von γ und die Anzahl der Korrekturen mit Gleichheit sollen minimiert werden
    obj_expr = gp.LinExpr()
    for i in range(len(L_m_kmm)):
        for l in range(k):
            # Beachte, dass 0.0001 < k * |L_m_kmm| für alle betrachteten Fälle
            obj_expr -= 0.0001 * λ[l * len(L_m_kmm) + i]
    obj_expr += γ[0]

    model.setObjective(obj_expr, GRB.MINIMIZE)

    # Optimiert das Modell
    model.optimize()

    # Sobald die Optimierung abgeschlossen ist, wird eine Optimallösung zurückgegeben
    if model.status == GRB.OPTIMAL:
        optimal_λ = [λ[i].x for i in range(len(L_m_kmm) * k)]
        optimal_a = [a[i].x for i in range((g_ord + 1) * k)]
        optimal_γ = [γ[0].x]
        return [optimal_a, optimal_λ, optimal_γ]
    else:
        return None

# Verbesserte Ausgabe der nicht-trivialen Facettenkoeffizienten
def print_a(a):
    for i in range(k):
        if all([a[j] == 0 for j in range(i * (g_ord + 1), (i + 1) * (g_ord + 1))]): continue
        s = ""
        for j in range(g_ord):
            s += str(round(a[i * (g_ord + 1) + j], 2)) + " "
        s += ">= "
        s += str(round(a[i * (g_ord + 1) + g_ord], 2))
        print(s)


[res_a, res_λ, res_γ] = minimieren(L_m_kmm)

print("")
print("")

print_a(res_a)
