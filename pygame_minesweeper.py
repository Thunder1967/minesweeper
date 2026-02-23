import sys
import pygame
import os
import random
import math

#主界面

#setting
Width = 500
Height = 600
GRAY = (225,225,225)
LIGHTBLUE = (0,255,255)
NumberColor = [(0,38,255),(0,180,33),(215,0,0),(240,105,0),(175,0,255),(242,193,0),(128,128,128),(0,20,128)]
sys.setrecursionlimit(10000)

#初始化
pygame.init()
screen = pygame.display.set_mode((Width,Height))
screen.fill(GRAY)
pygame.display.set_caption('踩地雷')
timer = pygame.time.Clock()


#變數
Running = True #遊戲是否運行
SceneIndex = 0 #場景
Game_Width,Game_Height,Game_Bomb = 9,9,10 #存地圖大小和地雷數
BlockSize = 50 #存單格區塊大小(50~30)
GameStorer=[] #存地圖
GameBlock=[] #存覆蓋層物件
StartPointInGameScene = [0,0] #地塊生成起始點
Hint = False #是否有提示
AutoClick = None

#NoCover = 0 #已點開格數
#GameTime = 0 #遊戲時間
#GameOver = 0 #遊戲是否結束
#DigCount = 0 #紀錄挖掘次數
#SafeBlock = 0 #安全格數
#GameSlider = None #遊戲滑條
#GameScreen = None #遊戲螢幕
#GameScene = None #遊戲主畫面
#SettingSprites = None #設定物件


#載入圖片、字體
Bomb_img = pygame.image.load(os.path.join("img","sweeper.png")).convert()
Bomb_img.set_colorkey(LIGHTBLUE)
flag_img = pygame.image.load(os.path.join("img","flag.png")).convert()
flag_img.set_colorkey(LIGHTBLUE)
clock_img = pygame.image.load(os.path.join("img","clock.png")).convert()
clock_img.set_colorkey(LIGHTBLUE)
house_img = pygame.image.load(os.path.join("img","house.png")).convert()
info_img = pygame.image.load(os.path.join("img","info.png")).convert()
Chinese_font = os.path.join("TaipeiSansTCBeta-Regular.ttf")
pygame.display.set_icon(Bomb_img)


#定義物件
class Button(pygame.sprite.Sprite):
    def __init__(self,mod):
        pygame.sprite.Sprite.__init__(self)
        if mod==0:#start
            self.image = pygame.font.SysFont(None,50).render('Start',True,(0,0,0))
            self.rect = self.image.get_rect()
            self.rect.center = (Width/2,320)

        elif mod==1:#setting
            self.image = pygame.font.SysFont(None,50).render('Setting',True,(0,0,0))
            self.rect = self.image.get_rect()
            self.rect.center = (Width/2,380)

        elif mod==2:#home
            self.image = pygame.transform.scale(house_img,(40,40))
            self.rect = self.image.get_rect()
            self.rect.topleft = (430,37)

        elif mod==3:#info
            self.image = pygame.transform.scale(info_img,(40,40))
            self.rect = self.image.get_rect()
            self.rect.topleft = (380,37)

        elif mod==4:#easy
            self.image = pygame.font.Font(Chinese_font,25).render("[簡單](9x9 10)" ,True,(0,255,33))
            self.rect = self.image.get_rect()
            self.rect.topleft = (180,385)

        elif mod==5:#normal
            self.image = pygame.font.Font(Chinese_font,25).render("[中等](16x16 40)" ,True,(255,216,0))
            self.rect = self.image.get_rect()
            self.rect.topleft = (180,425)

        elif mod==6:#hard
            self.image = pygame.font.Font(Chinese_font,25).render("[困難](30x16 99)" ,True,(255,0,0))
            self.rect = self.image.get_rect()
            self.rect.topleft = (180,465)

        elif mod==7:#hint
            self.image = pygame.font.Font(Chinese_font,25).render("[開啟]" ,True,(0,255,33))
            self.rect = self.image.get_rect()
            self.rect.topleft = (115,513)

