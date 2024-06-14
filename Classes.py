import pygame
pygame.init()
from math import *

        

class Block():
    def __init__(self, type, x,y):
        self.type = type
        self.image = pygame.image.load(self.type+".png")
        self.image = pygame.transform.scale(self.image,(25,25))
        self.x = x
        self.y = y

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))


class Platform():
    def __init__(self, type, x, y, length, height):
        self.blocks: list[Block] = []
        self.type = type
        self.x = x
        self.y = y
        lengthOffset = 0
        heightOffest = 0
        self.length = length
        self.height = height
        for x in range(self.length):
            for i in range(self.height):
                self.blocks.append(Block(self.type, self.x + lengthOffset,self.y + heightOffest))
                heightOffest += 25
            heightOffest = 0
            lengthOffset += 25

    def draw(self, surface):
        for block in self.blocks:
            block.draw(surface)
    
class Bounce(Platform):
    def __init__(self, x, y, length = 1, height = 1):
        Platform.__init__(self, "bounce", x, y, length, height)


class Grass(Platform):
    def __init__(self, x, y, length = 1, height = 1):
        Platform.__init__(self, "grass", x, y, length, height)

class Dive(Platform):
    def __init__(self, x, y, length = 1, height = 1):
        Platform.__init__(self, "dive", x, y, length, height)

class Lava(Platform):
    def __init__(self, x, y, length = 1, height = 1):
        Platform.__init__(self, "lava", x, y, length, height)

    

        

class Player():
    def __init__(self, x: int, y: int):
        self.facing = 'right'
        self.Vy = 0
        self.jumpSpeed = -20
        self.gravity = 2
        self.x = x
        self.y = y
        self.frame = 0
        self.frames = []

        for x in range(10):
            self.frames.append(pygame.transform.scale(pygame.image.load("mario"+str(x)+".png"), (25,50)))

        self.nextRightPic = [4, 4, 4, 4, 5, 6, 7, 5, 4, 4]
        self.nextLeftPic = [1, 2, 3, 1, 1, 1, 1, 1, 1, 1]

        self.jumped = False
        

    def draw(self, surface):
        surface.blit(self.frames[self.frame],(self.x,self.y))
    
    def moveRight(self, change = True):
        self.x += 10
        if change:
            self.facing = 'right'

    def moveLeft(self, change = True):
        self.x -= 10
        if change:
            self.facing = 'left'

    def collide(self, platforms: list[list[Platform]]):
        playerRect = pygame.Rect(self.x, self.y, 25, 50)
        if platforms == None:
            return False
        for platform in platforms:
            for block in platform.blocks:
                blockRect = pygame.Rect(block.x, block.y, 25, 25)
                if playerRect.colliderect(blockRect):
                    return True
        return False
    
    def grassCollide(self, platform: list[Platform]):
        playerRect = pygame.Rect(self.x, self.y, 25, 40)
        if platform == None:
            return False
        for block in platform:
                blockRect = pygame.Rect(block.x, block.y, 50, 25)
                if playerRect.colliderect(blockRect):
                    return True
        return False

    
    

class Level():
    def __init__(self, levelNumber: int, playerCoord: tuple[int], bedCoord, grass: list[Grass] = None , bounce: list[Bounce] = None, dive: list[Dive] = None, lava: list[Lava] = None, playLava = False):
        self.bedSpawn = bedCoord
        self.playerSpawn = playerCoord
        self.level = levelNumber
        self.grass = grass
        self.dive = dive
        self.lava = lava
        self.bounce = bounce
        self.playLava = playLava
        self.platforms: dict[str:list[Platform]] = {"grass":self.grass, "bounce":self.bounce, "dive": self.dive, "lava":self.lava}
        self.platformsDraw: list[list[Platform]] = [self.grass, self.bounce, self.dive, self.bounce, self.lava]
        

class Bed():
    def __init__(self, x, y):
        self.image = pygame.image.load("bed.png")
        self.image = pygame.transform.scale(self.image,(75,75))
        self.x = x
        self.y = y
    
    def collide(self, player: Player):
        playerRect = pygame.Rect(player.x, player.y, 25, 50)
        bedRect = pygame.Rect(self.x, self.y, 75, 55)

        if playerRect.colliderect(bedRect):
            return True
        return False
        

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

            

