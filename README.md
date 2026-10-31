# HAI716 — Projet Agent : Le Robot de Réconfort

> **Projet de semestre — Master Informatique (POA / SMA)**  
> **Équipe :** LAOUICI Heythem & MOKADDEM Sara  
> **Langage :** Python 3 (aucune dépendance externe requise)

Un agent autonome à perception locale navigue dans un appartement modélisé sous forme de grille, consulte un dictionnaire pour identifier l'émotion d'un message transmis par un résident, explore une armoire selon la roue des émotions de Plutchik, et livre l'objet de réconfort approprié.

L'énoncé complet du projet est disponible dans [`ENONCE.pdf`](ENONCE.pdf).

---

## Sommaire

- [Installation & Prérequis](#installation--prérequis)
- [Commandes d'exécution (Usage)](#commandes-dexécution-usage)
  - [Format de la commande](#format-de-la-commande)
  - [Exécution des scénarios (1 à 5)](#exécution-des-scénarios-1-à-5)
  - [Validation des entrées & Codes de retour](#validation-des-entrées--codes-de-retour)
- [Visualiser l'exécution de la trace](#visualiser-lexécution-de-la-trace)
  - [Options du visualisateur](#options-du-visualisateur)
  - [Exemples d'utilisation du visualisateur](#exemples-dutilisation-du-visualisateur)
- [Structure du projet](#structure-du-projet)
- [Règles et contraintes du sujet](#règles-et-contraintes-du-sujet)

---

## Installation & Prérequis

- **Python 3.9+** (avec la bibliothèque standard uniquement).
- Se placer dans le répertoire du projet avant d'exécuter les scripts :

```bash
cd robot-reconfort/base_fournie
```

---

## Commandes d'exécution (Usage)

### Format de la commande

L'agent respecte le contrat d'appel standard (section 2 de l'énoncé) :

```bash
python agent.py <carte.json> <scenario.json> <dossier_donnees> <trace_sortie.json>
```

- `<carte.json>` : Fichier décrivant les dimensions, le départ du robot, les résidents, l'armoire et le dictionnaire.
- `<scenario.json>` : Fichier listant les demandes des résidents (numéro, résident cible, message).
- `<dossier_donnees>` : Dossier contenant `dictionnaire.json` et `armoire.json`.
- `<trace_sortie.json>` : Fichier JSON où sera enregistrée la trace complète d'exécution.

---

### Exécution des scénarios (1 à 5)

Les cartes et scénarios fournis se trouvent dans le sous-dossier `cartes/` :

```bash
# Scénario 1 (Appartement 1)
python agent.py cartes/appartement_01.json cartes/scenario_01.json donnees sorties/trace_01.json

# Scénario 2 (Appartement 2)
python agent.py cartes/appartement_02.json cartes/scenario_02.json donnees sorties/trace_02.json

# Scénario 3 (Appartement 3)
python agent.py cartes/appartement_03.json cartes/scenario_03.json donnees sorties/trace_03.json

# Scénario 4 (Appartement 4)
python agent.py cartes/appartement_04.json cartes/scenario_04.json donnees sorties/trace_04.json

# Scénario 5 (Appartement 5)
python agent.py cartes/appartement_05.json cartes/scenario_05.json donnees sorties/trace_05.json
```

---

### Validation des entrées & Codes de retour

L'agent implémente une validation rigoureuse des arguments et des fichiers JSON d'entrée (section 5.6 de l'énoncé) :

- **Code 0** : Exécution terminée avec succès (la trace est générée).
- **Code 1** : Fichier absent, mal formé ou incohérent (message clair affiché sur `stderr`, aucune trace produite).
- **Code 2** : Arguments de ligne de commande incorrects ou manquants (affiche le message d'usage).

---

## Visualiser l'exécution de la trace

Un visualisateur interactif en terminal (`outils/visualiser.py`) permet de rejouer le déplacement du robot pas à pas, d'observer sa mémoire de la carte, la position du sélecteur d'armoire et les actions exécutées.

### Format de la commande

```bash
python outils/visualiser.py <carte.json> <trace.json> [delai] [--demande N]
```

### Options du visualisateur

| Paramètre / Option | Rôle | Valeur par défaut |
|---|---|---|
| `<carte.json>` | Fichier de la carte correspondant à la trace | *Obligatoire* |
| `<trace.json>` | Trace générée par `agent.py` | *Obligatoire* |
| `[delai]` | Vitesse d'animation en secondes par pas | `0.12` |
| `--demande N` | Visualiser uniquement la demande numéro `N` | Toutes les demandes |

### Exemples d'utilisation du visualisateur

```bash
# 1. Visualiser toute la trace du scénario 01 à vitesse normale (0.12s)
python outils/visualiser.py cartes/appartement_01.json sorties/trace_01.json

# 2. Visualiser plus rapidement (0.04s par pas)
python outils/visualiser.py cartes/appartement_01.json sorties/trace_01.json 0.04

# 3. Visualiser plus lentement pour observer en détail (0.3s par pas)
python outils/visualiser.py cartes/appartement_01.json sorties/trace_01.json 0.3

# 4. Visualiser uniquement la demande numéro 2
python outils/visualiser.py cartes/appartement_01.json sorties/trace_01.json --demande 2

# 5. Combiner vitesse rapide et demande spécifique
python outils/visualiser.py cartes/appartement_01.json sorties/trace_01.json 0.05 --demande 3
```

---

## Structure du projet

```text
robot-reconfort/base_fournie/
├── agent.py                 # Point d'entrée principal (boucle décisionnelle, CLI)
├── reconfort_io.py          # Chargement des entrées et écriture de trace conforme
├── validation.py            # Validation robuste des schémas et cohérence des entrées
├── rendu.json               # Métadonnées de l'équipe et commande de rendu
├── cartes/                  # Cartes (appartement_01 à 05) et scénarios associés
├── donnees/                 # armoire.json et dictionnaire.json
├── sorties/                 # Fichiers de trace JSON générés
├── outils/
│   └── visualiser.py        # Visualisateur dynamique de trace en terminal
└── robot/
    ├── memoire.py           # Carte mentale et mémorisation des découvertes
    ├── lecture_emotion.py   # Analyse du message et identification des émotions
    ├── roue.py              # Roue de Plutchik et stratégie de repli
    ├── selecteur.py         # Déplacements du sélecteur d'armoire
    ├── action.py            # Exécution et log des actions
    ├── geometrie.py         # Repère, distances de Manhattan et adjacences
    └── decision.py          # Machine à états finis du robot et planification BFS
```

---

## Règles et contraintes du sujet

1. **Aucune triche sur l'environnement :**
   - Le robot ne lit **jamais** `carte["grille"]` à l'avance : il découvre les murs case par case via son capteur local (`percevoir`).
   - Le robot ne lit **jamais** le champ `"objet"` des casiers à l'avance : il découvre les objets uniquement lorsqu'il amène le sélecteur devant le casier.
2. **Navigation optimale :** Recherche du plus court chemin par parcours en largeur (BFS) sur la carte mentale actualisée en temps réel.
3. **Gestion des replis :** Application conforme des règles de repli de Plutchik en cas de casier vide dans l'armoire.
