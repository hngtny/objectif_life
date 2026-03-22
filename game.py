import pygame
import math

LARGEUR, HAUTEUR = 1920, 1080

GRAVITE = 0.4
FORCE_SAUT = -10
VITESSE = 4
FORCE_DASH = 12
DUREE_DASH = 10
GLISSE_MUR = 0.3

DIRECTIONS_DASH = [
    (-1, 0), (1, 0),
    (0, -1), (0, 1),
    (-1, -1), (1, -1),
    (-1, 1), (1, 1)
]

OFFSETS = {
    "Long":           40,
    "long_cailloux":  40,
    "long_detruit":   55,
    "moyen":          40,
    "moyen_plante":   40,
    "moyen_trou":     40,
    "cailloux":       40,
    "court":          30,
}

class Joueur:
    def __init__(self, x, y):
        self.sprites_droite = [
            pygame.transform.scale(
                pygame.image.load(f"Sprite/running_right_{i}.png").convert_alpha(),
                (50, 50)
            )
            for i in range(1, 9)
        ]
        self.stand = pygame.transform.scale(
            pygame.image.load("Sprite/stand.png").convert_alpha(),
            (50, 50)
        )
        self.sprites_gauche = [
            pygame.transform.scale(
                pygame.image.load(f"Sprite/running_left_{i}.png").convert_alpha(),
                (50, 50)
            )
            for i in range(1, 9)
        ]
        self.frame = 0
        self.timer_animation = 0
        self.rectangle = pygame.Rect(x, y, 50, 50)
        self.vitesse_x = 0
        self.vitesse_y = 0
        self.au_sol = False
        self.sur_mur = False
        self.direction_mur = 0
        self.peut_dasher = True
        self.en_dash = False
        self.temps_dash = 0
        self.background = pygame.transform.scale(
            pygame.image.load("Assets/images/Background_jeu.png").convert_alpha(),
            (LARGEUR, HAUTEUR)
        )

    def mettre_a_jour(self, plateformes):
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
                meilleur_score = -1

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

        if self.en_dash:
            self.temps_dash -= 1
            if self.temps_dash <= 0:
                self.en_dash = False

        if not self.en_dash:
            self.vitesse_y += GRAVITE

        self.rectangle.x += self.vitesse_x
        self.sur_mur = False

        for p in plateformes:
            rect = p["rect"]
            if self.rectangle.colliderect(rect):
                if self.vitesse_x > 0:
                    self.rectangle.right = rect.left
                    self.sur_mur = True
                    self.direction_mur = 1
                elif self.vitesse_x < 0:
                    self.rectangle.left = rect.right
                    self.sur_mur = True
                    self.direction_mur = -1

        self.rectangle.y += self.vitesse_y
        self.au_sol = False

        for p in plateformes:
            rect = p["rect"]
            if self.rectangle.colliderect(rect):
                if self.vitesse_y > 0:
                    self.rectangle.bottom = rect.top
                    self.vitesse_y = 0
                    self.au_sol = True
                    self.peut_dasher = True
                elif self.vitesse_y < 0:
                    self.rectangle.top = rect.bottom
                    self.vitesse_y = 0

        if self.sur_mur and self.vitesse_y > 0:
            self.vitesse_y *= GLISSE_MUR

        if self.vitesse_x != 0:
            self.timer_animation += 1
            if self.timer_animation > 5:
                self.frame = (self.frame + 1) % 8
                self.timer_animation = 0
        else:
            self.frame = 0


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

        facteur = 0.5

        def charge(nom):
            img = pygame.image.load(f"Assets/images/{nom}.png").convert_alpha()
            w, h = img.get_size()
            img = pygame.transform.scale(img, (int(w * facteur), int(h * facteur)))
            return img, OFFSETS[nom]

        self.img_cailloux,       self.off_cailloux       = charge("cailloux")
        self.img_court,          self.off_court          = charge("court")
        self.img_long,           self.off_long           = charge("Long")
        self.img_long_cailloux,  self.off_long_cailloux  = charge("long_cailloux")
        self.img_long_detruit,   self.off_long_detruit   = charge("long_detruit")
        self.img_moyen,          self.off_moyen          = charge("moyen")
        self.img_moyen_plante,   self.off_moyen_plante   = charge("moyen_plante")
        self.img_moyen_trou,     self.off_moyen_trou     = charge("moyen_trou")

    def creer_plateforme(self, x, y, image, offset_y):
        rect = image.get_rect(topleft=(x, y + offset_y))
        return {"rect": rect, "image": image, "offset_y": offset_y}

    def nouvelle_partie(self):
        self.joueur = Joueur(100, 350)
        self.plateformes = []

        self.plateformes.append(self.creer_plateforme(0,    420, self.img_long,           self.off_long))
        self.plateformes.append(self.creer_plateforme(200,  360, self.img_moyen,          self.off_moyen))
        self.plateformes.append(self.creer_plateforme(350,  320, self.img_court,          self.off_court))
        self.plateformes.append(self.creer_plateforme(650,  240, self.img_moyen_plante,   self.off_moyen_plante))
        self.plateformes.append(self.creer_plateforme(820,  30,  self.img_long_cailloux,  self.off_long_cailloux))
        self.plateformes.append(self.creer_plateforme(1150, 220, self.img_moyen_trou,     self.off_moyen_trou))
        self.plateformes.append(self.creer_plateforme(1320, 280, self.img_moyen,          self.off_moyen))
        self.plateformes.append(self.creer_plateforme(1480, 340, self.img_court,          self.off_court))
        self.plateformes.append(self.creer_plateforme(1650, 300, self.img_long_detruit,   self.off_long_detruit))
        self.plateformes.append(self.creer_plateforme(1820, 260, self.img_court,          self.off_court))
        self.plateformes.append(self.creer_plateforme(2170, 180, self.img_moyen,          self.off_moyen))
        self.plateformes.append(self.creer_plateforme(2520, 300, self.img_court,          self.off_court))
        self.plateformes.append(self.creer_plateforme(2700, 260, self.img_moyen_plante,   self.off_moyen_plante))
        self.plateformes.append(self.creer_plateforme(2880, 220, self.img_moyen_trou,     self.off_moyen_trou))
        self.plateformes.append(self.creer_plateforme(3100, 35,  self.img_long,           self.off_long))
        self.plateformes.append(self.creer_plateforme(3250, 310, self.img_court,          self.off_court))
        self.plateformes.append(self.creer_plateforme(3550, 230, self.img_moyen,          self.off_moyen))
        self.plateformes.append(self.creer_plateforme(1000, 260, self.img_cailloux,       self.off_cailloux))
        self.plateformes.append(self.creer_plateforme(1120, 260, self.img_cailloux,       self.off_cailloux))
        self.plateformes.append(self.creer_plateforme(1000, 260, self.img_moyen,          self.off_moyen))
        self.plateformes.append(self.creer_plateforme(3700, 300, self.img_moyen,          self.off_moyen))
        self.plateformes.append(self.creer_plateforme(3850, 250, self.img_court,          self.off_court))

    def mettre_a_jour(self):
        self.joueur.mettre_a_jour(self.plateformes)
        self.camera.mettre_a_jour(self.joueur)

    def dessiner(self):
        self.ecran.blit(self.joueur.background, (0, 0))

        for p in self.plateformes:
            rect = p["rect"]
            image = p["image"]
            self.ecran.blit(
                image,
                (rect.x - self.camera.decalage_x,
                 rect.y - self.camera.decalage_y - p["offset_y"])
            )
            pygame.draw.rect(
                self.ecran,
                (255, 0, 0),
                pygame.Rect(
                    rect.x - self.camera.decalage_x,
                    rect.y - self.camera.decalage_y,
                    rect.width,
                    rect.height
                ),
                2
            )

        if self.joueur.vitesse_x < 0:
            sprite = self.joueur.sprites_gauche[self.joueur.frame]
        elif self.joueur.vitesse_x > 0:
            sprite = self.joueur.sprites_droite[self.joueur.frame]
        else:
            sprite = self.joueur.stand

        self.ecran.blit(
            sprite,
            (
                self.joueur.rectangle.x - self.camera.decalage_x,
                self.joueur.rectangle.y - self.camera.decalage_y
            )
        )