class Slider(pygame.sprite.Sprite):
    def __init__(self,x:int,y:int,width:int,height:int,isbalance:bool=True,headcolor:tuple[int,int,int]=(10,10,10),bodycolor:tuple[int,int,int]=(180,180,180),step:int=1,max:int=99,min:int=0,value:int=0):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((Width,Height)).convert_alpha()
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.topleft = (0,0)
        self.body = pygame.Surface((width,height)).convert()
        self.body.fill(bodycolor)
        self.x = x
        self.y = y
        self.head = SliderHead(x,y,width,height,isbalance,headcolor,height/1.4 if isbalance else width/1.4,step,max,min,value)
        self.group = pygame.sprite.Group()
        self.group.add(self.head)

    def update(self):
        self.image.fill((0,0,0))
        self.image.blit(self.body,(self.x,self.y))
        self.head.run()
        self.group.draw(self.image)

class SliderHead(pygame.sprite.Sprite):
     SliderEvent = None
     enable = False
     def __init__(self,x,y,width,height,isbalance,headcolor,radius,step,max,min,value):   
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.isbalance = isbalance
        radius = math.ceil(radius)
        self.Max = max
        self.Min = min
        self.step = step
        self.mousepos = None
        self.value = value//self.step*self.step
        self.total = max - min
        self.rate = (self.value-self.Min)/self.total if self.total != 0 else 0
        self.pos = self.x+self.rate*width if self.isbalance else self.y+self.rate*height
        self.canmove = False
        self.image = pygame.Surface((radius*2,radius*2)).convert_alpha()
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        pygame.draw.circle(self.image,headcolor,(radius,radius),radius)
        self.rect.center = (self.pos, self.y+self.height/2) if self.isbalance else (self.x+self.width/2, self.pos)

     def run(self):
        if  not(self.enable):
            self.mousepos = None
            self.canmove = False
            return
        if self.isbalance:
            if self.rect.collidepoint(self.SliderEvent.pos) or self.canmove:
                self.canmove = True
                if self.mousepos != None:
                    self.pos += (self.SliderEvent.pos[0]-self.mousepos[0])
                    if self.pos < self.x:
                        self.pos = self.x
                    elif self.pos > self.x+self.width:
                        self.pos = self.x+self.width
                
                self.mousepos = self.SliderEvent.pos
            
            self.rect.center = (self.pos, self.y+self.height/2)
        
        else:
            if self.rect.collidepoint(self.SliderEvent.pos) or self.canmove:
                self.canmove = True
                if self.mousepos != None:
                    self.pos += (self.SliderEvent.pos[1]-self.mousepos[1])
                    if self.pos < self.y:
                        self.pos = self.y
                    elif self.pos > self.y+self.height:
                        self.pos = self.y+self.height
                
                self.mousepos = self.SliderEvent.pos
            
            self.rect.center = (self.x+self.width/2, self.pos)

        self.rate = (self.pos-self.x)/self.width if self.isbalance else (self.pos-self.y)/self.height
        self.value = (self.rate*self.total+self.Min)//self.step*self.step
    
     def setrange(self,min:int,max:int):
        self.total = max - min
        self.Min,self.Max = min,max
        if self.total == 0:
            self.rate = 0

        self.pos = self.x+self.rate*self.width if self.isbalance else self.y+self.rate*self.height
        self.rect.center = (self.pos, self.y+self.height/2) if self.isbalance else (self.x+self.width/2, self.pos)
        self.value = (self.rate*self.total+self.Min)//self.step*self.step
    
     def setvalue(self,value):
         self.value = value//self.step*self.step
         self.rate = (self.value-self.Min)/self.total if self.total != 0 else 0
         self.pos = self.x+self.rate*self.width if self.isbalance else self.y+self.rate*self.height

