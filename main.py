"""
Pygame game based on bomberman 
Includes a somewhat functional bot to play against
I think all the bugs have been removed
"""


import os
from pyexpat.errors import XML_ERROR_BINARY_ENTITY_REF
import pygame
from colours import *
import time
import random
import os
import csv
import sys
import menus
from pygame.locals import (
    K_w, 
    K_a, 
    K_s, 
    K_d, 
    K_b, 
    K_ESCAPE, 
    K_UP, 
    K_DOWN, 
    K_LEFT,
    K_RIGHT, 
    K_RETURN
)
GAME = None
INACTIVE_MARGIN = 200
THINGS_WIDTH = 50
THINGS_HEIGHT = THINGS_WIDTH
BANNER_HEIGHT = 25
WIDTH = None
HEIGHT = None
PLAYERHEIGHT = THINGS_HEIGHT-10
PLAYERWIDTH = int(PLAYERHEIGHT*0.75//1)
GAME_COUNT = 0

GAME_FRAMES = 45
#constants
GRAVITY = -1
JUMP_STRENGTH = 30
DRAG = 1
MOVE_STRENGTH = 1
RUN_SPEED = 10
EXPLOSION_SPEED = 10

FONT = None

class Point2D:
    def __init__(self,x,y): self.x,self.y = x,y
    def __add__(self,other): return Point2D(self.x+other.x,self.y+other.y)
    def __iadd__(self,other): return self.__add__(other)
    def __sub__(self,other): return Point2D(self.x-other.x,self.y-other.y)
    def __isub__(self,other): return self.__sub__(other)
    def __str__(self): return f"({self.x},{self.y})"
    def __mul__(self,other): return Point2D(self.x*other.x, self.y*other.y)
    def __repr__(self) -> str: return self.__str__()
    def inv(self): return Point2D(-self.x,-self.y)
    def __eq__(self, other) -> bool:
        if other.x==self.x and other.y==self.y: return True
        return False
    def __abs__(self): return (self.x**2+self.y**2)**0.5
        




class Banner(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([WIDTH, BANNER_HEIGHT])
        self.rect = self.image.get_rect()
        self.image.fill(LIGHT_GREY)
        self.rect.x = 0
        self.rect.y = 0
        self.setText(0,0)
        
    def setText(self,p1b,p2b):
        t = (200*GAME_FRAMES-GAME_COUNT)//GAME_FRAMES
        self.scoreText = FONT.render(f"TIME: {t}", True, WHITE, LIGHT_GREY)
        self.scoreTextRect = self.scoreText.get_rect()
        self.scoreTextRect.x = 20
        self.scoreTextRect.y = 0
        self.image.blit(self.scoreText,self.scoreTextRect)
        self.scoreText = FONT.render(f"PLAYER 1 BOMBS: {p1b}", True, WHITE, LIGHT_GREY)
        self.scoreTextRect = self.scoreText.get_rect()
        self.scoreTextRect.x = 120
        self.scoreTextRect.y = 0
        self.image.blit(self.scoreText,self.scoreTextRect)
        self.scoreText = FONT.render(f"PLAYER 2 BOMBS: {p2b}", True, WHITE, LIGHT_GREY)
        self.scoreTextRect = self.scoreText.get_rect()
        self.scoreTextRect.x = 340
        self.scoreTextRect.y = 0
        self.image.blit(self.scoreText,self.scoreTextRect)
        if t==0: return True
        else: return False

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y,msg):
        super().__init__(GAME.players)
        self.image = pygame.transform.scale(pygame.image.load(os.path.join("img","player.png")),(PLAYERWIDTH,PLAYERHEIGHT))
        self.rect = self.image.get_rect()
        self.msg=msg
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.bombs = []
        self.bombs_count = 0
        self.powerUpTime = 0
        self.lives = 0
    def moveRight(self): self.rect.x += self.speed
    def moveLeft(self): self.rect.x -= self.speed
    def moveUp(self): self.rect.y -= self.speed
    def moveDown(self): self.rect.y += self.speed
    def dropBomb(self): 
        if self.bombs_count>0: 
            self.bombs.append(Bomb(self.rect.centerx, self.rect.centery))
            self.bombs_count -= 1   
    def update(self):
        self.SQ = Point2D(
            (self.rect.centerx//THINGS_WIDTH),
            ((self.rect.centery-BANNER_HEIGHT)//THINGS_HEIGHT)
        )
        self.pos = Point2D(
            self.rect.centerx,
            self.rect.centery
        )
        self.collideCheck()
        for bomb in self.bombs:
            if bomb: 
                if bomb.tick():
                    bomb.kill()
                    self.bombs.remove(bomb)
                    self.bombs_count =len(self.bombs)
        # powerups
        if self.powerUpTime:
            self.powerUpTime -= 1
            if self.powerUpTime==0: self.endPowerUp()

    def collideCheck(self):
        touched = pygame.sprite.spritecollide(self, GAME.powerUps, False) # IDK why this dosnt work
        if touched:
            for t in touched: self.powerUp(t.collected())
            #"self.kill() # why?? "# I genuinly just left this in and I think it broke it
        touched = pygame.sprite.spritecollide(self, GAME.walls, False)
        for t in touched:
            if(self.rect.top < t.rect.bottom)and(abs(self.rect.top-t.rect.bottom)<2*self.speed): self.rect.top = t.rect.bottom
            if(self.rect.bottom > t.rect.top)and(abs(self.rect.bottom-t.rect.top)<2*self.speed): self.rect.bottom = t.rect.top
            if(self.rect.right > t.rect.left)and(abs(self.rect.right-t.rect.left)<2*self.speed): self.rect.right = t.rect.left
            if(self.rect.left < t.rect.right)and(abs(self.rect.left-t.rect.right)<2*self.speed): self.rect.left = t.rect.right
        if touched: return True
        else: return False
        
    def powerUp(self, type_):
        if 0==self.powerUpTime:
            if type_=="speed-boost":
                self.speed += 5
                self.image.blit(pygame.transform.scale(pygame.image.load(os.path.join("img","powerup-speed.png")),(20,20)),(0,0))
            elif type_=="extra-life":
                self.lives = 1
                self.image.blit(pygame.transform.scale(pygame.image.load(os.path.join("img","powerup-extralife.png")),(20,20)),(0,0))
            self.type_ = type_
            self.powerUpTime = GAME.FPS*3
    def endPowerUp(self):
        self.image = pygame.transform.scale(pygame.image.load(os.path.join("img","player.png")),(PLAYERWIDTH,PLAYERHEIGHT))
        if self.type_=="speed-boost": self.speed -= 5
        if self.type_=="extra-life": self.lives = 0
        self.type_ = None

    def hit(self): 
        if self.lives==0: GAME.hit(self.msg)
        else: 
            self.image = pygame.transform.scale(pygame.image.load(os.path.join("img","player.png")),(PLAYERWIDTH,PLAYERHEIGHT))
            self.lives -= 1

    def decay(self):
        if self.alivemoments: self.alivemoments -= 1
        else: self.kill()
        
class Bot(Player):
    def __init__(self,*args):
        super().__init__(*args)
        self.AI = BotAI()
        # self.aggresiveness = 5
        # self.safty = 7
        # self.desieretobreakwalls = 3
        self.setPosWithCoord(Point2D(14,9))
        #self.setCourse()
        self.moves = [Point2D(14,9)]
        self.runningAway = False
            
    def setCourse(self,spec=None): 
        """
        Creates a path which can be specified

        Choice 
        1: random
        2: otherplayer
        3: powerUp
        4: run away (Only called manually)
        """
        #for row in GAME.map: print (row)
        def checkOpen(sq):
            if GAME.map[sq.y][sq.x]==".": return True
            else: return False
        #print(" - : \t",[ str(j) for j in range(15)])
        #for y in range(12): print(y, " :\t",["."if checkOpen(Point2D(x,y)) else "#"for x in range(16) ])
        #### Staring Square ####
        ## Functions
        def rand():
            t = Point2D(random.randint(0,len(GAME.map[0])-1),random.randint(0,len(GAME.map)-1))
            while not checkOpen(t): t = Point2D(random.randint(0,len(GAME.map[0])-1),random.randint(0,len(GAME.map)-1))
            return t
        def otherplayer():
            return Point2D(
                (player1.rect.x//THINGS_WIDTH),
                ((player1.rect.y-BANNER_HEIGHT)//THINGS_HEIGHT)
            )
        def powerUp():
            if len(GAME.powerUps.sprites())>0: return random.choice(GAME.powerUps.sprites()).getSQ()
            else: return rand()
        def runAway(): 
            self.runningAway = True
            n = rand()
            while abs(n-self.SQ)<=self.AI.safty: n = rand()
            return n 
        o = {
            1: rand,
            2: otherplayer,
            3: powerUp,
            4: runAway
        }
        if self.runningAway: self.runningAway = False
        if spec: self.targetSQ = o[spec]()
        else: self.targetSQ = o[random.randint(1,3)]()# this will bve imporved but atm that just breaks it
        ## Pick what to do=
        #### pathfinder ####
        ## Starting stuff
        SQ = self.SQ 
        moves = [self.SQ]
        sqsToAvoid = []
        done = False
        n = 80
        priority = random.choice(("X","Y"))# removes predictability somewhat
        while n!=0:
            n -= 1
            ## set direction
            if SQ.x>self.targetSQ.x: X = Point2D(-1,0)
            elif SQ.x<self.targetSQ.x: X = Point2D(1,0)
            else: X = Point2D(0,0)
            if SQ.y>self.targetSQ.y: Y = Point2D(0,-1)
            elif SQ.y<self.targetSQ.y: Y = Point2D(0,1)
            else: Y = Point2D(0,0)
            ## Find next square
            # Trying to get there directly or if not go antoher route
            if priority=="X":
                if checkOpen(SQ+X)and(SQ+X)not in [*moves,*sqsToAvoid]: SQ += X
                elif checkOpen(SQ+Y)and(SQ+Y)not in [*moves,*sqsToAvoid]: SQ += Y
                elif checkOpen(SQ-X)and(SQ-X)not in [*moves,*sqsToAvoid]: SQ -= X
                elif checkOpen(SQ-Y)and(SQ-Y)not in [*moves,*sqsToAvoid]: SQ -= Y
                else: # Reversing
                    sqsToAvoid.append(SQ)
                    if moves: moves.pop()
                    if checkOpen(SQ+X)and(SQ+X)not in sqsToAvoid: SQ += X
                    if checkOpen(SQ+Y)and(SQ+Y)not in sqsToAvoid: SQ += Y
                    if checkOpen(SQ-X)and(SQ-X)not in sqsToAvoid: SQ -= X
                    if checkOpen(SQ-Y)and(SQ-Y)not in sqsToAvoid: SQ -= Y
            if priority=="Y":
                if checkOpen(SQ+Y)and(SQ+Y)not in [*moves,*sqsToAvoid]: SQ += Y
                elif checkOpen(SQ+X)and(SQ+X)not in [*moves,*sqsToAvoid]: SQ += X
                elif checkOpen(SQ-Y)and(SQ-Y)not in [*moves,*sqsToAvoid]: SQ -= Y
                elif checkOpen(SQ-X)and(SQ-X)not in [*moves,*sqsToAvoid]: SQ -= X
                else: # Reversing
                    sqsToAvoid.append(SQ)
                    if moves: moves.pop()
                    if checkOpen(SQ+Y)and(SQ+Y)not in sqsToAvoid: SQ += Y
                    if checkOpen(SQ+X)and(SQ+X)not in sqsToAvoid: SQ += X
                    if checkOpen(SQ-Y)and(SQ-Y)not in sqsToAvoid: SQ -= Y
                    if checkOpen(SQ-X)and(SQ-X)not in sqsToAvoid: SQ -= X

        # Stuff
            moves.append(SQ)
            if SQ == self.targetSQ: done = True
        self.moves = moves
        #self.setPosWithCoord(self.moves[0])


    def update(self):
        """
        Moves in line with a pre detirmined path although it can change the path due to tactics (wow!)
        """
        super().update()
        # Super.update creates
        # self.SQ
        # self.pos
        self.targetPos = Point2D(
            ((self.moves[0].x*THINGS_WIDTH)+(THINGS_WIDTH//2)),
            ((self.moves[0].y*THINGS_HEIGHT)+(THINGS_HEIGHT//2)+BANNER_HEIGHT)
        )
        # if not self.moves:
        #     self.setCourse()
        #     self.currentDirec = self.SQ-self.moves[0]

        ### The responsive part ###
        ## Bomb droping
        # If close to oponent
        if not self.runningAway and abs(player1.pos-self.pos)<self.AI.bombCloseness and random.randint(0,self.AI.aggressiveness)==1: 
            if self.bombs_count>0: 
                self.dropBomb()
                self.setCourse(4)
                self.targetPos = self.pos
        # If close to a wall
        for wall in GAME.breakingwalls:
            if not self.runningAway and abs(player1.pos-wall.pos)<self.AI.wallDist and random.randint(0,self.AI.wallAggressiveness)==1: 
                if self.bombs_count>0: 
                    self.dropBomb()
                    self.setCourse(4)
                    self.targetPos = self.pos
        ## Bomb escaping
        for bomb in GAME.bombs:
            if self.runningAway!=bomb and abs(player1.pos-wall.pos)<THINGS_WIDTH*3 and random.randint(0,self.AI.aggressiveness)!=0: 
                if self.bombs_count>0: 
                    self.dropBomb()
                    self.setCourse(4)
                    self.targetPos = self.pos


        #### Just following the path ####

        if self.pos==self.targetPos:
            self.setPosWithCoord(self.moves[0])
            self.moves.pop(0)
            if not self.moves: self.setCourse()
            self.currentDirec = self.moves[0]-self.SQ
            #if abs(self.currentDirec)!=1: raise AlgorithmError
        else: self.moveByDirecVector(self.currentDirec)
    def moveByVector(self, vector):
        self.rect.x += vector.x
        self.rect.y += vector.y
    def moveByDirecVector(self, vector): 
        if vector.x>1: vector.x = 1
        if vector.x<-1: vector.x = -1
        if vector.y>1: vector.y = 1
        if vector.x<-1: vector.y = -1
        return self.moveByVector(Point2D(self.speed,self.speed)*vector)
    def setPos(self,point): self.rect.centerx, self.rect.centery = point.x, point.y
    def setPosWithCoord(self,coord): self.rect.centerx, self.rect.centery = ((coord.x*THINGS_WIDTH)+(THINGS_WIDTH//2)), ((coord.y*THINGS_HEIGHT)+(THINGS_HEIGHT//2)+BANNER_HEIGHT)
    def collideCheck(self):
        """Very lazy bug fix"""
        r = super().collideCheck()
        if pygame.sprite.spritecollide(self, GAME.walls, False): self.setPosWithCoord(self.SQ)
        return r

class HumanPlayer(Player):
    def dropBomb(self):
        player2.AI.bombDropped(self.pos,player2.pos)
        return super().dropBomb()

class BotAI:
    """This class collects data about how player one work and uses it to influence how the bot plays"""
    def __init__(self,bombCloseness=3*THINGS_WIDTH, wallDist=THINGS_WIDTH, agressiveness= 5,safty=7,wallAggressiveness=2) -> None:
        self._bombCloseness = [bombCloseness]
        self._wallDist = [wallDist]
        self._safty = [safty]
        self.bombCloseness = bombCloseness
        self.wallDist = wallDist
        self.aggressiveness = agressiveness
        self.safty = safty
        self.wallAggressiveness = wallAggressiveness

    def bombDropped(self,humanpos,botpos):
        playerdist= abs(humanpos-botpos)
        if playerdist <2*self.bombCloseness:
            self._bombCloseness.append(playerdist)
            self.bombCloseness = sum(self._bombCloseness)/len(self._bombCloseness)
        else:
            for wall in GAME.breakingwalls:
                walldist = abs(wall.pos-botpos)
                if walldist<2*self.wallDist:
                    self._wallDist.append(walldist)
                    self.wallDist = sum(self._wallDist)/len(self._wallDist)
    def bombExploded(self,bombpos, playerpos):
        self._safty.append(abs(bombpos-playerpos))
        self.safty = sum(self._safty)/len(self._safty)


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(GAME.walls)
        self.image = pygame.transform.scale(pygame.image.load(os.path.join("img","wall.png")),(THINGS_WIDTH,THINGS_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class BreakingWall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(GAME.walls,GAME.breakingwalls)
        self.image = pygame.transform.scale(pygame.image.load(os.path.join("img","breakingwall.png")),(THINGS_WIDTH,THINGS_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.SQ = Point2D(
            (self.rect.centerx//THINGS_WIDTH),
            ((self.rect.centery-BANNER_HEIGHT)//THINGS_HEIGHT)
        )
        self.pos = Point2D(
            self.rect.centerx,
            self.rect.centery
        )
    
    def hit(self): 
        GAME.todestroy.add(self)
        self.lives = 5
        self.image.fill(RED)
    def decay(self):
        if self.lives: self.lives -= 1
        else: self.kill()
        
class PowerUp(pygame.sprite.Sprite):
    def __init__(self,x, y, image):
        super().__init__(GAME.powerUps)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x,y

    def collected(self):
        GAME.todestroy.add(self)
        return self.getType()

    def getSQ(self):
        return Point2D(
            (self.rect.centerx//THINGS_WIDTH),
            ((self.rect.centery-BANNER_HEIGHT)//THINGS_HEIGHT)
        )

    def decay(self): self.kill()


class SpeedPowerUp(PowerUp):
    def __init__(self,x,y): super().__init__(x,y,pygame.transform.scale(pygame.image.load(os.path.join("img","powerup-speed.png")),(THINGS_WIDTH,THINGS_HEIGHT)))#pygame.image.load(os.path.join("img","powerup_speed.png")))
    def getType(self): return "speed-boost"
class LifePowerUp(PowerUp):
    def __init__(self,x,y): super().__init__(x,y,pygame.transform.scale(pygame.image.load(os.path.join("img","powerup-extralife.png")),(THINGS_WIDTH,THINGS_HEIGHT)))#pygame.image.load(os.path.join("img","powerup_speed.png")))
    def getType(self): return "extra-life"
class BombPowerUp(PowerUp):
    def __init__(self,x,y): super().__init__(x,y,pygame.transform.scale(pygame.image.load(os.path.join("img","powerup-speed.png")),(THINGS_WIDTH,THINGS_HEIGHT)))#pygame.image.load(os.path.join("img","powerup_speed.png")))
    def getType(self): return "big-bomb"
        

class Bomb(pygame.sprite.Sprite):
    def __init__(self, cx, cy):
        super().__init__(GAME.bombs)
        self.height = PLAYERWIDTH
        self.width = PLAYERWIDTH
        self.image = pygame.transform.scale(pygame.image.load(os.path.join("img","bomb.png")),(self.width,self.height))#pygame.Surface([self.width,self.height])
        self.rect = self.image.get_rect()
        self.rect.centerx = cx
        self.rect.centery = cy
        self.fuse = (GAME_FRAMES*1.5)//1
        self.pos = Point2D(
            self.rect.centerx,
            self.rect.centery
        )
    def tick(self):
        if self.fuse>0: self.fuse -= 1
        elif self.fuse == 0: return self.explode()
        else: raise IDKError
    def explode(self):
        for b in range(self.width): V_Shards(self.rect.x+b, self.rect.y+self.height, EXPLOSION_SPEED) 
        for o in range(self.width): V_Shards(self.rect.x+o, self.rect.y, -EXPLOSION_SPEED)
        for m in range(self.height): H_Shards(self.rect.x, self.rect.y+m, -EXPLOSION_SPEED)
        for b in range(self.height): H_Shards(self.rect.x+self.width, self.rect.y+b, EXPLOSION_SPEED)
        if type(player2) =="BOT": player2.AI.bombExploded(self.pos, player1.pos)
        return True


class Shard(pygame.sprite.Sprite):
    def __init__(self, velocity): 
        super().__init__(GAME.shards)
        self.velocity = velocity
        self.rect = self.image.get_rect()
        self.image.fill(ORANGE)
    def update(self):
        touched = pygame.sprite.spritecollide(self, GAME.breakingwalls, False) # IDK why this dosnt work
        if touched:
            for t in touched: t.hit()
            self.kill()
        
        touched = pygame.sprite.spritecollide(self, GAME.players, False) # IDK why this dosnt work
        if touched:
            for t in touched: t.hit()
            self.kill()
        touched = pygame.sprite.spritecollide(self, GAME.walls, False)
        if touched: self.kill()

class V_Shards(Shard):
    def __init__(self, x, cy, velocity):
        self.image = pygame.Surface([1,random.randint(20,35)])
        super().__init__(velocity)
        self.rect.x = x
        self.rect.centery = cy
        self.Ylim = self.rect.centery + velocity*((4*THINGS_HEIGHT)//EXPLOSION_SPEED)
    def update(self):
        if self.rect.centery == self.Ylim: self.kill()
        self.rect.y += self.velocity
        super().update()
class H_Shards(Shard):
    def __init__(self, cx, y, velocity):
        self.image = pygame.Surface([random.randint(10,15),1])
        super().__init__(velocity)
        self.rect.centerx = cx
        self.rect.y = y
        self.Xlim = self.rect.centerx + velocity*((4*THINGS_WIDTH)//EXPLOSION_SPEED)
    def update(self):
        if self.rect.centerx == self.Xlim: self.kill()
        self.rect.x += self.velocity
        super().update()
        
def generateNewPowerUp(): 
    if len(GAME.powerUps.sprites())<5:
        x = random.randint(0,len(GAME.map[0])-1)
        y = random.randint(0,len(GAME.map)-1)
        while GAME.map[y][x]!=".":
            x = random.randrange(0,len(GAME.map[0]))
            y = random.randrange(0,len(GAME.map))
        # Should be a random power up
        n = random.randint(1,3)
        if n==1:SpeedPowerUp(x*THINGS_WIDTH,y*THINGS_HEIGHT+BANNER_HEIGHT)
        elif n==2:LifePowerUp(x*THINGS_WIDTH,y*THINGS_HEIGHT+BANNER_HEIGHT)
        elif n ==3:BombPowerUp(x*THINGS_WIDTH,y*THINGS_HEIGHT+BANNER_HEIGHT)
class Game:
    FPS = 30
    def exec(self):
        self.msg = "ERROR"
        
        player1, player2 = None,None
        with open("grid.csv") as f:
            r = csv.reader(f)
            self.map = []
            for row in r:
                GAME.map.append(row)
        global WIDTH, HEIGHT, FONT
        WIDTH = THINGS_WIDTH*(len(self.map[0]))
        HEIGHT = THINGS_HEIGHT*(len(self.map))+BANNER_HEIGHT
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode([WIDTH,HEIGHT],pygame.NOFRAME)
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        result = menus.openingScreen(self.screen)
        if result=="ESC":
            pygame.quit()
            sys.exit()
        FONT = pygame.font.SysFont('Arial',20)
        self.walls = pygame.sprite.Group()
        self.bombs = pygame.sprite.Group()
        self.shards = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.breakingwalls = pygame.sprite.Group()
        self.todestroy = pygame.sprite.Group()
        self.powerUps = pygame.sprite.Group()
        for i in range(len(self.map)):
            for j in range(len(self.map[i])):
                if(self.map[i][j]=="#"): Wall((j*THINGS_WIDTH),(i*THINGS_HEIGHT+BANNER_HEIGHT))
                elif(self.map[i][j]=="~"): BreakingWall((j*THINGS_WIDTH),(i*THINGS_HEIGHT+BANNER_HEIGHT))
                elif(self.map[i][j]=="."): pass
        if result=="AI": self.main_againtComputer()
        elif result=="MULTI": self.main_multiplayer()
        

        pygame.quit()
        sys.exit()
    def hit(self,msg="!ERROR!"):
        self.done = True
        self.msg = msg

    def main_againtComputer(self):
        global GAME_COUNT, player1, player2
        self.screen.fill(GREEN)
        clock = pygame.time.Clock()
        banner = Banner()

        player1 = Player(THINGS_WIDTH,THINGS_HEIGHT+BANNER_HEIGHT,"Computer Wins")
        player2 = Bot(WIDTH-(2*THINGS_WIDTH),HEIGHT -(3*THINGS_HEIGHT),"You Win")
        time.sleep(0.2)
        self.done = False
        while not self.done:
            GAME_COUNT += 1
            clock.tick(self.FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.done = True

            keys = pygame.key.get_pressed()
            done = banner.setText(player1.bombs_count, player2.bombs_count)

            if keys[K_w]: player1.moveUp()
            if keys[K_s]: player1.moveDown()
            if keys[K_a]: player1.moveLeft()
            if keys[K_d]: player1.moveRight()
            if keys[K_b]: player1.dropBomb()
            if keys[K_ESCAPE]: self.done = True
            self.main_shared(banner)
        self.endscreen()
    def endscreen(self):
        somthing = menus.endingScreen(self.screen,self.msg)
        if somthing=="CONT": self.exec()
        else: 
            pygame.quit()
            exit

    def main_multiplayer(self):
        global GAME_COUNT, player1, player2
        self.screen.fill(GREEN)
        clock = pygame.time.Clock()
        banner = Banner()

        player1 = Player(THINGS_WIDTH,THINGS_HEIGHT+BANNER_HEIGHT, "Player 2 wins")
        player2 = Player(WIDTH-(2*THINGS_WIDTH),HEIGHT -(3*THINGS_HEIGHT),"Player 1 wins")
        time.sleep(0.2)
        self.done = False
        while not self.done:
            GAME_COUNT += 1
            clock.tick(self.FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.done = True

            keys = pygame.key.get_pressed()
            done = banner.setText(player1.bombs_count,player2.bombs_count)

            if keys[K_w]: player1.moveUp()
            if keys[K_s]: player1.moveDown()
            if keys[K_a]: player1.moveLeft()
            if keys[K_d]: player1.moveRight()
            if keys[K_b]: player1.dropBomb()
            if keys[K_UP]: player2.moveUp()
            if keys[K_DOWN]: player2.moveDown()
            if keys[K_LEFT]: player2.moveLeft()
            if keys[K_RIGHT]: player2.moveRight()
            if keys[K_RETURN]: player2.dropBomb()
            if keys[K_ESCAPE]: self.done = True
            self.main_shared(banner)
        self.endscreen()


    def main_shared(self,banner):
        if GAME_COUNT%(self.FPS)==0 and player1.bombs_count < 3: player1.bombs_count += 1 # IK this isnt OO but Its not v big code
        if GAME_COUNT%(self.FPS)==0 and player2.bombs_count < 3: player2.bombs_count += 1
        self.shards.update()
        player1.update()
        player2.update()
        for thing in self.todestroy: thing.decay()
        if random.randint(1,self.FPS*5)==1: generateNewPowerUp()
        self.screen.fill((6, 167, 25))
        self.screen.blit(banner.image, banner.rect)
        self.walls.draw(self.screen)
        self.shards.draw(self.screen)
        self.bombs.draw(self.screen)
        self.powerUps.draw(self.screen)
        
        if (200*GAME_FRAMES-GAME_COUNT)//GAME_FRAMES==0: 
            self.msg = "Time up"
            self.done = True
        self.screen.blit(player1.image, player1.rect)
        self.screen.blit(player2.image, player2.rect)
        pygame.display.flip()

        
if __name__=="__main__":
    GAME = Game()
    GAME.exec()
    

class IDKError(Exception): pass
class AlgorithmError(Exception): pass