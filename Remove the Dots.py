# Remove the Dots
#
# Delete groups of dots and try to get a high score

import random, pygame, sys
from pygame.locals import *

pygame.init()

FPS = 30
WINDOWWIDTH = 450
WINDOWHEIGHT = 670

BOARDWIDTH = 8
BOARDHEIGHT = 11
SPACESIZE = 50
BOARDWIDTHPIXELS = SPACESIZE * BOARDWIDTH
BOARDHEIGHTPIXELS = SPACESIZE * BOARDHEIGHT
XMARGIN = int((WINDOWWIDTH - BOARDWIDTHPIXELS) / 2)
YMARGIN = XMARGIN

BGCOLOR = (200, 85, 75) # pale red
BOARDCOLOR = (185, 235, 250) # blue
BORDERCOLOR = (0, 0, 0) # black
TEXTCOLOR = (135, 240, 115) # green
WINTEXTCOLOR = (0, 0, 0) # black
TEXTRECTCOLOR = (55, 115, 255) # blue
HIGHLIGHTCOLOR = (150, 80, 205) # purple

DOTIMAGEBLUE = pygame.image.load("blue-dot.png")
DOTIMAGEGREEN = pygame.image.load("green-dot.png")
DOTIMAGERED = pygame.image.load("red-dot.png")
DOTIMAGEYELLOW = pygame.image.load("yellow-dot.png")
DISPLAYICON = pygame.image.load("display-icon.png")

DELETESOUND = pygame.mixer.Sound("deletesound.ogg")

DOTSYMBOLS = ["b", "g", "r", "y"]
SYMBOLSTOIMAGES = {"b":DOTIMAGEBLUE, "g":DOTIMAGEGREEN, "r":DOTIMAGERED, "y":DOTIMAGEYELLOW}

def main():
    global FPSCLOCK, DISPLAYSURF, FONT

    FPSCLOCK = pygame.time.Clock()
    mouseX, mouseY = 0, 0
    
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption("Remove the Dots")
    pygame.display.set_icon(DISPLAYICON)
    FONT = pygame.font.Font('freesansbold.ttf', 36)

    board = createBoard()
    playerScore = 0
    dotsWorth = None
    dotsToHighlight = []
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mouseX, mouseY = event.pos
            elif event.type == MOUSEBUTTONUP:
                if dotsWorth:
                    DELETESOUND.play()
                    removeDots(dotsToHighlight, board)
                    dropDotRows(board)
                    shiftColumnsRight(board)
                    playerScore += dotsWorth
                dotsToHighlight = []
                dotsWorth = None

        dotHover = getDotAtPixel(mouseX, mouseY)
        if dotHover and not dotsWorth:
            dotsToHighlight = getDotGrouping(board, dotHover, dotHover, dotsToHighlight)
            if len(dotsToHighlight) == 1:
                dotsToHighlight = []
            else:
                dotsWorth = getScore(dotsToHighlight)
        elif not dotHover in dotsToHighlight and dotsWorth:
            dotsToHighlight = []
            dotsWorth = None
                
        draw(board, dotsToHighlight, playerScore, dotsWorth)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

        if isGameOver(board):
            return playAgainScreen(playerScore)

def createBoard():
    # Create a board filled with randomized dots
    board = []
    for x in range(BOARDWIDTH):
        row = []
        for y in range(BOARDHEIGHT):
            row.append(random.choice(DOTSYMBOLS))
        board.append(row)
    return board

def draw(board, dotsToHighlight, playerScore, dotsWorth):
    # Main rendering function
    drawBgAndBoard()
    drawBorder()
    drawDots(board)
    if len(dotsToHighlight) > 0:
        highlightDots(board, dotsToHighlight)
    drawText(playerScore, dotsWorth)

def drawBgAndBoard():
    # Fill the background and draw the empty board
    DISPLAYSURF.fill(BGCOLOR)
    pygame.draw.rect(DISPLAYSURF, BOARDCOLOR,
                     (XMARGIN, YMARGIN, BOARDWIDTHPIXELS, BOARDHEIGHTPIXELS))

