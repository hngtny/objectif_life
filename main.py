import pygame
from pygame import FULLSCREEN

from menu import Menu
from game import Jeu

pygame.init()

LARGEUR, HAUTEUR = 800, 480
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR),FULLSCREEN)
logo = pygame.image.load('assets/images/objectif life logo.png')
pygame.display.set_icon(logo)
pygame.display.set_caption("Objectif Life")

horloge = pygame.time.Clock()

etat = "menu"

menu = Menu(ecran)
jeu = Jeu(ecran)

en_cours = True
while en_cours:
    horloge.tick(60)

    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            en_cours = False

        if etat == "menu":
            action = menu.gerer_evenement(evenement)
            if action == "jouer":
                jeu.nouvelle_partie()
                etat = "jeu"
            elif action == "quitter":
                en_cours = False

        elif etat == "jeu":
            if evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_ESCAPE:
                    etat = "menu"

    if etat == "menu":
        menu.dessiner()

    elif etat == "jeu":
        jeu.mettre_a_jour()
        jeu.dessiner()

    pygame.display.flip()

pygame.quit()
