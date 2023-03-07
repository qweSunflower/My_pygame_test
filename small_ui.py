import pygame
import random, time
from collections import deque, namedtuple
import typing
from typing import Self
from functools import partial

pygame.init()

FT_FONT_NAME = 'microsoftyahei'
FT_font = {25:pygame.font.SysFont(FT_FONT_NAME, 25)}
COLOR = {"red":(250, 50, 30), "blue":(50, 150, 250), "white":(240, 240, 240), "grey":(100,100,100)}
def get_FTfont(size:int, fontname:str=None):
    if size in FT_font:
        return FT_font[size]
    else:
        FT_font[size] = pygame.font.SysFont(FT_FONT_NAME, size)
        return FT_font[size]

def fuc_none(*arg, **args):
    pass

class Scene():
    def __init__(self) -> None:
        self.gameobj = {}
        pass
    def getobj(self, name):
        if name in self.gameobj:
            return self.gameobj[name]
    def addobj(self, gameobject):
        if not gameobject.name in self.gameobj:
            self.gameobj[gameobject.name] = gameobject
    def addobjs(self, *gameobjects):
        for gameobject in gameobjects:
            self.addobj(gameobject)
    def popobj(self, name):
        if name in self.gameobj:
            return self.gameobj.pop(name)
    def draw(self, screen):
        for name in self.gameobj:
            self.gameobj[name].draw(screen)
    def eventact(self, event:pygame.event.Event):
        for name in self.gameobj:
            self.gameobj[name].eventact(event)
    
class FloatBox_Scene(Scene):
    def __init__(self) -> None:
        super().__init__()
        self.now = None
    def eventact(self, event: pygame.event.Event):
        for name in self.gameobj:
            self.gameobj[name].eventact(event)
            if event.type == pygame.MOUSEBUTTONDOWN and self.gameobj[name].rect.collidepoint(*event.pos):
                self.now = self.gameobj[name]

class UIBase():
    def __init__(self, name:str, scene:Scene, coord:list, anchor:list=(0,0)) -> None:
        self.name = name
        if scene != None:
            self.scene = scene
            self.scene.addobj(self)
        self.rect = pygame.Rect(0,0,0,0)
        self.anchor =anchor
        self.setcoord(coord)
        '''self.children = {}
        pass
    def addchild(self, child:Self):
        if not child.name in self.children:
            self.children[child.name] = child
    def addchildren(self, *children):
        for child in children:
            self.addchild(child)'''
    def setcoord(self, coord:list):
        self.coord = list(coord)
        self.rect = pygame.Rect(0,0,self.rect.width,self.rect.height)
        self.rect.x = self.coord[0]- self.anchor[0]*self.rect.w
        self.rect.y = self.coord[1]-self.anchor[1]*self.rect.h
    def setrect(self, rect:pygame.Rect):
        self.rect = rect.copy()
        self.width = self.rect.w
        self.height = self.rect.h
        self.rect.x = self.coord[0]- self.anchor[0]*self.rect.w
        self.rect.y = self.coord[1]-self.anchor[1]*self.rect.h
    def movecoord(self, rel):
        self.coord[0] += rel[0]
        self.coord[1] += rel[1]
        self.setcoord(self.coord)
        #for name in self.children:
        #    self.children[name].movecoord(rel)
    def draw(self, screen:pygame.Surface):
        screen.blit(self.image, self.coord)
    def updata(self):
        pass
    def eventact(self, event:pygame.event.Event):
        pass

class ComposeBox(UIBase):
    def __init__(self, name: str, scene: Scene, coord: list, anchor: list=[0,0]) -> None:
        super().__init__(name, scene, coord, anchor)
        self.children = {}
    def addchild(self, child:UIBase):
        if not child.name in self.children:
            self.children[child.name] = child
    def addchildren(self, *children):
        for child in children:
            self.addchild(child)
    def getchild(self, name):
        if name in self.children:
            return self.children[name]
    def draw(self, screen: pygame.Surface):
        for name in self.children:
            self.children[name].draw(screen)
    def eventact(self, event: pygame.event.Event):
        for name in self.children:
            self.children[name].eventact(event)
    def setcoord(self, coord: tuple):
        super().setcoord(coord)
    def movecoord(self, rel):
        super().movecoord(rel)
        for name in self.children:
            self.children[name].movecoord(rel)
    
class RectBlock(UIBase):
    def __init__(self, name:str, scene:Scene, width:int, height:int, color:tuple, coord:list, anchor:list=[0,0], radius:int=0) -> None:
        super().__init__(name, scene, coord, anchor)
        self.color = color
        self.radius = radius
        self.rect = pygame.Rect(*self.coord,width, height)
        pass
    def draw(self, screen:pygame.Surface):
        pygame.draw.rect(screen, self.color, self.rect, 0, self.radius)

