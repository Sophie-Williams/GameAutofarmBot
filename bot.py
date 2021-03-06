import win32gui
from PIL import ImageGrab, ImageOps
import pyautogui
import time
from numpy import *
from multiprocessing import Process

#pyautogui.PAUSE = 1
pyautogui.FAILSAFE = False

class Window:
    top = 0
    left = 0
    bottom = 0
    right = 0
    width = 0
    height = 0
    blockSize = 86

colorRGB ={
    'doorGreyBorder' : (162, 162, 162),
    'pastelBackground' : (96, 213, 240),
    'playerColor1':(125, 95, 83),
    'playerColor2':(138, 106, 93),
    'playerColor3':(153, 117, 102),
    'playerColor4':(166, 127, 111),

}

def colorValue(which):
    c = colorRGB[which]
    return c[0]+c[1]+c[2]


Speeds ={
    #in seconds
    'punch3' : 0.317,#3hit with picaxe
    'punch4': 0.53,
    'punch6': 0.928,#6hit
    #walk one tile
    'right' : 0.062,
    'left' : 0.062,
    'turnRight': 0.01,
    'turnLeft': 0.01,
    #jump one tile
    'jump' : 0.1,
    #jump two
    'jump2' : 0.1,
    'jump3' : 0.1,
    'delay' : 1,
    "mouseCenter":0.3,
    "mouseTop":0.3,
    "mouseTop2":0.3,
    "mouseBottom":0.3,
    "mouseBottom":0.3,
    "mouseTop2punch6":0.928,
    "mouseTop2punch6":0.928
}

def getWindow(hwnd, extra):

    name = win32gui.GetWindowText(hwnd)
    if name == "Growtopia":
        rect = win32gui.GetWindowRect(hwnd)
        x1 = rect[0]
        y1 = rect[1]
        x2 = rect[2]
        y2 = rect[3]
        Window.left = x1+8
        Window.top = y1+31
        Window.right = x2-8
        Window.bottom = y2-6
        width = Window.right-Window.left
        height = Window.bottom-Window.top
        Window.width = width
        Window.height = height
        print("\t x1 %d, y1 %d, x2 %d, y2 %d)" % (x1, y1,x2,y2))
        print("\t    Size: (%d, %d)" % (width, height))


def mouseMove(x,y):
    pyautogui.moveTo(x+Window.left,y+Window.top)

def mouseClick(x,y):
    pyautogui.click(x + Window.left, y + Window.top)


def getPlayerCoordinates(divider = 1):
    img = screenshot(Window.left,Window.top,Window.right,Window.bottom)
    #Window.width,Window.height,Window.blockSize
    bl = Window.blockSize
    step = 0
    def makeStep():
        nonlocal step,bl,divider
        step = int(bl/divider)

    step = step if step > 2 else 2

    makeStep()
    c1 = colorRGB['playerColor1']
    c2 = colorRGB['playerColor2']
    c3 = colorRGB['playerColor3']
    c4 = colorRGB['playerColor4']
    sum1 = c1[0]+c1[1]+c1[2]
    sum2 = c2[0] + c2[1] + c2[2]
    sum3 = c3[0] + c3[1] + c3[2]
    sum4 = c4[0] + c4[1] + c4[2]

    imgX =0
    imgY = 0

    def findPerson():
        nonlocal sum,sum1,sum2,sum3,sum4,c1,c2,c3,c4,imgX,imgY,step,divider
        for y in range(step,Window.height,step):
            for x in range(step,Window.width,step):
                px = img.getpixel((x,y))
                sum = px[0]+px[1]+px[2]
                if sum == sum2 or sum == sum1 or sum == sum3 or sum == sum4:
                    if px == c2 or px == c1 or px == c3 or px ==c4:
                       imgX = x
                       imgY = y
                       return
        divider +=1
        makeStep()
        findPerson()

    findPerson()
   # findPerson()
   # mouseMove(imgX,imgY)
   # time.sleep(3)
   # findPerson()


    #get center of player
    centerY1 =0
    centerY2 = 0
    centerX1 = 0
    centerX2 = 0

    imgH = Window.height
    imgW = Window.width

    plusBlX = imgX + bl
    minusBlX = imgX -bl
    plusBlY = imgY+bl
    minusBlY = imgY-bl

    if plusBlX > imgW:
        plusBlX = imgW
    if minusBlX < 0:
        minusBlX = 0
    if plusBlY > imgH:
        plusBlY = imgH
    if minusBlY < 0:
        minusBlY = 0

    for x in range(minusBlX, imgX, 3):
        px = img.getpixel((x, imgY))
        sum = px[0] + px[1] + px[2]
        if sum == sum2 or sum == sum1 or sum == sum3 or sum == sum4:
            print("trigger X1")
            centerX1=x
            break
    for x in range(plusBlX, imgX, -3):
        px = img.getpixel((x, imgY))
        sum = px[0] + px[1] + px[2]
        if sum == sum2 or sum == sum1 or sum == sum3 or sum == sum4:
            print("trigger X2")
            centerX2=x
            break
    centerXX = centerX1 + (centerX2 - centerX1) / 2

    for y in range(minusBlY, imgY, 3):
        px = img.getpixel((centerXX, y))
        sum = px[0] + px[1] + px[2]
        if abs(sum-sum2)<4 or abs(sum-sum1)<4 or abs(sum-sum3)<4 or abs(sum-sum4)<4:
            print("trigger Y1")
            centerY1 = y
            break

    for y in range(plusBlY, imgY, -3):
        px = img.getpixel((centerXX, y))
        sum = px[0] + px[1] + px[2]
        if abs(sum - sum2) < 4 or abs(sum - sum1) < 4 or abs(sum - sum3) < 4 or abs(sum - sum4) < 4:
            print("trigger Y2")
            centerY2 = y
            break
    centerYY = centerY1+(centerY2-centerY1)/2
    return (centerXX,centerYY)