class Game():
    def __init__(self):
        self.start = False
        self.width = 600
        self.height = 900
        self.WHITE = (255,255,255)

        self.walkCount = 500
        
        self.surface = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()

        pygame.mixer.music.load("Intro.wav")
        pygame.mixer.music.set_volume(0.08)
        pygame.mixer.music.play(-1)

        self.burned = pygame.mixer.Sound("burned.wav")
        self.burned.set_volume(0.2)
        self.lava = pygame.mixer.Sound("lava.wav")
        self.lava.set_volume(0.5)
        self.jumpSound = pygame.mixer.Sound("bounce.wav")
        self.jumpSound.set_volume(0.2)
        self.landSound = pygame.mixer.Sound("land.wav")
        self.landSound.set_volume(0.2)
        self.walkingSound = pygame.mixer.Sound("walking.wav")
        self.walkingSound.set_volume(0.2)

        self.introImage = pygame.image.load("introBg.png")
        self.introBg = pygame.transform.scale(self.introImage,(self.width,self.height))
        self.fonts = {"Big":pygame.font.SysFont("Ariel Black",40),
                "Small":pygame.font.SysFont("Ariel Black",24),
                "Medium":pygame.font.SysFont("Ariel Black",30),
                "Title":pygame.font.SysFont("impact",50)
                     }

        self.deaths = 0
        self.level = 1
        self.levels: list[Level] = [
            None, #so that we can index using the self.level
            Level(
                1, 
                (30, 450),
                (500, 200),
                grass = [Grass(30, 500, 2), Grass(130, 450, 2), Grass(230, 400, 2), Grass(400, 350, 2)],
                lava = [Lava(0, 800, int(600/25))]
                ),
            Level(
                2,
                (30, 450),
                (500, 200),
                grass = [Grass(30,500, 2), Grass(400, 600, 2)],
                bounce= [Bounce(200, 500, 2), Bounce(500, 450, 2)],
                lava = [Lava(0, 800,int(600/25)), Lava(400, 325,1, 3)]
            ),
            Level(
                3,
                (30, 100),
                (500, 100),
                grass=[Grass(30, 150, 2), Grass(130, 600), Grass(350, 700)],
                bounce = [Bounce(230, 700, 2), Bounce(500,600,2), Bounce(420, 450, 2), Bounce(500, 300, 2)],
                dive = [Dive(325,550,2)],
                lava = [Lava(0, 800,int(600/25)), Lava(250, 100, 5, 18), Lava(500, 425,2), Lava(420, 275,2)],
                playLava = True
            )
            ]
        
        self.player = Player(self.levels[self.level].playerSpawn[0], self.levels[self.level].playerSpawn[1])
        self.bed = Bed(self.levels[self.level].bedSpawn[0], self.levels[self.level].bedSpawn[1])

    def reset(self):
        self.player.x, self.player.y = self.levels[self.level].playerSpawn
        self.deaths += 1
        self.player.jumped = False
        
    def introScreen(self):
        text = self.fonts["Title"].render("Press SPACE to Continue",1,self.WHITE)
        self.surface.blit(self.introBg, (0,0))
        self.surface.blit(text, (45, 700))

        pass
    def drawAll(self):
        self.surface.fill((0,0,0))
        if not self.start:
            self.introScreen()
        else:
            self.player.draw(self.surface)
            self.bed.draw(self.surface)
            for platform in self.levels[self.level].platformsDraw:
                if platform != None:
                    for block in platform:
                        block.draw(self.surface) 

    def unSinkPlayer(self):
        while self.player.collide(self.levels[self.level].platforms["grass"]):
            self.player.y -= 1
        self.player.y += 1 #player needs to be barely touchign grass so he can jump

    def gameCollide(self, type):
        return self.player.collide(self.levels[self.level].platforms[type])
    
    def bedCollide(self):
        if self.bed.collide(self.player):
            self.nextLevel()

    def sideGrassCollide(self):
        return self.player.grassCollide(self.levels[self.level].platforms["grass"])
    
    def nextLevel(self):
        self.level += 1
        self.player.x, self.player.y = self.levels[self.level].playerSpawn
        self.bed.x, self.bed.y = self.levels[self.level].bedSpawn
        if self.levels[self.level].playLava:
            self.lava.play()
        