class IRectBlock(UIBase):
    def __init__(self, name:str, scene:Scene, width:int, height:int, color:tuple, coord:list, anchor:list=[0,0], radius:list=0) -> None:
        super().__init__(name, scene, coord, anchor)
        self.color = color
        self.radius = radius
        self.rect = pygame.Rect(*self.coord,width, height)
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.image.fill(self.color)

class ScaleBar(UIBase):
    def __init__(self, name:str, scene:Scene, length:int, height:int, color:tuple, keycolor:tuple, coord:list, fact=(1,0), anchor:list=[0,0]) -> None:
        super().__init__(name, scene, coord, anchor)
        self.color = color
        self.fact = fact
        self.fuc = fuc_none
        self.height = height
        self.length = length
        if fact[1] == 0:#横向
            self.height, self.length = self.length, self.height
            self.key = RectBlock(name+"_key", scene, length*0.1, height, keycolor, coord)
        else:
            self.key = RectBlock(name+"_key", scene, height, length*0.1, keycolor, coord)
        self.rect = pygame.Rect(*coord, self.height, self.length)
        self.setcoord(self.coord)
        self.setkeyrect(self.rect.copy())
        self.fl_down = False
        self.scalenum = 0.0

        pass
    def linkobj(self, obj):
        pass
    def linkfuc(self, fuc:fuc_none):
        self.fuc = fuc
        fuc(self.scalenum)
    def setkeyrect(self, pos:list):
        if self.fact[1] == 0:
            i = 0
        else:
            i = 1
        if pos[i] < self.rect[i]+self.rect[i+2]*0.95:
            if pos[i] > self.rect[i]+self.rect[i+2]*0.05:
                pass
            else:
                pos[i] = self.rect[i]+self.rect[i+2]*0.05
        else:
            pos[i] = self.rect[i]+self.rect[i+2]*0.95
        if self.fact[0] == 1 or self.fact[1] == 1:
            self.scalenum = (pos[i]-(self.rect[i]+self.rect[i+2]*0.05))/(self.rect[i+2]*0.9)
            
        else:
            self.scalenum = (self.rect[i+2]*0.95-pos[i]+self.rect[i])/(self.rect[i+2]*0.9)
        if self.fact[1] == 0:
            self.key.setcoord((pos[0]-self.rect[2]*0.05, self.rect[1]))
        else:
            self.key.setcoord((self.rect[0], pos[1]-self.rect[3]*0.05))
        self.fuc(self.scalenum)
    def eventact(self, event:pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1  and self.rect.collidepoint(*event.pos):
                self.fl_down = True
                self.startpos = event.pos
                self.setkeyrect(list(event.pos))
        elif event.type == pygame.MOUSEMOTION:
            if self.fl_down == True:
                self.setkeyrect(list(event.pos))
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.fl_down == True and event.button == 1:
                self.fl_down = False
        pass
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        self.key.draw(screen)

class SlideBox(ComposeBox):
    def __init__(self, name: str, scene: Scene, imgwidth:int, imgheight:int, area:pygame.Rect, coord:list, anchor:list=[0,0]) -> None:
        super().__init__(name, scene, coord, anchor)
        self.image = pygame.Surface((imgwidth,imgheight))
        self.image.fill(COLOR["blue"])
        if type(area) != pygame.Rect:
            area = pygame.Rect(*area)
        self.imgheight = imgheight
        self.imgwidth = imgwidth
        self.scalenum = [0.0, 0.0]
        self.speed = 5
        self.area = area
    def eventact(self, event:pygame.event.Event):
        if event.type == pygame.MOUSEWHEEL and self.rect.collidepoint(*pygame.mouse.get_pos()):
            self.area.top += event.y * self.speed
            if self.area.bottom > self.imgheight:
                self.area.bottom = self.imgheight
            elif self.area.top < 0:
                self.area.top = 0
            self.scalenum[0] = self.area.top/(self.imgheight - self.area.height)
    def changescalenumx(self, scalenum:int):
        self.scalenum[0] = scalenum
        self.setarea()
    def changescalenumy(self, scalenum:int):
        self.scalenum[1] = scalenum
        self.setarea()
    def setarea(self):
        self.area.x = (self.imgwidth - self.area.w)*self.scalenum[0]
        self.area.top = (self.imgheight - self.area.h)*self.scalenum[1]
    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.coord, self.area)

