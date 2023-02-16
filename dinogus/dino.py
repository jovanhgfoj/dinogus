import os
import sys
import math
import random
import pygame

WIDTH = 623
HEIGHT = 150

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
pygame.display.set_caption('Dino')

class BG:			#arriere plan

    def __init__(self, x):		#permet de creer des textures pour chaque objet en fonction de ses dimensions
        self.width = WIDTH
        self.height = HEIGHT
        self.x = x
        self.y = 0
        self.set_texture()
        self.show()

    def update(self, dx):		#recharge por éviter la superposition d'images
        self.x += dx
        if self.x <= -WIDTH:
            self.x = WIDTH

    def show(self):			#affiche la texture
        screen.blit(self.texture, (self.x, self.y))

    def set_texture(self):
        path = os.path.join('assets/images/bg.png')
        self.texture = pygame.image.load(path)
        self.texture = pygame.transform.scale(self.texture, (self.width, self.height))

class Dino:		#prédéfinit les mouvements du dino

    def __init__(self):
        self.width = 44
        self.height = 44
        self.x = 10
        self.y = 80
        self.texture_num = 0
        self.dy = 3
        self.gravity =  0.75
        self.onground = True
        self.jumping = False
        self.jump_stop = 10
        self.falling = False
        self.fall_stop = self.y
        self.set_texture()
        self.set_sound()
        self.show()

    def update(self, loops):		#saut
        if self.jumping:
            self.y -= self.dy
            if self.y <= self.jump_stop:
                self.fall()
        
        elif self.falling:		#retombée après saut
            self.y += self.gravity * self.dy
            if self.y >= self.fall_stop:
                self.stop()

        elif self.onground and loops % 4 == 0:		#courrir
            self.texture_num = (self.texture_num + 1) % 3
            self.set_texture()
        

    def show(self):		#permet d'afficher les textures a une position
        screen.blit(self.texture, (self.x, self.y))

    def set_texture(self):
        path = os.path.join(f'assets/images/dino{self.texture_num}.png')
        self.texture = pygame.image.load(path)
        self.texture = pygame.transform.scale(self.texture, (self.width, self.height))

    def set_sound(self):
        path = os.path.join('assets/sounds/saut.wav')
        self.sound = pygame.mixer.Sound(path)

    def jump(self):
        self.sound.play()
        self.jumping = True
        self.onground = False

    def fall(self):
        self.jumping = False
        self.falling = True

    def stop(self):
        self.falling = False
        self.onground = True

class Cactus:

    def __init__(self, x):
        self.width = 34
        self.height = 44
        self.x = x
        self.y = 80
        self.set_texture()
        self.show()

    def update(self, dx):
        self.x += dx

    def show(self):
        screen.blit(self.texture, (self.x, self.y))

    def set_texture(self):
        path = os.path.join('assets/images/cactus.png')
        self.texture = pygame.image.load(path)
        self.texture = pygame.transform.scale(self.texture, (self.width, self.height))

class Collision:

    def between(self, obj1, obj2):
        distance = math.sqrt((obj1.x - obj2.x)**2 + (obj1.y - obj2.y)**2)
        return distance < 35

class Score:

    def __init__(self, hs):
        self.hs = hs
        self.act = 0
        self.font = pygame.font.SysFont('monospace', 18)
        self.color = (0, 0, 0)
        self.set_sound()
        self.show()

    def update(self, loops):		#met a jour le score à chaque fois
        self.act = loops // 10
        self.check_hs()
        self.check_sound()

    def show(self):
        self.lbl = self.font.render(f'HI {self.hs} {self.act}', 1, self.color)
        lbl_width = self.lbl.get_rect().width
        screen.blit(self.lbl, (WIDTH - lbl_width - 10, 10))

    def set_sound(self):
        path = os.path.join('assets/sounds/100.wav')
        self.sound = pygame.mixer.Sound(path)

    def check_hs(self):
        if self.act >= self.hs:
            self.hs = self.act

    def check_sound(self):
        if self.act % 100 == 0 and self.act != 0:
           self.sound.play()

class Game:

    def __init__(self, hs=0):		#définit les valeurs par défaut
        self.bg = [BG(x=0), BG(x=WIDTH)]
        self.dino = Dino()
        self.obstacles = []
        self.collision = Collision()
        self.score = Score(hs)
        self.speed = 3
        self.playing = False
        self.set_sound()
        self.set_labels()
        self.spawn_cactus()

    def set_labels(self):		#disposition des textes
        big_font = pygame.font.SysFont('monospace', 24, bold=True)
        small_font = pygame.font.SysFont('monospace', 18)
        self.big_lbl = big_font.render(f'perdu', 1, (0, 0, 0))
        self.small_lbl = small_font.render(f'appuyer sur R pour reccomencer', 1, (0, 0, 0))

    def set_sound(self):		#permet de jouer les sons
        path = os.path.join('assets/sounds/mort.wav')
        self.sound = pygame.mixer.Sound(path)

    def start(self):
        self.playing = True

    def over(self):		#animation du game over
        self.sound.play()
        screen.blit(self.big_lbl, (WIDTH // 2 - self.big_lbl.get_width() // 2, HEIGHT // 4))
        screen.blit(self.small_lbl, (WIDTH // 2 - self.small_lbl.get_width() // 2, HEIGHT // 2))
        self.playing = False

    def tospawn(self, loops):
        return loops % 100 == 0

    def spawn_cactus(self):
        #définit l'espace entre les cactus
        if len(self.obstacles) > 0:
            prev_cactus = self.obstacles[-1]
            x = random.randint(prev_cactus.x + self.dino.width + 84, WIDTH + prev_cactus.x + self.dino.width + 84)

        #redéfinit l'espace entre les cactus
        else:
            x = random.randint(WIDTH + 100, 1000)

        # fait apparaitre un cactus a une position
        cactus = Cactus(x)
        self.obstacles.append(cactus)

    def restart(self):		#permet de changer le score a chaque évolution
        self.__init__(hs=self.score.hs)

def main():

    # objets
    game = Game()
    dino = game.dino

    # variables
    clock = pygame.time.Clock()
    loops = 0
    over = False

    #boucle principale qui (corps du jeu)
    while True:

        if game.playing:

            loops += 1

            #arriere plan
            for bg in game.bg:
                bg.update(-game.speed)
                bg.show()

            #dino
            dino.update(loops)
            dino.show()

            #cactus
            if game.tospawn(loops):
                game.spawn_cactus()

            for cactus in game.obstacles:
                cactus.update(-game.speed)
                cactus.show()

                #collision
                if game.collision.between(dino, cactus):
                   over = True
            
            if over:
                game.over()

            #score
            game.score.update(loops)
            game.score.show()

        #évolution de la fenetre(quitter; raccourcis...)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not over:
                        if dino.onground:
                            dino.jump()

                        if not game.playing:
                            game.start()

                if event.key == pygame.K_r:
                    game.restart()
                    dino = game.dino
                    loops = 0
                    over = False

        clock.tick(80)
        pygame.display.update()

main()