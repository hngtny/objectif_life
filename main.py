import pygame
from menu import Menu
from game import Jeu

pygame.init()

info = pygame.display.Info()
LARGEUR, HAUTEUR = info.current_w, info.current_h
ecran = pygame.display.set_mode((LARGEUR,HAUTEUR))

logo = pygame.image.load('Assets/images/objectif life logo.png')
pygame.display.set_icon(logo)
pygame.display.set_caption("Objectif Life")

horloge = pygame.time.Clock()

def changer_musique(chemin_fichier):
    pygame.mixer.music.fadeout(1000)
    pygame.mixer.music.load(chemin_fichier)
    pygame.mixer.music.play(-1, fade_ms=2000)

etat = "menu"
changer_musique("Assets/songs/menu.mp3")

menu = Menu(ecran)
jeu = Jeu(ecran)

pygame.mixer.init()
pygame.mixer.music.load("Assets/songs/Song.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

en_cours = True
while en_cours:
    horloge.tick(60)

    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            en_cours = False

        if etat == "menu":
            action = menu.gerer_evenement(evenement)
            changer_musique("Assets/songs/menu.mp3")

            if action == "jouer":
                jeu.nouvelle_partie()
                etat = "jeu"
                changer_musique("Assets/songs/Song.mp3")

            elif action == "quitter":
                en_cours = False

        elif etat == "jeu":
            if evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_ESCAPE:
                    etat = "menu"

            if jeu.etat_niveau != "en_cours":
                jeu.gerer_evenements_niveau(evenement)

    if etat == "menu":
        menu.dessiner()

    elif etat == "jeu":
        jeu.mettre_a_jour()
        jeu.dessiner()

    pygame.display.flip()
pygame.quit()