class FloatSlideBox(SlideBox):
    def __init__(self, name: str, scene: Scene, imgwidth:int, imgheight:int, area:pygame.Rect, coord:list, anchor:list=[0, 0]) -> None:
        super().__init__(name, scene, imgwidth, imgheight, area, coord, anchor)

def changeslidboxscalenum(obj:SlideBox, i, scalenum):
    obj.scalenum[i] = scalenum
    obj.setarea()

class Image(UIBase):
    def __init__(self, name:str, image:pygame.Surface, coord:list, anchor:list=[0,0]) -> None:
        self.image = image
        rect = self.image.get_rect()
        super().__init__(name, coord, anchor)
        pass


class Label(UIBase):
    def __init__(self, name:str, scene:Scene, font:pygame.font.Font, text:str, color:tuple, bgcolor:None, coord:list, anchor:list=[0,0]) -> None:
        super().__init__(name, scene, coord, anchor)
        self.font = font
        self.text = text
        self.color = color
        self.bgcolor = bgcolor
        self.prep()
        pass
    def reset(self, font:pygame.font.Font, text, color, coord:tuple, anchor=(0,0)):
        self.font = font
        self.text = text
        self.color = color
        self.coord = coord
        self.anchor = anchor
        self.prep()
        return self
    def change_text(self, text):
        self.text = text
        self.prep()
    def prep(self):
        self.image = self.font.render(self.text, True, self.color, self.bgcolor)

