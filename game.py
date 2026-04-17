import pygame
import math
import random

pygame.init()
info = pygame.display.Info()
LARGEUR, HAUTEUR = info.current_w, info.current_h
SPAWN_X = -140
SPAWN_Y = 945
GRAVITE = 0.4
FORCE_SAUT = -10
VITESSE = 4
FORCE_DASH = 12
DUREE_DASH = 10
GLISSE_MUR = 0.3

TAILLE_JOUEUR = 50
TAILLE_DECHET = 48

DIRECTIONS_DASH = [
    (-1, 0), (1, 0),
    (0, -1), (0, 1),
    (-1, -1), (1, -1),
    (-1, 1), (1, 1)
]

OFFSETS = {
    "long": 45,
    "long_cailloux": 40,
    "long_detruit": 55,
    "moyen": 40,
    "moyen_plante": 40,
    "moyen_trou": 40,
    "court": 30,
}

class Joueur:
    def __init__(self, x, y):
        self.sprites_droite = [
            pygame.transform.scale(
                pygame.image.load(f"Sprite/running_right_{i}.png").convert_alpha(),
                (TAILLE_JOUEUR, TAILLE_JOUEUR)
            )
            for i in range(1, 9)
        ]

        self.sprites_gauche = [
            pygame.transform.scale(
                pygame.image.load(f"Sprite/running_left_{i}.png").convert_alpha(),
                (TAILLE_JOUEUR, TAILLE_JOUEUR)
            )
            for i in range(1, 9)
        ]

        self.stand = pygame.transform.scale(
            pygame.image.load("Sprite/stand.png").convert_alpha(),
            (TAILLE_JOUEUR, TAILLE_JOUEUR)
        )

        self.background = pygame.transform.scale(
            pygame.image.load("Assets/images/Background_jeu.png").convert_alpha(),
            (LARGEUR, HAUTEUR)
        )

        self.frame = 0
        self.timer_animation = 0

        self.rectangle = pygame.Rect(x, y, TAILLE_JOUEUR, TAILLE_JOUEUR)
        self.vitesse_x = 0
        self.vitesse_y = 0

        self.au_sol = False
        self.sur_mur = False
        self.direction_mur = 0
        self.plateforme_support = None

        self.peut_dasher = True
        self.en_dash = False
        self.temps_dash = 0

    def sprite_actuel(self):
        if self.vitesse_x < 0:
            return self.sprites_gauche[self.frame]
        elif self.vitesse_x > 0:
            return self.sprites_droite[self.frame]
        return self.stand

    def gerer_entrees(self):
        touches = pygame.key.get_pressed()

        if not self.en_dash:
            self.vitesse_x = 0

            if touches[pygame.K_LEFT]:
                self.vitesse_x = -VITESSE
            if touches[pygame.K_RIGHT]:
                self.vitesse_x = VITESSE

            if touches[pygame.K_UP]:
                if self.au_sol:
                    self.vitesse_y = FORCE_SAUT
                elif self.sur_mur:
                    self.vitesse_y = FORCE_SAUT
                    self.vitesse_x = -self.direction_mur * VITESSE * 1.5

            if touches[pygame.K_LSHIFT] and self.peut_dasher:
                entree_x = touches[pygame.K_RIGHT] - touches[pygame.K_LEFT]
                entree_y = touches[pygame.K_DOWN] - touches[pygame.K_UP]

                if entree_x == 0 and entree_y == 0:
                    entree_x = 1

                meilleure_direction = None
                meilleur_score = -float("inf")

                for dx, dy in DIRECTIONS_DASH:
                    score = dx * entree_x + dy * entree_y
                    if score > meilleur_score:
                        meilleur_score = score
                        meilleure_direction = (dx, dy)

                norme = math.hypot(meilleure_direction[0], meilleure_direction[1])
                self.vitesse_x = FORCE_DASH * meilleure_direction[0] / norme
                self.vitesse_y = FORCE_DASH * meilleure_direction[1] / norme

                self.en_dash = True
                self.peut_dasher = False
                self.temps_dash = DUREE_DASH

    def deplacement_horizontal(self, plateformes):
        self.rectangle.x += int(self.vitesse_x)
        self.sur_mur = False

        for plateforme in plateformes:
            rect = plateforme["rect"]

            if self.rectangle.colliderect(rect):
                if self.vitesse_x > 0:
                    self.rectangle.right = rect.left
                    self.sur_mur = True
                    self.direction_mur = 1

                elif self.vitesse_x < 0:
                    self.rectangle.left = rect.right
                    self.sur_mur = True
                    self.direction_mur = -1

    def deplacement_vertical(self, plateformes):
        self.rectangle.y += int(self.vitesse_y)
        self.au_sol = False
        self.plateforme_support = None

        for plateforme in plateformes:
            rect = plateforme["rect"]

            if self.rectangle.colliderect(rect):
                if self.vitesse_y >= 0 and self.rectangle.bottom - rect.top < 20:
                    self.rectangle.bottom = rect.top
                    self.vitesse_y = 0
                    self.au_sol = True
                    self.peut_dasher = True
                    self.plateforme_support = plateforme

                elif self.vitesse_y < 0 and rect.bottom - self.rectangle.top < 20:
                    self.rectangle.top = rect.bottom
                    self.vitesse_y = 0

    def animation(self):
        if self.vitesse_x != 0 and self.au_sol:
            self.timer_animation += 1
            if self.timer_animation > 5:
                self.frame = (self.frame + 1) % 8
                self.timer_animation = 0
        else:
            self.frame = 0
            self.timer_animation = 0

    def mettre_a_jour(self, plateformes):
        self.gerer_entrees()

        if self.en_dash:
            self.temps_dash -= 1
            if self.temps_dash <= 0:
                self.en_dash = False

        if not self.en_dash:
            self.vitesse_y += GRAVITE

        self.deplacement_horizontal(plateformes)
        self.deplacement_vertical(plateformes)

        if self.sur_mur and self.vitesse_y > 0:
            self.vitesse_y *= GLISSE_MUR

        self.animation()