def getBlockSize():

    img = screenshot(Window.left,Window.top,Window.left+Window.width/3,Window.bottom)
    yCoordinate = 0
    pastelBackground = colorValue('pastelBackground')
    door = colorValue('doorGreyBorder')

    for y in range(Window.height):
        px = img.getpixel((0,y))
        sum = px[0]+px[1]+px[2]

        if sum != pastelBackground:
            yCoordinate = y
            break

    playerHasColor = False

    playerColorX =0
    playerColorY =0
    blockSize = 0
    def getFirstColor(yCoord):
        nonlocal playerColorY,playerColorX,playerHasColor,blockSize
        for x in range(int(Window.width/3-Window.left)):
            px = img.getpixel((x,yCoord))
            sum = px[0] + px[1] + px[2]

            if sum == pastelBackground:
               blockSize = x-1
               break
            if not playerHasColor and sum != door:
                playerColorX = x
                playerColorY = yCoord
                playerHasColor = True
        if not playerHasColor:
            getFirstColor(yCoord+1)

    getFirstColor(yCoordinate)

    Window.blockSize = blockSize
    #get the three remaining player colors:
    color1 = img.getpixel((playerColorX,playerColorY))

    colorRGB['playerColor1'] = color1
    checkColor = colorValue('playerColor1')
    counter = 1

    for x in range(playerColorX,blockSize):

        px = img.getpixel((x,playerColorY))
        sum = px[0] + px[1] + px[2]
        if sum != checkColor:
            counter +=1
            if counter == 4:
                playerColorX = x - 1
                break
            colorRGB['playerColor'+str(counter)] = px
            checkColor = sum

    for y in range(playerColorY,playerColorY+blockSize):
        px = img.getpixel((playerColorX, y))
        sum = px[0] + px[1] + px[2]
        if sum != checkColor:
            colorRGB['playerColor4'] = px
            break

    print("player colors: ",colorRGB['playerColor1'],colorRGB['playerColor2'],colorRGB['playerColor3'],colorRGB['playerColor4'])
    print("blockSize:",Window.blockSize)

def do(which):
    print(which)
    def keyDown(key, whichSpeed):
        pyautogui.keyDown(key)
        time.sleep(Speeds[whichSpeed])
        pyautogui.keyUp(key)

    #punch
    if (which == "punch6"):
        keyDown('space', which)
        return
    if (which == "punch4"):
        keyDown('space', which)
        return
    if (which == "punch3"):
        keyDown('space', which)
        return

    #move
    if (which == "right"):
        keyDown(which,which)
        return
    if (which == "left"):
        keyDown(which,which)
        return
    if (which == "turnLeft"):
        keyDown("left",which)
        return
    if (which == "turnRight"):
        keyDown("right", which)
        return

        # jump
    if (which == "jump"):
        keyDown('up', which)
        return
    if (which == "jump2"):
        keyDown('up', which)
        return
    if (which == "jump3"):
        keyDown('up', which)
        return
    #mouse
    def mouseClickL(multiX,multiY):
        co = getPlayerCoordinates()
        #print("player Center",co)
        bl = Window.blockSize
        print(co)
        mouseMove(co[0],co[1])
        #mouseClick(co[0]+(bl*multiX),co[1]+(bl*multiY))
        #mouseMove(co[0]+(bl*multiX),co[1]+(bl*multiY))

    if which == "mouseCenter":
        mouseClickL(0,0)
        return
    if which == "mouseTop":
        mouseClickL(0,-1)
        return
    if which == "mouseTop2":
        mouseClickL(0, -2)
        return
    if which == "mouseBottom":
        mouseClickL(0, 1)
        return
    if which == "mouseBottom2":
        mouseClickL(0, 2)
        return

    #if which == selectHand:
    #if which == selectSeeds:
    #if which == selectBlocks

#[action index[repeat index]]
def mover(moveArr,actionIndex,repeatIndex):
    print("action index: ",actionIndex, " repeat index: ",repeatIndex)
    if actionIndex == len(moveArr):
        return
    move = moveArr[actionIndex]
    if repeatIndex == move[0]:
        mover(moveArr,actionIndex+1,0)
        return
    speed1 = Speeds[move[1]]
    speed2 = Speeds[move[1]]
    delay = speed1 if speed1>speed2 else speed2
    for i in range(1,len(move)):
        do(move[i])
    time.sleep(2)
    mover(moveArr,actionIndex,repeatIndex+1)

def screenshot(x1,y1,x2,y2):
    return ImageGrab.grab((x1,y1,x2,y2))

def main():

    win32gui.EnumWindows(getWindow, None)

    getBlockSize()
    mouseClick(0,0)
  #  time1 =  time.time()

   # print(time.time()-time1)
    #arr = [[2,"right"],[96,"mouseCenter","right"]]
    #arr = [[1,"mouseCenter"]]
   # mover(arr,0,0)
    co = getPlayerCoordinates()
   # mouseMove(co[0],co[1])
  #  pyautogui.moveTo(coord[0],coord[1])
    arr = [[2,"right"],[5,"mouseCenter","right"]]
    mover(arr,0,0)
  #  img = screenshot(Window.left,Window.top,Window.right,Window.bottom)
   # img.save("D:/growtopia2.bmp")



main()