def drawBorder():
    # Draw a border around the board
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR,
                     (XMARGIN - 3, YMARGIN - 3, BOARDWIDTHPIXELS + 5, BOARDHEIGHTPIXELS + 5), 4)

def drawDots(board):
    # Draw the dots on the board
    boardX, boardY = 0, 0
    for row in board:
        for space in row:
            if space != "":
                pixelX, pixelY = getLeftTopCoordsOfBox(boardX, boardY)
                DISPLAYSURF.blit(SYMBOLSTOIMAGES[space], (pixelX, pixelY))
            boardY += 1
        boardY = 0
        boardX += 1

def drawText(playerScore, dotsWorth):
    # Draw the player's score and how much a selected dot group is worth
    scoreText = "Current score: " + str(playerScore)
    scoreTextSurfaceObj = FONT.render(scoreText, True, TEXTCOLOR)
    scoreTextRectObj = scoreTextSurfaceObj.get_rect()
    scoreTextRectObj.topleft = (XMARGIN, BOARDHEIGHTPIXELS + XMARGIN + 10)
    DISPLAYSURF.blit(scoreTextSurfaceObj, scoreTextRectObj)

    if dotsWorth:
        dotsText = "Group is worth " + str(dotsWorth) + " points"
        dotsTextSurfaceObj = FONT.render(dotsText, True, TEXTCOLOR)
        dotsTextRectObj = dotsTextSurfaceObj.get_rect()
        dotsTextRectObj.center = (XMARGIN + BOARDWIDTHPIXELS / 2, YMARGIN + BOARDHEIGHTPIXELS + 65)
        DISPLAYSURF.blit(dotsTextSurfaceObj, dotsTextRectObj)

def highlightDots(board, dotsToHighlight):
    # Highlight the dots on the board that are in a list
    boardX, boardY = 0, 0
    for row in board:
        for space in row:
            if (boardX, boardY) in dotsToHighlight:
                pixelX, pixelY = getLeftTopCoordsOfBox(boardX, boardY)
                circleX, circleY = pixelX + int(SPACESIZE/2), pixelY + int(SPACESIZE/2)
                pygame.draw.circle(DISPLAYSURF, HIGHLIGHTCOLOR,
                                   (circleX, circleY), int(SPACESIZE/2), 3)
            boardY += 1
        boardY = 0
        boardX += 1

def getDotGrouping(board, oldDot, newDot, dotsInGroup):
    # Use recursion to find the dots connected to a clicked dot
    if board[oldDot[0]][oldDot[1]] != board[newDot[0]][newDot[1]] or board[oldDot[0]][oldDot[1]] == "":
        return dotsInGroup
    
    dotsInGroup.append(newDot)

    if newDot[0] > 0:
        adjDot = (newDot[0] - 1, newDot[1])
        if adjDot not in dotsInGroup:
            dotsInGroup = getDotGrouping(board, newDot, adjDot, dotsInGroup)
    if newDot[0] < BOARDWIDTH - 1:
        adjDot = (newDot[0] + 1, newDot[1])
        if adjDot not in dotsInGroup:
            dotsInGroup = getDotGrouping(board, newDot, adjDot, dotsInGroup)

    if newDot[1] > 0:
        adjDot = (newDot[0], newDot[1] - 1)
        if adjDot not in dotsInGroup:
            dotsInGroup = getDotGrouping(board, newDot, adjDot, dotsInGroup)
    if newDot[1] < BOARDHEIGHT - 1:
        adjDot = (newDot[0], newDot[1] + 1)
        if adjDot not in dotsInGroup:
            dotsInGroup = getDotGrouping(board, newDot, adjDot, dotsInGroup)
            
    return dotsInGroup
            
def getDotAtPixel(pixelX, pixelY):
    # Get the dot containing a certain pixel
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            left, top = getLeftTopCoordsOfBox(x, y)
            dotRect = pygame.Rect(left, top, SPACESIZE, SPACESIZE)
            if dotRect.collidepoint(pixelX, pixelY):
                return (x, y)
    return None

def removeDots(dotList, board):
    # Remove dots in a group from the board
    for dot in dotList:
        board[dot[0]][dot[1]] = ""

