#from turtle import Screen
import pygame
import button
import os
from pygame.locals import K_ESCAPE
class OpeningScreen(pygame.sprite.Sprite):
    def __init__(self,w,h):
        self.image = pygame.transform.scale(pygame.image.load(os.path.join("img","openingscreen.png")),(w,h))
        #self.againtComputer_button = button.Button()
        self.running = True
def openingScreen(screen):
    opsc = OpeningScreen(screen.get_width(),screen.get_height())
    result = None
    multiplayer_btn = button.Button(width=(screen.get_width()*0.28),height=screen.get_height()*0.16,text="Multiplayer",x=(screen.get_width()*0.185),y=(screen.get_height()*0.67),fontsize=50,padding=10,bg=(6, 167, 25),fg=(255,255,255))
    computer_btn = button.Button(width=(screen.get_width()*0.31),height=screen.get_height()*0.155,text="Against AI",x=(screen.get_width()*0.572),y=(screen.get_height()*0.68),fontsize=50,padding=10,bg=(6, 167, 25),fg=(255,255,255))
    exit_btn = button.Button(width=(screen.get_width()*0.24),height=screen.get_height()*0.077,text="Exit",x=(screen.get_width()*0.725),y=(screen.get_height()*0.89),fontsize=30,padding=5,bg=(6, 167, 25),fg=(255,255,255))
    while not result:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                result = "ESC"
        keys = pygame.key.get_pressed()
        if keys[K_ESCAPE]: result = "ESC"
        if pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos()
            if multiplayer_btn.isClicked(pos): result = "MULTI"
            elif computer_btn.isClicked(pos): result = "AI"
            elif exit_btn.isClicked(pos): result = "ESC"


        screen.blit(opsc.image,(0,0))
        screen.blit(multiplayer_btn.image, multiplayer_btn.rect)
        screen.blit(computer_btn.image, computer_btn.rect)
        screen.blit(exit_btn.image, exit_btn.rect)
        pygame.display.flip()
    return result

class EndingScreen(pygame.sprite.Sprite):
    def __init__(self,w,h):
        self.image = pygame.transform.scale(pygame.image.load(os.path.join("img","endingscreen.png")),(w,h))
        #self.againtComputer_button = button.Button()
        self.running = True
def endingScreen(screen,msg="TESTMESSAGE"):
    opsc = EndingScreen(screen.get_width(),screen.get_height())
    result = None
    font = pygame.font.SysFont('Arial',48)
    pgtext = font.render(msg, True, (255,255,255), (6, 167, 25))
    pgtextrect = pgtext.get_rect()
    pgtextrect.centerx, pgtextrect.centery = screen.get_width()*0.5, screen.get_height()*0.6
    
    continue_btn = button.Button(width=(screen.get_width()*0.312),height=screen.get_height()*0.155,text="Continue",x=(screen.get_width()*0.3),y=(screen.get_height()*0.76),fontsize=50,padding=10,bg=(6, 167, 25),fg=(255,255,255))
    exit_btn = button.Button(width=(screen.get_width()*0.24),height=screen.get_height()*0.077,text="Exit",x=(screen.get_width()*0.724),y=(screen.get_height()*0.89),fontsize=30,padding=5,bg=(6, 167, 25),fg=(255,255,255))
    
    while not result:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: result = "ESC"
        keys = pygame.key.get_pressed()
        if keys[K_ESCAPE]: result = "ESC"
        if pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos()
            if continue_btn.isClicked(pos): result = "CONT"
            elif exit_btn.isClicked(pos): result = "ESC"


        screen.blit(opsc.image,(0,0))
        screen.blit(pgtext,pgtextrect)
        screen.blit(continue_btn.image, continue_btn.rect)
        screen.blit(exit_btn.image, exit_btn.rect)
        pygame.display.flip()
    return result


if __name__=="__main__":
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode([1000,600],pygame.NOFRAME)
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    result = endingScreen(screen)