class Button(RectBlock):
    def __init__(self, name:str, scene:Scene, text:str, textcolor:tuple, font:pygame.font.Font, width:int, height:int, color:tuple, fuc:function, coord:list, anchor=[0,0], radius=0) -> None:
        super().__init__(name, scene, width, height, color, coord, anchor, radius)
        self.label = Label(name+"_label", scene, font, text, textcolor, self.rect.center, (0.5,0.5))
        self.fuc = fuc
    def eventact(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(*event.pos):
            self.fuc()
    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        self.label.draw(screen)

class Entry(Label):
    def __init__(self, name:str, scene: Scene, font: pygame.font.Font, minwidth:int, text:str, color:tuple, bgcolor:tuple=None, coord:list=[0,0], anchor:list=[0,0], fuc:function=fuc_none) -> None:
        self.minwidth = minwidth
        super().__init__(name, scene, font, text, color, bgcolor, coord, anchor)
        self.f_focus = False
        self.fuc = fuc
    def eventact(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(*event.pos):
                self.f_focus = True
            else:
                self.f_focus = False
        elif self.f_focus == True and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:# and len(self.text) > 0:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.fuc(self.text)
            else:
                self.text += event.unicode
            self.prep()
    def setrect(self, rect: pygame.Rect):
        super().setrect(rect)
        if self.rect.w < self.minwidth:
            self.rect.w = self.minwidth
            self.width = self.minwidth
    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        pygame.draw.rect(screen, (50,50,50), self.rect, 1)

class EntrySelect(Entry):
    def __init__(self, name, scene: Scene, font: pygame.font.Font, minwidth: int, text: str, color, bgcolor: None, coord:list, anchor=[0,0], fuc=None) -> None:
        super().__init__(name, scene, font, minwidth, text, color, bgcolor, coord, anchor, fuc)

class MenuNode(Label):
    def __init__(self, name, font: pygame.font.Font, text: str, color, bgcolor: None, coord:list, anchor=[0,0], fuc=fuc_none) -> None:
        super().__init__(name, None, font, text, color, bgcolor, coord, anchor)
        self.fuc = fuc
    

class ContextMenu(UIBase):
    def __init__(self, name: str, scene: Scene, width: int, height: int, coord:list, anchor:list=[0,0]) -> None:
        super().__init__(name, scene, coord, anchor)
        self.active = False
        self.menu = {}
    def draw(self, screen: pygame.Surface):
        return super().draw(screen)

class FloatBox(RectBlock):
    def __init__(self, name: str, scene: Scene, width: int, height: int, color: tuple, coord: list, anchor: list = [0, 0], radius: int = 0) -> None:
        super().__init__(name, scene, width, height, color, coord, anchor, radius)
        self.flag = [0,0]
        self.f_move = False
    def eventact(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            rect = self.rect
            n = 5
            if rect.x-n < pos[0] < rect.x+n:
                self.flag[0] = -1
            elif rect.right-n < pos[0] < rect.right+n:
                self.flag[0] = 1
            if rect.y-n < pos[1] < rect.y+n:
                self.flag[1] = -1
            elif rect.bottom-n < pos[1] < rect.bottom+n:
                self.flag[1] = 1
            elif rect.collidepoint(*pos):
                self.f_move = True
        elif  event.type == pygame.MOUSEMOTION:
            if self.flag != [0,0]:
                pos = event.pos
                flag = self.flag
                if flag[0] == -1:
                    self.width = self.rect.right - pos[0]
                    self.coord[0] = pos[0]
                elif flag[0] == 1:
                    self.width = pos[0] - self.rect.x
                if flag[1] == -1:
                    self.height = self.rect.bottom - pos[1]
                    self.coord[1] = pos[1]
                elif flag[1] == 1:
                    self.height = pos[1] - self.rect.y
                self.setcoord(self.coord)
            elif self.f_move == True:
                self.movecoord(event.rel)
        elif event.type == pygame.MOUSEBUTTONUP and (self.flag != [0,0] or self.f_move == True):
            self.flag = [0,0]
            self.f_move = False
    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.color, self.rect, 0)
        pygame.draw.rect(screen, COLOR["grey"], self.rect, 2)
        


def change_rect(obj:UIBase, text:str):
    l = text.split(",")
    obj.width = int(l[2])
    obj.height = int(l[3])
    obj.setcoord(( int(l[0]), int(l[1]) ))

def main():
    pygame.init()
    Height = 700
    Width = 1400
    screen = pygame.display.set_mode((Width, Height))
    screen_rect = screen.get_rect()
    pygame.display.set_caption("贪吃蛇")
    ts = pygame.time.Clock()
    global SC_1
    SC_1 = Scene()
    floatSC = FloatBox_Scene()
    font14 = get_FTfont(14)
    mainwindow = ComposeBox("mainwidow", SC_1, [0,0])
    mainwindowrect = pygame.Rect(0,0,Width-200, Height)
    mainwindow.addchildren(
        SlideBox("mianwindow", SC_1, 2000, 2000, pygame.Rect(0,0,Width-200,Height), (0,0)),
        ScaleBar("mainwindow_scalebarx", SC_1, mainwindowrect.width, 15, COLOR["white"], COLOR["grey"], (0, Height), (1,0), (0,1)),
        ScaleBar("mainwindow_scalebary", SC_1, Height, 15, COLOR["white"], COLOR["grey"], (mainwindowrect.right,0), (0,1), (1,0))
    )
    mainwindowslidebox = SC_1.getobj("mianwindow")
    SC_1.getobj("mainwindow_scalebarx").linkfuc(SC_1.getobj("mianwindow").changescalenumx)
    SC_1.getobj("mainwindow_scalebary").linkfuc(SC_1.getobj("mianwindow").changescalenumy)
    mainban = ComposeBox("mianban", SC_1, [0,0], [1,0])
    mainban.addchildren(
        RectBlock("mianban_bg", SC_1, 200, Height, COLOR["grey"], [0,0], [0,0]),
        Label("mianban_name_k", SC_1, font14, "name:", COLOR["white"], None, (5,0)),
        Label("mianban_name_v", SC_1, font14, "name", COLOR["white"], None, (60,0)),
        Label("mianban_rect_k", SC_1, font14, "rect:", COLOR["white"], None, (5,20)),
        Entry("mianban_rect_v", SC_1, font14, 20, "rect", COLOR["white"], None, (50,20), (0,0), fuc_none)
    )
    mainban.movecoord((Width-200,0))
    Streeobj = ComposeBox("streeobj", SC_1, [0,0])
    Streeobj.addchildren(
        mainwindow,
        mainban
    )
    mb_name = SC_1.getobj("mianban_name_v")
    mb_rect = SC_1.getobj("mianban_rect_v")
    floatbox = FloatBox("floatbox", SC_1, 100, 100, COLOR["blue"], screen_rect.center)
    floatSC.addobjs(floatbox)
    mb_rect_fuc =  partial(change_rect, floatbox)
    mb_rect.fuc = mb_rect_fuc

    global keep_going
    keep_going = True
    active = True
    FPS = 60
    jgtime = 0.0
    while keep_going:
        screen.fill(COLOR["white"])
        dt = ts.tick(FPS) / 1000 #帧率
        jgtime += dt
        
        for event in pygame.event.get():
            #print(event.type)
            floatSC.eventact(event)
            mb_rect.eventact(event)
            mainwindow.eventact(event)
            if event.type == pygame.QUIT:  # 退出事件
                keep_going = False
        
        if jgtime > 0.2:
            jgtime = 0.0
            if floatSC.now != None:
                mb_name.change_text(floatSC.now.name)
                if not mb_rect.f_focus:
                    mb_rect.change_text(str(floatSC.now.rect)[6:-2])

        floatSC.draw(mainwindowslidebox.image)
        Streeobj.draw(screen)
        pygame.display.update()  # 刷新屏幕
        
    pygame.quit()
    return 0

if __name__ == "__main__":
    main()