class Camera:
    def __init__(self):
        self.decalage_x = 0
        self.decalage_y = 0

    def mettre_a_jour(self, cible):
        self.decalage_x = cible.rectangle.centerx - LARGEUR // 2
        self.decalage_y = cible.rectangle.centery - HAUTEUR // 2


class Jeu:
    def __init__(self, ecran):
        self.ecran = ecran
        self.camera = Camera()
        self.joueur = None

        self.plateformes = []
        self.dechets = []
        self.score = 0

        self.font_score = pygame.font.Font(None, 50)
        self.font_hud = pygame.font.Font(None, 40)
        self.font_big = pygame.font.Font(None, 80)

        self.niveau_index = 0
        self.etat_niveau = "en_cours"
        self.temps_debut_niveau = 0

        self.background_1 = pygame.transform.scale(
            pygame.image.load("Assets/images/background_1.png").convert(),
            (LARGEUR, HAUTEUR)
        )

        self.background_2 = pygame.transform.scale(
            pygame.image.load("Assets/images/background_2.png").convert(),
            (LARGEUR, HAUTEUR)
        )

        self.background_3 = pygame.transform.scale(
            pygame.image.load("Assets/images/background_3.png").convert(),
            (LARGEUR, HAUTEUR)
        )

        self.background_final = pygame.transform.scale(
            pygame.image.load("Assets/images/background_4.png").convert(),
            (LARGEUR, HAUTEUR)
        )
        self.plante_finale = None

        self.img_plante_fin = pygame.transform.scale(
            pygame.image.load("Assets/images/plante.png").convert_alpha(),
            (64, 64)
        )
        facteur = 0.55



        def charge(nom, path):
            img = pygame.image.load(path).convert_alpha()
            w, h = img.get_size()
            img = pygame.transform.scale(img, (int(w * facteur), int(h * facteur)))
            return img, OFFSETS[nom]

        self.img_court, self.oy_court = charge("court", "Assets/images/court.png")
        self.img_long, self.oy_long = charge("long", "Assets/images/Long.png")
        self.img_long_cailloux, self.oy_long_cailloux = charge("long_cailloux", "Assets/images/long_cailloux.png")
        self.img_long_detruit, self.oy_long_detruit = charge("long_detruit", "Assets/images/long_detruit.png")
        self.img_moyen, self.oy_moyen = charge("moyen", "Assets/images/moyen.png")
        self.img_moyen_plante, self.oy_moyen_plante = charge("moyen_plante", "Assets/images/moyen_plante.png")
        self.img_moyen_trou, self.oy_moyen_trou = charge("moyen_trou", "Assets/images/moyen_trou.png")

        self.img_dechet = pygame.transform.scale(
            pygame.image.load("Assets/images/dechet.png").convert_alpha(),
            (TAILLE_DECHET, TAILLE_DECHET)
        )

        self.niveaux = self.creer_niveaux()

    def generer_plante_finale(self):
        self.plante_finale = None

        if self.niveau_index != 9:
            return

        derniere_plateforme = self.plateformes[-1]
        x = derniere_plateforme["rect"].centerx - 32
        y = derniere_plateforme["rect"].top - 64

        self.plante_finale = {
            "rect": pygame.Rect(x, y, 64, 64),
            "image": self.img_plante_fin
        }

    def background_actuel(self):
        niveau = self.niveau_index + 1

        if niveau <= 3:
            return self.background_1
        elif niveau <= 6:
            return self.background_2
        elif niveau <= 9:
            return self.background_3
        return self.background_final

    def creer_niveaux(self):
        return [
            {
                "score_cible": 5,
                "temps_limite": 40,
                "plateformes": [
                    {"x": -200, "y": 950, "type": "long"},
                    {"x": 250, "y": 850, "type": "moyen"},
                    {"x": 650, "y": 760, "type": "moyen"},
                    {"x": 1100, "y": 840, "type": "long"},
                    {"x": 1600, "y": 760, "type": "moyen_plante"},
                    {"x": 2100, "y": 860, "type": "long_detruit"},
                ]
            },
            {
                "score_cible": 5,
                "temps_limite": 40,
                "plateformes": [
                    {"x": -200, "y": 950, "type": "long"},
                    {"x": 240, "y": 820, "type": "court"},
                    {"x": 500, "y": 690, "type": "court"},
                    {"x": 790, "y": 800, "type": "court"},
                    {"x": 1110, "y": 650, "type": "moyen"},
                    {"x": 1500, "y": 810, "type": "long"},
                    {"x": 1960, "y": 690, "type": "moyen_trou"},
                    {"x": 2360, "y": 860, "type": "long_detruit"},
                ]
            },
            {
                "score_cible": 5,
                "temps_limite": 42,
                "plateformes": [
                    {"x": -200, "y": 950, "type": "long"},
                    {"x": 180, "y": 860, "type": "moyen"},
                    {"x": 180, "y": 650, "type": "court"},
                    {"x": 520, "y": 540, "type": "moyen"},
                    {"x": 910, "y": 430, "type": "court"},
                    {"x": 1280, "y": 560, "type": "moyen_plante"},
                    {"x": 1640, "y": 420, "type": "court"},
                    {"x": 2010, "y": 590, "type": "moyen_trou"},
                    {"x": 2410, "y": 760, "type": "long"},
                ]
            },
            {
                "score_cible": 5,
                "temps_limite": 43,
                "plateformes": [
                    {"x": -220, "y": 950, "type": "long"},
                    {"x": 180, "y": 830, "type": "court"},
                    {"x": 460, "y": 730, "type": "moyen"},
                    {"x": 830, "y": 630, "type": "court"},
                    {"x": 1130, "y": 530, "type": "moyen"},
                    {"x": 1500, "y": 620, "type": "court"},
                    {"x": 1800, "y": 760, "type": "moyen_plante"},
                    {"x": 2200, "y": 640, "type": "court"},
                    {"x": 2540, "y": 500, "type": "moyen_trou"},
                    {"x": 2920, "y": 720, "type": "long_detruit"},
                ]
            },
            {
                "score_cible": 5,
                "temps_limite": 45,
                "plateformes": [
                    {"x": -220, "y": 950, "type": "long"},
                    {"x": 220, "y": 840, "type": "moyen", "mobile": True, "axe": "x", "vitesse": 2, "min": 180, "max": 420},
                    {"x": 620, "y": 700, "type": "court"},
                    {"x": 900, "y": 560, "type": "moyen"},
                    {"x": 1280, "y": 470, "type": "court", "mobile": True, "axe": "x", "vitesse": 2, "min": 1240, "max": 1480},
                    {"x": 1660, "y": 620, "type": "moyen_plante"},
                    {"x": 2080, "y": 780, "type": "long_detruit"},
                ]
            },
            {
                "score_cible": 5,
                "temps_limite": 46,
                "plateformes": [
                    {"x": -220, "y": 950, "type": "long"},
                    {"x": 170, "y": 860, "type": "court"},
                    {"x": 420, "y": 760, "type": "court", "mobile": True, "axe": "y", "vitesse": 2, "min": 650, "max": 860},
                    {"x": 760, "y": 620, "type": "moyen"},
                    {"x": 1140, "y": 470, "type": "court", "mobile": True, "axe": "x", "vitesse": 3, "min": 1100, "max": 1360},
                    {"x": 1500, "y": 600, "type": "moyen_trou"},
                    {"x": 1880, "y": 470, "type": "court"},
                    {"x": 2230, "y": 640, "type": "moyen_plante"},
                    {"x": 2630, "y": 830, "type": "long"},
                ]
            },
            {
                "score_cible": 5,
                "temps_limite": 47,
                "plateformes": [
                    {"x": -240, "y": 950, "type": "long"},
                    {"x": 150, "y": 850, "type": "court", "mobile": True, "axe": "x", "vitesse": 2, "min": 120, "max": 320},
                    {"x": 470, "y": 700, "type": "moyen"},
                    {"x": 830, "y": 520, "type": "court", "mobile": True, "axe": "y", "vitesse": 2, "min": 420, "max": 620},
                    {"x": 1180, "y": 670, "type": "court"},
                    {"x": 1480, "y": 500, "type": "moyen"},
                    {"x": 1840, "y": 360, "type": "court", "mobile": True, "axe": "x", "vitesse": 3, "min": 1800, "max": 2060},
                    {"x": 2250, "y": 530, "type": "moyen_trou"},
                    {"x": 2660, "y": 760, "type": "long_detruit"},
                ]
            },
            {
                "score_cible": 5,
                "temps_limite": 48,
                "plateformes": [
                    {"x": -240, "y": 950, "type": "long"},
                    {"x": 140, "y": 860, "type": "moyen"},
                    {"x": 140, "y": 640, "type": "court", "mobile": True, "axe": "y", "vitesse": 2, "min": 540, "max": 820},
                    {"x": 470, "y": 500, "type": "moyen_plante"},
                    {"x": 860, "y": 380, "type": "court"},
                    {"x": 1250, "y": 500, "type": "moyen", "mobile": True, "axe": "x", "vitesse": 3, "min": 1200, "max": 1500},
                    {"x": 1650, "y": 670, "type": "court"},
                    {"x": 1950, "y": 500, "type": "moyen_trou", "mobile": True, "axe": "y", "vitesse": 2, "min": 420, "max": 620},
                    {"x": 2360, "y": 660, "type": "court"},
                    {"x": 2700, "y": 820, "type": "long"},
                ]
            },
            {
                "score_cible": 5,
                "temps_limite": 50,
                "plateformes": [
                    {"x": -260, "y": 950, "type": "long"},
                    {"x": 130, "y": 860, "type": "court"},
                    {"x": 360, "y": 740, "type": "court", "mobile": True, "axe": "x", "vitesse": 3, "min": 300, "max": 540},
                    {"x": 680, "y": 610, "type": "moyen"},
                    {"x": 1060, "y": 460, "type": "court", "mobile": True, "axe": "y", "vitesse": 2, "min": 360, "max": 560},
                    {"x": 1440, "y": 330, "type": "court"},
                    {"x": 1760, "y": 470, "type": "moyen_plante"},
                    {"x": 2120, "y": 620, "type": "court", "mobile": True, "axe": "x", "vitesse": 3, "min": 2060, "max": 2360},
                    {"x": 2490, "y": 470, "type": "moyen_trou"},
                    {"x": 2890, "y": 700, "type": "court"},
                    {"x": 3230, "y": 860, "type": "long_detruit"},
                ]
            },
            {
                "score_cible": 5,
                "temps_limite": 52,
                "plateformes": [
                    {"x": -260, "y": 950, "type": "long"},
                    {"x": 120, "y": 850, "type": "moyen", "mobile": True, "axe": "x", "vitesse": 3, "min": 80, "max": 320},
                    {"x": 470, "y": 700, "type": "court"},
                    {"x": 760, "y": 560, "type": "court", "mobile": True, "axe": "y", "vitesse": 3, "min": 440, "max": 660},
                    {"x": 1120, "y": 420, "type": "moyen"},
                    {"x": 1510, "y": 310, "type": "court", "mobile": True, "axe": "x", "vitesse": 3, "min": 1450, "max": 1710},
                    {"x": 1880, "y": 470, "type": "court"},
                    {"x": 2180, "y": 620, "type": "moyen_trou", "mobile": True, "axe": "y", "vitesse": 2, "min": 500, "max": 720},
                    {"x": 2580, "y": 470, "type": "court"},
                    {"x": 2890, "y": 340, "type": "moyen_plante"},
                    {"x": 3280, "y": 520, "type": "court", "mobile": True, "axe": "x", "vitesse": 4, "min": 3220, "max": 3500},
                    {"x": 3680, "y": 760, "type": "long"},
                ]
            }
        ]

    def image_et_offset(self, nom):
        correspondances = {
            "court": (self.img_court, self.oy_court),
            "long": (self.img_long, self.oy_long),
            "long_cailloux": (self.img_long_cailloux, self.oy_long_cailloux),
            "long_detruit": (self.img_long_detruit, self.oy_long_detruit),
            "moyen": (self.img_moyen, self.oy_moyen),
            "moyen_plante": (self.img_moyen_plante, self.oy_moyen_plante),
            "moyen_trou": (self.img_moyen_trou, self.oy_moyen_trou),
        }
        return correspondances[nom]

    def creer_plateforme(self, x, y, image, offset_y, mobile=False, axe="x", vitesse=0, borne_min=0, borne_max=0):
        rect = pygame.Rect(
            x,
            y + offset_y,
            image.get_width(),
            image.get_height() - offset_y
        )

        return {
            "rect": rect,
            "image": image,
            "offset_y": offset_y,
            "mobile": mobile,
            "axe": axe,
            "vitesse": vitesse,
            "min": borne_min,
            "max": borne_max,
            "delta_x": 0,
            "delta_y": 0
        }

    def creer_dechet(self, x, y):
        rect = pygame.Rect(x, y, TAILLE_DECHET, TAILLE_DECHET)

        return {
            "rect": rect,
            "image": self.img_dechet,
            "points": 1
        }

    def respawn_joueur(self):
        self.joueur = Joueur(SPAWN_X, SPAWN_Y)
        self.camera.mettre_a_jour(self.joueur)

    def charger_plateformes_niveau(self):
        self.plateformes = []
        data = self.niveaux[self.niveau_index]["plateformes"]

        for p in data:
            image, offset_y = self.image_et_offset(p["type"])
            plateforme = self.creer_plateforme(
                p["x"],
                p["y"],
                image,
                offset_y,
                p.get("mobile", False),
                p.get("axe", "x"),
                p.get("vitesse", 0),
                p.get("min", 0),
                p.get("max", 0)
            )
            self.plateformes.append(plateforme)

    def generer_dechets(self):
        self.dechets = []

        plateformes_disponibles = self.plateformes[1:]

        emplacements = []

        for plateforme in plateformes_disponibles:
            rect = plateforme["rect"]
            marge = 20
            largeur_disponible = rect.width - TAILLE_DECHET - 2 * marge
            y = rect.top - TAILLE_DECHET - 10

            if largeur_disponible < 0:
                x = rect.centerx - TAILLE_DECHET // 2
                emplacements.append((x, y, plateforme))
            else:
                nb_slots = max(1, rect.width // (TAILLE_DECHET + 20))
                for i in range(nb_slots):
                    if nb_slots == 1:
                        x = rect.centerx - TAILLE_DECHET // 2
                    else:
                        x = rect.x + marge + i * (largeur_disponible // max(1, nb_slots - 1))
                    emplacements.append((x, y, plateforme))

        derniere_plateforme = self.plateformes[-1]
        emplacements_fin = [e for e in emplacements if e[2] == derniere_plateforme]


        x_fin, y_fin, _ = random.choice(emplacements_fin)
        self.dechets.append(self.creer_dechet(x_fin, y_fin))

        emplacements_restants = [
            e for e in emplacements
            if not (e[0] == x_fin and e[1] == y_fin and e[2] == derniere_plateforme)
        ]
        random.shuffle(emplacements_restants)

        for i in range(4):
            x, y, _ = emplacements_restants[i]
            self.dechets.append(self.creer_dechet(x, y))

    def mettre_a_jour_plateformes(self):
        for p in self.plateformes:
            p["delta_x"] = 0
            p["delta_y"] = 0

            if not p["mobile"]:
                continue

            ancien_x = p["rect"].x
            ancien_y = p["rect"].y

            if p["axe"] == "x":
                p["rect"].x += p["vitesse"]

                if p["rect"].x <= p["min"] or p["rect"].x >= p["max"]:
                    p["vitesse"] *= -1
                    p["rect"].x = max(p["min"], min(p["rect"].x, p["max"]))

            elif p["axe"] == "y":
                p["rect"].y += p["vitesse"]

                if p["rect"].y <= p["min"] or p["rect"].y >= p["max"]:
                    p["vitesse"] *= -1
                    p["rect"].y = max(p["min"], min(p["rect"].y, p["max"]))

            p["delta_x"] = p["rect"].x - ancien_x
            p["delta_y"] = p["rect"].y - ancien_y

    def verifier_collecte_dechets(self):
        dechets_restants = []

        for dechet in self.dechets:
            if self.joueur.rectangle.colliderect(dechet["rect"]):
                self.score += dechet["points"]
            else:
                dechets_restants.append(dechet)

        self.dechets = dechets_restants

    def verifier_plante_finale(self):
        if self.plante_finale is None:
            return

        if self.joueur.rectangle.colliderect(self.plante_finale["rect"]):
            self.plante_finale = None
            self.etat_niveau = "termine"

    def lancer_niveau(self, index):
        self.niveau_index = index
        self.etat_niveau = "en_cours"
        self.score = 0

        self.charger_plateformes_niveau()
        self.joueur = Joueur(SPAWN_X, SPAWN_Y)
        self.generer_dechets()
        self.generer_plante_finale()

        self.camera.mettre_a_jour(self.joueur)
        self.temps_debut_niveau = pygame.time.get_ticks()

    def nouvelle_partie(self):
        self.lancer_niveau(0)

    def temps_restant(self):
        niveau = self.niveaux[self.niveau_index]
        temps_limite_ms = niveau["temps_limite"] * 1000
        temps_ecoule = pygame.time.get_ticks() - self.temps_debut_niveau
        restant_ms = max(0, temps_limite_ms - temps_ecoule)
        return restant_ms // 1000

    def verifier_etat_niveau(self):
        if self.etat_niveau != "en_cours":
            return

        if self.joueur.rectangle.y > 1200:
            self.respawn_joueur()
            return

        if self.niveau_index == 9:
            if self.temps_restant() <= 0:
                self.etat_niveau = "perdu"
            return

        if self.score >= 5:
            self.etat_niveau = "gagne"
        elif self.temps_restant() <= 0:
            self.etat_niveau = "perdu"

    def niveau_suivant(self):
        if self.niveau_index + 1 < len(self.niveaux):
            self.lancer_niveau(self.niveau_index + 1)
        else:
            self.etat_niveau = "termine"

    def mettre_a_jour(self):
        if self.joueur is None:
            return

        if self.etat_niveau == "en_cours":
            self.mettre_a_jour_plateformes()
            self.joueur.mettre_a_jour(self.plateformes)

            support = self.joueur.plateforme_support
            if self.joueur.au_sol and support is not None and support["mobile"]:
                if support["axe"] == "x":
                    self.joueur.rectangle.x += support["delta_x"]
                    self.joueur.rectangle.bottom = support["rect"].top
                elif support["axe"] == "y":
                    self.joueur.rectangle.y += support["delta_y"]
                    self.joueur.rectangle.bottom = support["rect"].top
                    self.joueur.vitesse_y = 0
                    self.joueur.au_sol = True

            self.verifier_collecte_dechets()
            self.verifier_plante_finale()
            self.verifier_etat_niveau()

        self.camera.mettre_a_jour(self.joueur)

    def dessiner_background(self):
        self.ecran.blit(self.background_actuel(), (0, 0))

    def dessiner_plateformes(self):
        for plateforme in self.plateformes:
            image = plateforme["image"]
            rect = plateforme["rect"]
            offset_y = plateforme["offset_y"]

            x_affiche = rect.x - self.camera.decalage_x
            y_affiche = rect.y - offset_y - self.camera.decalage_y
            self.ecran.blit(image, (x_affiche, y_affiche))

    def dessiner_plante_finale(self):
        if self.plante_finale is None:
            return

        x_affiche = self.plante_finale["rect"].x - self.camera.decalage_x
        y_affiche = self.plante_finale["rect"].y - self.camera.decalage_y
        self.ecran.blit(self.plante_finale["image"], (x_affiche, y_affiche))

    def dessiner_dechets(self):
        for dechet in self.dechets:
            x_affiche = dechet["rect"].x - self.camera.decalage_x
            y_affiche = dechet["rect"].y - self.camera.decalage_y
            self.ecran.blit(dechet["image"], (x_affiche, y_affiche))

    def dessiner_joueur(self):
        sprite = self.joueur.sprite_actuel()
        x_affiche = self.joueur.rectangle.x - self.camera.decalage_x
        y_affiche = self.joueur.rectangle.y - self.camera.decalage_y
        self.ecran.blit(sprite, (x_affiche, y_affiche))

    def dessiner_hud(self):
        texte_score = self.font_score.render(f"Score : {self.score}/5", True, (255, 255, 255))
        self.ecran.blit(texte_score, (30, 30))

        texte_temps = self.font_hud.render(
            f"Temps : {self.temps_restant()}s",
            True,
            (255, 255, 255)
        )
        self.ecran.blit(texte_temps, (30, 90))

        texte_niveau = self.font_hud.render(
            f"Niveau : {self.niveau_index + 1}/10",
            True,
            (200, 200, 255)
        )
        self.ecran.blit(texte_niveau, (30, 140))

        texte_dechets = self.font_hud.render(
            f"Déchets restants : {len(self.dechets)}",
            True,
            (180, 255, 180)
        )
        self.ecran.blit(texte_dechets, (30, 190))

    def dessiner_etat_niveau(self):
        if self.etat_niveau == "en_cours":
            return

        overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.ecran.blit(overlay, (0, 0))

        if self.etat_niveau == "gagne":
            texte = "NIVEAU RÉUSSI !"
            couleur = (0, 255, 0)
            sous_texte = "Appuie sur ENTRÉE pour passer au niveau suivant"

        elif self.etat_niveau == "perdu":
            texte = "NIVEAU ÉCHOUÉ..."
            couleur = (255, 60, 60)
            sous_texte = "Appuie sur R pour recommencer le niveau"

        elif self.etat_niveau == "termine":
            texte = "BRAVO !"
            couleur = (255, 215, 0)
            sous_texte = "Tu as terminé les 10 niveaux - Appuie sur ENTRÉE pour recommencer"

        surf = self.font_big.render(texte, True, couleur)
        rect = surf.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 - 50))
        self.ecran.blit(surf, rect)

        surf2 = self.font_hud.render(sous_texte, True, (255, 255, 255))
        rect2 = surf2.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 30))
        self.ecran.blit(surf2, rect2)

    def gerer_evenements_niveau(self, evenement):
        if evenement.type == pygame.KEYDOWN:
            if self.etat_niveau == "gagne":
                if evenement.key == pygame.K_RETURN:
                    self.niveau_suivant()

            elif self.etat_niveau == "perdu":
                if evenement.key == pygame.K_r:
                    self.lancer_niveau(self.niveau_index)

            elif self.etat_niveau == "termine":
                if evenement.key == pygame.K_RETURN:
                    self.lancer_niveau(0)

    def dessiner(self):
        if self.joueur is None:
            return

        self.dessiner_background()
        self.dessiner_plateformes()
        self.dessiner_dechets()
        self.dessiner_joueur()
        self.dessiner_hud()
        self.dessiner_etat_niveau()
        self.dessiner_plante_finale()