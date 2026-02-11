import pygame
import math

pygame.init()

LARGEUR, HAUTEUR = 800, 480
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
horloge = pygame.time.Clock()

logo = pygame.image.load('Images/objectif life logo.png')
pygame.display.set_icon(logo)
pygame.display.set_caption('Objectif Life')

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
        self.rectangle = pygame.Rect(x, y, 32, 32)
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
        if touches[pygame.K_ESCAPE]:
            pygame.quit()
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

class Camera:
    def __init__(self):
        self.decalage_x = 0
        self.decalage_y = 0

    def mettre_a_jour(self, cible):
        self.decalage_x = cible.rectangle.centerx - LARGEUR // 2
        self.decalage_y = cible.rectangle.centery - HAUTEUR // 2

joueur = Joueur(100, 300)

plateformes = [
    pygame.Rect(0, 420, 2000, 60),
    pygame.Rect(300, 340, 120, 20),
    pygame.Rect(550, 280, 120, 20),
    pygame.Rect(800, 220, 120, 20),
    pygame.Rect(1000, 260, 20, 200),
    pygame.Rect(1120, 260, 20, 200),
    pygame.Rect(1000, 260, 120, 20)
]

camera = Camera()

en_cours = True
while en_cours:
    horloge.tick(60)

    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            en_cours = False

    joueur.mettre_a_jour(plateformes)
    camera.mettre_a_jour(joueur)

    ecran.fill((15, 15, 30))

    for plateforme in plateformes:
        pygame.draw.rect(
            ecran,
            (90, 90, 120),
            pygame.Rect(
                plateforme.x - camera.decalage_x,
                plateforme.y - camera.decalage_y,
                plateforme.width,
                plateforme.height
            )
        )

    pygame.draw.rect(
        ecran,
        (220, 80, 120),
        pygame.Rect(
            joueur.rectangle.x - camera.decalage_x,
            joueur.rectangle.y - camera.decalage_y,
            joueur.rectangle.width,
            joueur.rectangle.height
        )
    )

    pygame.display.flip()

pygame.quit()
