import pygame

LARGEUR, HAUTEUR = 1920, 1080

class Menu:
    def __init__(self, ecran):
        self.ecran = ecran
        self.police = pygame.font.Font("assets/fonts/Pixelify_Sans/PixelifySans-Regular.ttf", 70)
        self.selection = 0
        self.options = ["Nouvelle Partie", "Quitter"]

    def gerer_evenement(self, evenement):
        if evenement.type == pygame.KEYDOWN:

            if evenement.key == pygame.K_ESCAPE:
                return "quitter"

            if evenement.key == pygame.K_UP:
                self.selection = (self.selection - 1) % len(self.options)

            if evenement.key == pygame.K_DOWN:
                self.selection = (self.selection + 1) % len(self.options)

            if evenement.key == pygame.K_RETURN:
                if self.selection == 0:
                    return "jouer"
                elif self.selection == 1:
                    return "quitter"

        return None

    def dessiner(self):
        self.ecran.fill((15, 15, 30))

        titre = self.police.render("OBJECTIF LIFE", True, (255, 255, 255))
        self.ecran.blit(titre, (LARGEUR//2 - titre.get_width()//2, 400))

        for i, texte in enumerate(self.options):
            couleur = (255, 255, 255)
            if i == self.selection:
                couleur = (220, 80, 120)

            rendu = self.police.render(texte, True, couleur)
            self.ecran.blit(rendu, (LARGEUR//2 - rendu.get_width()//2, 500 + i*60))