def dropDotRows(board):
    # Move dots with empty space beneath them down the board
    for x in range(BOARDWIDTH):
        blankNumber = 0
        for space in board[x]:
            if space == "":
                blankNumber += 1
        for i in range(blankNumber):
            board[x].remove("")
        for i in range(blankNumber):
            board[x].insert(0, "")

def shiftColumnsRight(board):
    # Shift columns into empty space to the right
    for x in range(BOARDWIDTH):
        blankColumns = 0
        if board[x] == ["", "", "", "", "", "", "", "", "", "", ""]:
            blankColumns += 1
        for i in range(blankColumns):
            del board[x]
        for i in range(blankColumns):
            board.insert(0, ["", "", "", "", "", "", "", "", "", "", ""])

def isGameOver(board):
    # Check if there are any dot groups left to delete
    dotGroups = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            dotGrouping = getDotGrouping(board, (x, y), (x, y), [])
            if len(dotGrouping) > 1:
                dotGroups.append(dotGrouping)

    return len(dotGroups) == 0

def getScore(dotList):
    # Find how many points a group of dots is worth
    return len(dotList) * (len(dotList) - 1)

def playAgainScreen(score):
    # Show screen asking the player if they want to play again
    endGameTextSurfaceObj = FONT.render("All groups cleared!", True, WINTEXTCOLOR)
    endGameTextRectObj = endGameTextSurfaceObj.get_rect()
    endGameTextRectObj.centerx, endGameTextRectObj.centery = int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) - 70

    infoText = "Final score: " + str(score)
    infoTextSurfaceObj = FONT.render(infoText, True, WINTEXTCOLOR)
    infoTextRectObj = infoTextSurfaceObj.get_rect()
    infoTextRectObj.midtop = (endGameTextRectObj.centerx, endGameTextRectObj.bottom)
    
    playAgainTextSurfaceObj = FONT.render("Play again?", True, WINTEXTCOLOR)
    playAgainTextRectObj = playAgainTextSurfaceObj.get_rect()
    playAgainTextRectObj.midtop = (infoTextRectObj.centerx, infoTextRectObj.bottom)

    yesTextSurfaceObj = FONT.render("Yes", True, WINTEXTCOLOR, TEXTRECTCOLOR)
    yesTextRectObj = yesTextSurfaceObj.get_rect()
    yesTextRectObj.midtop = (int(endGameTextRectObj.centerx / 2), playAgainTextRectObj.bottom + 20)

    noTextSurfaceObj = FONT.render("No", True, WINTEXTCOLOR, TEXTRECTCOLOR)
    noTextRectObj = noTextSurfaceObj.get_rect()
    noTextRectObj.midtop = (int(WINDOWWIDTH * .75), playAgainTextRectObj.bottom + 20)
    
    while True:
        mouseClicked = False
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True
                
        if mouseClicked and yesTextRectObj.collidepoint(mousex, mousey):
            return True
        elif mouseClicked and noTextRectObj.collidepoint(mousex, mousey):
            return False
        
        DISPLAYSURF.blit(endGameTextSurfaceObj, endGameTextRectObj)
        DISPLAYSURF.blit(infoTextSurfaceObj, infoTextRectObj)
        DISPLAYSURF.blit(playAgainTextSurfaceObj, playAgainTextRectObj)
        DISPLAYSURF.blit(yesTextSurfaceObj, yesTextRectObj)
        DISPLAYSURF.blit(noTextSurfaceObj, noTextRectObj)
        
        pygame.display.update()
        FPSCLOCK.tick(FPS)
    
def coordsOnBoard(coords):
    # Check if coordinates are on the board
    return coords[0] >= 0 and coords[0] < BOARDWIDTH and coords[1] >= 0 and coords[1] < BOARDHEIGHT

def getLeftTopCoordsOfBox(x, y):
    # Convert board coordinates to pixel coordinates on the screen
    return XMARGIN + x * SPACESIZE, YMARGIN + y * SPACESIZE
    
if __name__ == "__main__":
    playAgain = True
    while playAgain:
        playAgain = main()
    pygame.quit()
    sys.exit()