class Block(pygame.sprite.Sprite):
    def __init__(self,x,y,value):
        pygame.sprite.Sprite.__init__(self)
        self.PosX = x
        self.PosY = y
        self.Value = value
        self.Enabled = True
        self.Flaged = False
        self.Text = pygame.font.SysFont(None,int(BlockSize * 1))
        self.BottomColor = (230,195,160) if (x+y)%2==0 else (216,178,140)
        self.CoverColor = (170,215,80) if (x+y)%2==0 else (154,198,71)
        self.image = pygame.Surface((BlockSize,BlockSize)).convert()
        self.image.fill(self.CoverColor)
        self.rect = self.image.get_rect()
        self.rect.topleft = [y*BlockSize, x*BlockSize]
        self.add(GameSprites)

    def PutFlag(self):
        global Flag
        if self.Enabled:
            if not(self.Flaged) and Flag.value != 0:
                self.image.blit(pygame.transform.scale(flag_img,(BlockSize,BlockSize)),(0,0))
                Flag.value-=1
            elif self.Flaged:
                self.image.fill(self.CoverColor)
                Flag.value+=1
            else: return
            self.Flaged = not(self.Flaged)

    def RemoveCover(self):
        global NoCover,GameOver
        if self.Enabled and not(self.Flaged):
            self.Enabled = False
            NoCover+=1
            self.image.fill(self.BottomColor)
            if self.Value==9:
                self.image.blit(pygame.transform.scale(Bomb_img,(BlockSize*0.9,BlockSize*0.9)),(BlockSize*0.05,BlockSize*0.05))
                for x in range(Game_Height):
                    for y in range(Game_Width):
                        GameBlock[x][y].End()
                GameOver = 1

            elif self.Value!=0:
                self.image.blit(self.Text.render(str(self.Value),True,NumberColor[self.Value-1]),(BlockSize/3, BlockSize/5))

            if self.Value==0:
                for x in range(-1,2):
                    for y in range(-1,2):
                        if (self.PosX+x)>=0 and (self.PosX+x)<Game_Height and (self.PosY+y)>=0 and (self.PosY+y)<Game_Width:
                            GameBlock[self.PosX+x][self.PosY+y].RemoveCover()
            return True
        return False

    def End(self):
        if  self.Value==9 and self.Enabled:
            self.image.blit(pygame.transform.scale(Bomb_img,(BlockSize*0.9,BlockSize*0.9)),(BlockSize*0.05,BlockSize*0.05))
        self.Enabled =False

class Scoreboard(pygame.sprite.Sprite):
    def __init__(self,size,value,pos):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.value = value
        self.Enabled = True
        self.Text = pygame.font.SysFont(None,size)
        self.image = self.Text.render(str(self.value),True,(0,0,0))
        self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    
    def update(self):
        self.image = self.Text.render(str(self.value),True,(0,0,0))

