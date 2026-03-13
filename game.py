import pygame
import math

LARGEUR, HAUTEUR = 800, 480

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

class Joueur:
    def __init__(self, x, y):
        self.sprites_droite = [
            pygame.transform.scale(
                pygame.image.load(f"Sprite/running_right_{i}.png").convert_alpha(),
                (50, 50)
            )
            for i in range(1, 9)
        ]
        self.stand = pygame.transform.scale(pygame.image.load(f"Sprite/stand.png").convert_alpha(),(50,50))
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

        for plateforme in plateformes:
            if self.rectangle.colliderect(plateforme):
                if self.vitesse_x > 0:
                    self.rectangle.right = plateforme.left
                    self.sur_mur = True
                    self.direction_mur = 1
                elif self.vitesse_x < 0:
                    self.rectangle.left = plateforme.right
                    self.sur_mur = True
                    self.direction_mur = -1

        self.rectangle.y += self.vitesse_y
        self.au_sol = False

        for plateforme in plateformes:
            if self.rectangle.colliderect(plateforme):
                if self.vitesse_y > 0:
                    self.rectangle.bottom = plateforme.top
                    self.vitesse_y = 0
                    self.au_sol = True
                    self.peut_dasher = True
                elif self.vitesse_y < 0:
                    self.rectangle.top = plateforme.bottom
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

    def nouvelle_partie(self):
        self.joueur = Joueur(100, 300)
        self.plateformes = [
            pygame.Rect(0, 420, 8000, 60),

            pygame.Rect(200, 360, 120, 180),
            pygame.Rect(350, 320, 120, 20),
            pygame.Rect(500, 80, 120, 20),
            pygame.Rect(650, 240, 120, 20),
            pygame.Rect(820, 30, 120, 180),
            pygame.Rect(980, 60, 120, 20),
            pygame.Rect(1150, 220, 120, 20),
            pygame.Rect(1320, 280, 120, 20),
            pygame.Rect(1480, 340, 120, 20),
            pygame.Rect(1650, 300, 120, 180),
            pygame.Rect(1820, 260, 120, 20),
            pygame.Rect(2000, 20, 120, 20),
            pygame.Rect(2170, 180, 120, 20),
            pygame.Rect(2350, 240, 120, 180),
            pygame.Rect(2520, 300, 120, 20),
            pygame.Rect(2700, 260, 120, 20),
            pygame.Rect(2880, 220, 120, 20),

            pygame.Rect(3100, 35, 120, 180),
            pygame.Rect(3250, 310, 120, 20),
            pygame.Rect(3400, 70, 120, 20),
            pygame.Rect(3550, 230, 120, 20),

            pygame.Rect(1000, 260, 20, 200),
            pygame.Rect(1120, 260, 20, 200),
            pygame.Rect(1000, 260, 120, 20),

            pygame.Rect(3700, 300, 120, 20),
            pygame.Rect(3850, 250, 120, 20),
            pygame.Rect(4000, 200, 120, 20),
        ]

    def mettre_a_jour(self):
        self.joueur.mettre_a_jour(self.plateformes)
        self.camera.mettre_a_jour(self.joueur)

    def dessiner(self):
        self.ecran.fill((15, 15, 30))

        for plateforme in self.plateformes:
            pygame.draw.rect(
                self.ecran,
                (90, 90, 120),
                pygame.Rect(
                    plateforme.x - self.camera.decalage_x,
                    plateforme.y - self.camera.decalage_y,
                    plateforme.width,
                    plateforme.height
                )
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
