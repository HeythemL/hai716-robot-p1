# robot/decision.py
# Machine a etats du robot pour une demande.
#
# Ordre des etats par demande (section 4 de l'enonce) :
#   ALLER_DICTIONNAIRE -> CONSULTER -> ALLER_ARMOIRE -> FOUILLER -> PRENDRE
#   -> ALLER_RESIDENT -> DONNER -> DONE
#
# En cas d'echec : etat = ECHEC, motif_echec = "emotion indeterminee" |
#                                               "armoire vide" |
#                                               "resident inaccessible"

from robot import chemin, geometrie, roue
from robot import selecteur as sel_module


class Robot:

    def __init__(self, carte, lecteur, pos_armoire, pos_dictionnaire, residents):
        """
        carte            : CarteMentale
        lecteur          : LecteurEmotion (deja charge)
        pos_armoire      : tuple (l, c)
        pos_dictionnaire : tuple (l, c)
        residents        : dict {id -> (l, c)}
        """
        self.carte    = carte
        self.lecteur  = lecteur
        self.pos_arm  = pos_armoire
        self.pos_dico = pos_dictionnaire
        self.residents = residents

        # ce qu'on a deja vu dans l'armoire : {(l,c) -> objet ou None}
        # persiste entre les demandes (section 4 : l'etat persiste)
        self.casiers_vus = {}

        # champs de la demande en cours (reinitialises par nouvelle_demande)
        self.etat         = "RIEN"
        self.message      = None
        self.resident_id  = None
        self.emotion      = None
        self.intensite    = None
        self.candidats    = []
        self.objet_porte  = None   # conserve jusqu'a la prochaine demande pour la trace
        self.casier_choisi = None
        self.repli        = "aucun"
        self.motif_echec  = None

    # Interface appelee par agent.py

    def nouvelle_demande(self, message, resident_id):
        """Reinitialise l'etat pour une nouvelle demande."""
        self.message      = message
        self.resident_id  = resident_id
        self.emotion      = None
        self.intensite    = None
        self.candidats    = []
        self.objet_porte  = None
        self.casier_choisi = None
        self.repli        = "aucun"
        self.motif_echec  = None
        self.etat         = "ALLER_DICTIONNAIRE"

    def mettre_a_jour(self, position, perception, sel_pos, contenu):
        """Met a jour la carte mentale et la memoire de l'armoire."""
        self.carte.mettre_a_jour(position, perception)
        # si on est adjacent a l'armoire, on enregistre le contenu du casier courant
        if self._adjacent(position, self.pos_arm):
            self.casiers_vus[sel_pos] = contenu  # None = casier vide

    def decider(self, position, sel_pos):
        """Retourne (action, argument) pour ce tick.
        
        On boucle jusqu'a 10 fois pour permettre des transitions d'etat
        sans action (ex: on arrive pres du dico et on consulte tout de suite).
        """
        for _ in range(10):
            result = self._step(position, sel_pos)
            if result is not None:
                return result
        return ("ATTENDRE", None)  # securite

    @property
    def est_termine(self):
        return self.etat in ("DONE", "ECHEC")

    @property
    def est_succes(self):
        return self.etat == "DONE"