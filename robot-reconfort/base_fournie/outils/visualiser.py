#!/usr/bin/env python3
"""outils/visualiser.py — Visualisateur de trace pour le Robot de Réconfort.

Rejoue une trace d'exécution dans le terminal en redessinant la grille
et les informations d'état à chaque pas de temps.

Usage :
    python outils/visualiser.py <carte.json> <trace.json> [delai] [--demande N]

Exemple :
    python outils/visualiser.py cartes/appartement_01.json sorties/trace_01.json
"""

import sys
import os
import time
import json
from pathlib import Path


# Configuration de l'encodage pour Windows PowerShell / CMD
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Activer les séquences ANSI sous Windows
if os.name == "nt":
    os.system("")


def effacer_ecran():
    """Efface l'écran du terminal de manière fluide."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def afficher_cadre(grille_lignes, infos_haut, infos_bas):
    """Affiche une vue complète et propre du monde et de l'état du robot."""
    buffer = []
    buffer.append("=" * 64)
    for info in infos_haut:
        buffer.append(f"  {info}")
    buffer.append("-" * 64)

    for ligne in grille_lignes:
        buffer.append(f"  {ligne}")

    buffer.append("-" * 64)
    for info in infos_bas:
        buffer.append(f"  {info}")
    buffer.append("=" * 64)

    sys.stdout.write("\033[H" + "\n".join(buffer) + "\n")
    sys.stdout.flush()


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)

    chemin_carte = Path(sys.argv[1])
    chemin_trace = Path(sys.argv[2])

    delai = 0.12  # valeur par défaut (environ 20 secondes pour 160 pas)
    demande_cible = None

    args = sys.argv[3:]
    i = 0
    while i < len(args):
        if args[i] == "--demande" and i + 1 < len(args):
            demande_cible = int(args[i + 1])
            i += 2
        else:
            try:
                delai = float(args[i])
            except ValueError:
                pass
            i += 1

    # Chargement des fichiers
    try:
        with open(chemin_carte, "r", encoding="utf-8") as f:
            carte_data = json.load(f)
        with open(chemin_trace, "r", encoding="utf-8") as f:
            trace_data = json.load(f)
    except Exception as e:
        print(f"Erreur de lecture : {e}", file=sys.stderr)
        sys.exit(1)

    dimensions = carte_data["dimensions"]
    H = dimensions["hauteur"]
    L = dimensions["largeur"]
    grille_orig = [list(ligne) for ligne in carte_data["grille"]]

    pos_armoire = tuple(carte_data["armoire"]["position"])
    pos_dico = tuple(carte_data["dictionnaire"]["position"])
    residents_pos = {tuple(r["position"]): r.get("id", "P") for r in carte_data.get("residents", [])}

    pas_liste = trace_data.get("pas", [])
    if demande_cible is not None:
        pas_liste = [p for p in pas_liste if p.get("demande") == demande_cible]

    if not pas_liste:
        print("Aucun pas à afficher dans la trace.")
        sys.exit(0)

    # Dictionnaire des livraisons indexé par numéro de demande
    livraisons_par_demande = {
        liv.get("demande"): liv for liv in trace_data.get("livraisons", [])
    }

    # Simulation visuelle pas à pas
    effacer_ecran()
    print(f"\nPreparation de la visualisation ({len(pas_liste)} pas, delai: {delai}s)...")
    time.sleep(1.0)

    # Suivi de l'objet porté (reconstruit à partir des actions PRENDRE / DONNER)
    objet_porte = None

    total_pas = len(pas_liste)

    for idx, p in enumerate(pas_liste):
        t = p.get("t", idx)
        num_demande = p.get("demande", 1)
        pos_r = tuple(p.get("position", [0, 0]))
        casier = p.get("casier", [0, 0])
        action = p.get("action", "")
        arg = p.get("argument", "")
        arg_str = f" {arg}" if arg is not None else ""
        perception = p.get("perception", {})
        comm = p.get("commentaire")

        # Mise à jour de l'objet porté selon les actions
        livraison_info = livraisons_par_demande.get(num_demande, {})
        if action == "PRENDRE":
            objet_porte = livraison_info.get("objet", "objet")
        elif action == "DONNER":
            objet_porte = None

        # Construction de la grille pour l'affichage
        grille_rendue = []
        for r in range(H):
            ligne_caracteres = []
            for c in range(L):
                char = grille_orig[r][c]

                # Remplacement par symboles lisibles
                if (r, c) == pos_r:
                    # Robot (en surbrillance)
                    ligne_caracteres.append("\033[1;33m[R]\033[0m")
                elif (r, c) == pos_armoire:
                    ligne_caracteres.append("\033[1;36m A \033[0m")
                elif (r, c) == pos_dico:
                    ligne_caracteres.append("\033[1;35m D \033[0m")
                elif (r, c) in residents_pos:
                    rid = residents_pos[(r, c)]
                    ligne_caracteres.append(f"\033[1;32m {rid[:2]}\033[0m")
                elif char == "#":
                    ligne_caracteres.append("\033[90m###\033[0m")
                else:
                    ligne_caracteres.append(" . ")
            grille_rendue.append("".join(ligne_caracteres))

        # Bandeau supérieur
        infos_haut = [
            f"\033[1mROBOT DE RECONFORT\033[0m | Carte: \033[36m{carte_data.get('nom', 'N/A')}\033[0m | Scenario: \033[36m{trace_data.get('scenario', 'N/A')}\033[0m",
            f"Tick: \033[1;33m{t:>3d}\033[0m / {pas_liste[-1].get('t', total_pas):<3d} (Pas {idx+1}/{total_pas}) | Demande: \033[1;32m#{num_demande}\033[0m",
        ]

        # Bandeau inférieur
        perc_str = f"N:{perception.get('N','?')[0]} S:{perception.get('S','?')[0]} E:{perception.get('E','?')[0]} O:{perception.get('O','?')[0]}"
        action_fmt = f"\033[1;37;44m {action}{arg_str} \033[0m"
        objet_str = f"\033[1;32m{objet_porte}\033[0m" if objet_porte else "\033[90m(aucun)\033[0m"
        repli_str = livraison_info.get("repli", "aucun")

        infos_bas = [
            f"Robot: \033[1m[{pos_r[0]}, {pos_r[1]}]\033[0m | Action: {action_fmt} | Selecteur: \033[36m{casier}\033[0m",
            f"Perception locale: {perc_str} | Objet porte: {objet_str} | Repli: \033[33m{repli_str}\033[0m",
        ]

        if comm:
            infos_bas.append(f"Note: \033[3m{comm}\033[0m")

        # Affichage
        afficher_cadre(grille_rendue, infos_haut, infos_bas)
        time.sleep(delai)

    # Écran de fin
    print("\n" + "=" * 64)
    print("  \033[1;32m[OK] FIN DE LA VISUALISATION DE LA TRACE\033[0m")
    print("  Bilan des livraisons :")
    for num, liv in sorted(livraisons_par_demande.items()):
        status = "\033[32mREUSSIE\033[0m" if liv.get("succes") else "\033[31mECHEC\033[0m"
        obj = liv.get("objet") or f"echec ({liv.get('motif_echec')})"
        print(f"    - Demande #{num} ({liv.get('resident')}) : {status} -> {obj} (repli: {liv.get('repli')})")
    print("=" * 64 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nVisualisation interrompue.")