class Mark(pygame.sprite.Sprite):
    def __init__(self,image,pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

#設定物件
Start_sprites,GameSprites,Sprites,Slider_Sprites = pygame.sprite.Group(),pygame.sprite.Group(),pygame.sprite.Group(),pygame.sprite.Group()
start_button,setting_button,home_button,info_button = Button(0),Button(1),Button(2),Button(3)
difficulty_button = [Button(4),Button(5),Button(6),Button(7)]
Flag = Scoreboard(50,0,(70,37)) #旗子數
GameClock = Scoreboard(50,0,(230,37)) #遊戲計時
Start_sprites.add(start_button,setting_button,Mark(pygame.font.Font(Chinese_font,90).render("踩地雷",True,(0,0,0)),(115,80)))

#遊戲迴圈
while Running:
    timer.tick(60)
    #取得輸入
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Running = False
            break

        #按下開始
        elif SceneIndex == 0 and event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.rect.collidepoint(event.pos):
                Wait = pygame.Surface((500,100))
                Wait.fill((0,0,0))
                Wait.set_alpha(200)
                Wait.blit(pygame.font.Font(Chinese_font,80).render("載入中..." ,True,(255,255,255)),(120,10))
                screen.blit(Wait,(0,Height/2-50))
                del Wait
                pygame.display.update()
                SceneIndex = 2
                
                #生成遊戲
                NoCover = 0
                Flag.value = Game_Bomb
                GameTime = 0
                GameClock.value = 0
                GameOver = 0
                DigCount = 0
                HintPoint =None
                AutoClick = None
                SafeBlock = Game_Width * Game_Height - Game_Bomb
                GameStorer.clear()
                GameSprites.empty()
                Sprites.empty()
                Slider_Sprites.empty()

                Sprites.add(Flag, GameClock, Mark(pygame.transform.scale(flag_img,(50,50)),(20,25)), Mark(pygame.transform.scale(clock_img,(50,50)),(180,25)), home_button, info_button)

                GameStorer=[[0 for y in range(Game_Width+2)] for x in range(Game_Height+2)]
                GameBlock.clear()
                GameBlock=[[0 for y in range(Game_Width)] for x in range(Game_Height)]

                for i in range(Game_Bomb):
                    while True:
                        a,b=random.randint(1,Game_Height),random.randint(1,Game_Width)
                        if GameStorer[a][b] == 0:
                            GameStorer[a][b]=9
                            break
                
                for x in range(1,Game_Height+1):
                    for y in range(1,Game_Width+1):
                        if GameStorer[x][y]==0:
                            count=0
                            for i in range(-1,2):
                                for j in range(-1,2):
                                    if i==0 and j==0:
                                        continue
                                    if(GameStorer[x+i][y+j]==9):
                                        count+=1
                            GameStorer[x][y]=count
                            if Hint and count==0 and (random.randint(1,100)>98 or HintPoint==None):
                                HintPoint=[x-1,y-1]

                
                #生成畫面
                StartPointInGameScene[0] = (500 - BlockSize*Game_Width)/2
                StartPointInGameScene[0] = StartPointInGameScene[0] if StartPointInGameScene[0]>=25 else 25
                StartPointInGameScene[1] = (500 - BlockSize*Game_Height)/2
                StartPointInGameScene[1] = StartPointInGameScene[1] if StartPointInGameScene[1]>=25 else 25

                GameSlider = [Slider(45,107,420,12,True,max=BlockSize * Game_Width+StartPointInGameScene[0]-(500-StartPointInGameScene[0])),Slider(8,145,12,420,False,max=BlockSize * Game_Height+StartPointInGameScene[1]-(500-StartPointInGameScene[1]))]
                Slider_Sprites.add(GameSlider[0],GameSlider[1])

                GameScreen = pygame.Surface((Width-StartPointInGameScene[0],500-StartPointInGameScene[1])).convert()
                GameScene = pygame.Surface((BlockSize * Game_Width+StartPointInGameScene[0], BlockSize * Game_Height+StartPointInGameScene[1])).convert()
                GameScene.fill(GRAY)
                for x in range(Game_Height):
                    for y in range(Game_Width):
                        GameBlock[x][y] = Block(x,y,GameStorer[x+1][y+1])
                if Hint and HintPoint!=None:
                    GameBlock[HintPoint[0]][HintPoint[1]].image.fill((255,216,0))

            #按下設定
            elif setting_button.rect.collidepoint(event.pos):
                SceneIndex = 1
                screen.fill(GRAY)
                Text = pygame.font.Font(Chinese_font,30)
                SettingSprites = [Slider(180,105,200,15,min=10,max=50,value=BlockSize,step=1),Scoreboard(40,9,(400,100)),Mark(Text.render("地塊大小:",True,(0,0,0)), (40,95)),
                                  Slider(180,155,200,15,min=1,max=100,value=Game_Width),Scoreboard(40,9,(400,150)),Mark(Text.render("地圖寬度:",True,(0,0,0)), (40,145)),
                                  Slider(180,205,200,15,min=1,max=100,value=Game_Height),Scoreboard(40,9,(400,200)),Mark(Text.render("地圖高度:",True,(0,0,0)), (40,195)),
                                  Slider(180,255,200,15,min=1,max=Game_Width*Game_Height,value=Game_Bomb),Scoreboard(40,9,(400,250)),Mark(Text.render("地雷數量:",True,(0,0,0)), (40,245)),
                                  Scoreboard(40,9,(210,300)),Mark(Text.render("地雷覆蓋率:",True,(0,0,0)), (40,295))]
                BlockCount = Game_Width*Game_Height
                for i in range(0,12):
                    if i%3 == 0:
                        Slider_Sprites.add(SettingSprites[i])
                    else:
                        Sprites.add(SettingSprites[i])
                Sprites.add(home_button,SettingSprites[12],SettingSprites[13],difficulty_button[0],difficulty_button[1],difficulty_button[2],difficulty_button[3],Mark(Text.render("推薦設定:",True,(0,0,0)),(40,380)),Mark(Text.render("提示:",True,(0,0,0)),(40,510)))
                del Text

        #遊戲中點擊
        elif SceneIndex == 1 and event.type == pygame.MOUSEBUTTONDOWN:
            if difficulty_button[0].rect.collidepoint(event.pos):
                SettingSprites[3].head.setvalue(9)
                SettingSprites[6].head.setvalue(9)
                BlockCount = SettingSprites[3].head.value * SettingSprites[6].head.value
                SettingSprites[9].head.setrange(1,BlockCount)
                SettingSprites[9].head.setvalue(10)
            elif difficulty_button[1].rect.collidepoint(event.pos):
                SettingSprites[3].head.setvalue(16)
                SettingSprites[6].head.setvalue(16)
                BlockCount = SettingSprites[3].head.value * SettingSprites[6].head.value
                SettingSprites[9].head.setrange(1,BlockCount)
                SettingSprites[9].head.setvalue(40)
            elif difficulty_button[2].rect.collidepoint(event.pos):
                SettingSprites[3].head.setvalue(30)
                SettingSprites[6].head.setvalue(16)
                BlockCount = SettingSprites[3].head.value * SettingSprites[6].head.value
                SettingSprites[9].head.setrange(1,BlockCount)
                SettingSprites[9].head.setvalue(99)
            elif difficulty_button[3].rect.collidepoint(event.pos):
                if Hint:
                    difficulty_button[3].image = pygame.font.Font(Chinese_font,25).render("[開啟]" ,True,(0,255,33))
                    Hint=False
                else:
                    difficulty_button[3].image = pygame.font.Font(Chinese_font,25).render("[關閉]" ,True,(255,0,0))
                    Hint=True
        elif SceneIndex == 2 and event.type == pygame.MOUSEBUTTONDOWN:
            x,y=event.pos[0],event.pos[1]
            if x>StartPointInGameScene[0] and x<Width and y>StartPointInGameScene[1]+100 and x<Height:
                try:
                    x = int((event.pos[0] - StartPointInGameScene[0] + GameSlider[0].head.value) // BlockSize)
                    y = int((event.pos[1] - StartPointInGameScene[1] - 100 + GameSlider[1].head.value) // BlockSize)
                    if pygame.mouse.get_pressed()[0]:
                        if GameBlock[y][x].RemoveCover():
                            DigCount += 1
                        else:
                            if AutoClick == None:
                                AutoClick=[x,y]
                            elif AutoClick[0]==x and AutoClick[1]==y:
                                for i in range(-1,2):
                                    for j in range(-1,2):
                                        try:
                                            if y+i<0 or x+j<0:
                                                continue
                                            elif GameBlock[y+i][x+j].RemoveCover():
                                                DigCount += 1
                                        except:
                                            pass
                                AutoClick=None
                            else:
                                AutoClick=None

                    elif pygame.mouse.get_pressed()[2]:
                        GameBlock[y][x].PutFlag()
                except:
                    pass
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
            SliderHead.enable = not(SliderHead.enable)
        if event.type == pygame.MOUSEMOTION:
            SliderHead.SliderEvent = event
        if (SceneIndex == 1 or SceneIndex == 2) and event.type == pygame.MOUSEBUTTONDOWN and home_button.rect.collidepoint(event.pos):
            SceneIndex = 0
            Sprites.empty()
            Slider_Sprites.empty()

    #更新遊戲
    if SceneIndex == 2:
        if GameOver == 0 and DigCount>0:
            GameTime += timer.get_time()/1000
            GameClock.value = int(GameTime//1)

        if GameOver == 0 and DigCount>0 and NoCover == SafeBlock:
            GameOver = 3
            GameOverIcon = pygame.Surface((Width,100))
            GameOverIcon.convert()
            GameOverIcon.fill((0,0,0))
            GameOverIcon.blit(pygame.font.SysFont(None,100).render("YOU WIN",True,(255,255,255)),(95,20))
            GameOverIcon.set_alpha(200)
            Sprites.add(Mark(GameOverIcon,(0,Height/2-50)))
        
        if GameOver == 1:
            GameOver = 3
            GameOverIcon = pygame.Surface((Width,100))
            GameOverIcon.convert()
            GameOverIcon.fill((0,0,0))
            GameOverIcon.blit(pygame.font.SysFont(None,100).render("GAMEOVER",True,(255,255,255)),(45,20))
            GameOverIcon.set_alpha(200)
            Sprites.add(Mark(GameOverIcon,(0,Height/2-50)))
    elif SceneIndex == 1:
        if BlockCount!=SettingSprites[3].head.value * SettingSprites[6].head.value:
            BlockCount = SettingSprites[3].head.value * SettingSprites[6].head.value
            SettingSprites[9].head.setrange(1,BlockCount)

        for i in range(0,12,3):
            SettingSprites[i+1].value = int(SettingSprites[i].head.value)
        SettingSprites[12].value = "%.2f%s"%(SettingSprites[9].head.value*100/BlockCount,"%")
        BlockSize,Game_Width,Game_Height,Game_Bomb = int(SettingSprites[0].head.value),int(SettingSprites[3].head.value),int(SettingSprites[6].head.value),int(SettingSprites[9].head.value)

    Sprites.update()
    Slider_Sprites.update()

    #更新畫面
    screen.fill(GRAY)
    if SceneIndex == 0:
        Start_sprites.draw(screen)
    elif SceneIndex == 2:
        GameSprites.draw(GameScene)
        GameScreen.blit(GameScene,(-GameSlider[0].head.value,-GameSlider[1].head.value))
        screen.blit(GameScreen,(StartPointInGameScene[0],(100+StartPointInGameScene[1])))
    Slider_Sprites.draw(screen)
    Sprites.draw(screen)

    if SceneIndex == 2 and info_button.rect.collidepoint(pygame.mouse.get_pos()):
            GameInfo = pygame.Surface((200,195))
            GameInfo.fill((140,140,140))
            GameInfo.blit(pygame.font.Font(Chinese_font,20).render("地圖大小: %d x %d" % (Game_Width,Game_Height) ,True,(255,255,255)),(5,10))
            GameInfo.blit(pygame.font.Font(Chinese_font,20).render("地塊總數: %d" % (Game_Width*Game_Height) ,True,(255,255,255)),(5,35))
            GameInfo.blit(pygame.font.Font(Chinese_font,20).render("地雷總數: %d" % (Game_Bomb) ,True,(255,255,255)),(5,60))
            GameInfo.blit(pygame.font.Font(Chinese_font,20).render("地雷覆蓋率: %.2f%s" % (Game_Bomb*100/(Game_Width*Game_Height),"%") ,True,(255,255,255)),(5,85))
            GameInfo.blit(pygame.font.Font(Chinese_font,20).render("挖掘次數: %d" % (DigCount) ,True,(255,255,255)),(5,110))
            GameInfo.blit(pygame.font.Font(Chinese_font,20).render("已挖掘地塊數: %d" % (NoCover) ,True,(255,255,255)),(5,135))
            GameInfo.blit(pygame.font.Font(Chinese_font,20).render("已標記地塊數: %d" % (Game_Bomb - Flag.value) ,True,(255,255,255)),(5,160))
            screen.blit(GameInfo,((260,80)))
    
    pygame.display.update()
pygame.quit()
sys.exit()