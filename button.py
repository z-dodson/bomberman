import pygame # maybe this is needed...
import threading # I was struggling to make it more effecient
class Button(pygame.sprite.Sprite):
    """This is actually useful"""
    def __init__(self, width, height, x, y, padding, text,fontsize=20, fg=(0,0,0), bg=(255,255,255)):
        super().__init__()
        font = pygame.font.SysFont("Arial",fontsize)
        self.image = pygame.surface.Surface([width,height])
        self.image.fill(bg)
        pgtext = font.render(text, True, fg, bg)
        pgtextrect = pgtext.get_rect()
        pgtextrect.x, pgtextrect.y = padding, padding
        self.image.blit(pgtext,pgtextrect)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x1 = x
        self.y1 = y
        self.x2 = width + x
        self.y2 = height + y
        self.threads = [] # I feel like this is really realy bad practice but I cant see an easy way around it
        
    def bind(self, function): 
        """Assigns a function to run when clicked""" 
        self.clickFunction = function # wow this works
        
    def click(self,position):
        print("CLICK TEST")
        x = position[0]
        y = position[1]
        if(self.x1<x<self.x2)and(self.y1<y<self.y2): 
            print("CLICKED")
            self.threads.append(threading.Thread(target=self.clickFunction, daemon=True))
            self.threads[len(self.threads)-1].start()
    
    def isClicked(self,position):
        x = position[0]
        y = position[1]
        if(self.x1<x<self.x2)and(self.y1<y<self.y2): return True
        else: return False
