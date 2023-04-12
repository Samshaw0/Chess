# This is the main driver file. It will be responsible for handling user input and displaying the current
# GameState object.

import pygame as p
import Chess_Engine
import Chess_AI

boardWidth = boardHeight = 512
moveLogPanelHeight = boardHeight
moveLogPanelWidth = 250
DIMENSION = 8 #Chess board is 8x8
SQ_SIZE = boardHeight // DIMENSION
MAX_FPS = 15 #For animations later
IMAGES = {}

# Load in images and inisialise a global dictionary of images. We don't want to do this multiple times.
# as in pygame it is an expensive operation.

def loadImages():
    pieces = ["wP", "wR", "wB", "wQ", "wK", "wN", "bP", "bR", "bB", "bQ", "bK", "bN"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    
    # Now we can access an image through the dictionary

# This is our main driver for our code. It will handle user imput and updating the graphics

def main():
    p.init()
    screen = p.display.set_mode((boardWidth+moveLogPanelWidth, boardHeight))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = Chess_Engine.GameState()
    validMoves = gs.getValidMoves() # Expensive Operation
    animate = False # Flag variable for when we animate
    boardChange = False #flag variable for when a move is made
    loadImages()
    running = True
    playerOne = True # If a human is playing white this will be True, else False
    playerTwo = False # If a human is plating black this will be True, else False
    sqSelected = () # Keeps track of the last square selected (tuple: (row, col))
    playerClicks = [] # Keeps track of player clicks (two tuples: [(row, col), (newRow, newCol)])
    colours = [p.Color("white"), p.Color("pink")]
    moveLogFont = p.font.SysFont("Arial", 16, False, False)
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        gameOver = gs.checkmate or gs.stalemate or gs.repetition
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Key handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos() # (x,y) position of mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col) or col > 7: # The user selected same square twice (undo action)
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected) # We append for both first and second clicks
                    if len(playerClicks) == 2:
                        move = Chess_Engine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                boardChange = True
                                animate = True
                                gs.makeMove(validMoves[i])
                                sqSelected = ()
                                playerClicks = []
                        if not boardChange:
                            playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_LEFT:
                    animate = False
                    gs.undoMove()
                    boardChange = True
                if e.key == p.K_r:
                    gs = Chess_Engine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    boardChange = False
                    animate = False


                if e.key == p.K_RETURN: # temporary stop line remove later
                    running = False
        # AI move finder
        if not gameOver and not humanTurn:
            AIMove = Chess_AI.findBestMoveInit(gs, validMoves)
            if AIMove is None: AIMove = Chess_AI.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            boardChange = True
            animate = True

        if boardChange:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock, colours)
            validMoves = gs.getValidMoves()
            boardChange = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected, colours, moveLogFont)

        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                drawEndGameText(screen, "Black wins by checkmate")
            else:
                drawEndGameText(screen, "White wins by checkmate")
        elif gs.stalemate:
            gameOver = True
            drawEndGameText(screen, "Draw by Stalemate")
        elif gs.repetition:
            gameOver = True
            drawEndGameText(screen, "Draw by repetition")

        clock.tick(MAX_FPS)
        p.display.flip()

# Highlight square selected and possible moves
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        row, col = sqSelected
        if gs.board[row][col][0] == ("w" if gs.whiteToMove else "b"): #Square Selected is of right colour
            # Highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) # Opacity value (0 transparent, 255 opaque)
            s.fill(p.Color("yellow")) # Colour of the highlight
            screen.blit(s, (col*SQ_SIZE, row*SQ_SIZE))
            # Highlight moves for selected piece
            s.fill(p.Color("grey"))
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))
            




# This function is responsible for all graphics in current game state
def drawGameState(screen, gs, validMoves, sqSelected, colours, moveLogFont):
    drawBoard(screen, colours) # Draws squares on board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) # Draws pieces ontop of board
    drawMoveLog(screen, gs, moveLogFont)

# This function draws the move log
def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(boardWidth, 0, moveLogPanelWidth, moveLogPanelHeight)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    while len(moveLog)>50: moveLog.pop(0)
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveTexts.append(str(i//2 + 1) + ". " + moveLog[i].moveNotation(gs.checkLog[i]))
        if i+1 < len(moveLog):
            moveTexts[-1] += " " + moveLog[i+1].moveNotation(gs.checkLog[i+1])
    border_padding = 5
    moveLog_padding = 120
    textY = border_padding
    lineSpacing = 2
    movesPerRow = 2
    if gs.checkmate: moveTexts[-1] = moveTexts[-1][:-1] + "#"
    for i in range(0, len(moveTexts)):
        text = moveTexts[i]
        textObject = font.render(text, True, p.Color("White"))
        textLocation = moveLogRect.move(border_padding + moveLog_padding*(i%movesPerRow), textY)
        screen.blit(textObject, textLocation)
        textY += (textObject.get_height() + lineSpacing) if (i+1)%movesPerRow==0 else 0

# Draws squares on board
def drawBoard(screen, colours):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            colour = colours[(row+col)%2]
            p.draw.rect(screen, colour, p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

# Draws pieces
def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def animateMove(move, screen, board, clock, colours):
    coords = [] # list of coords the animation will move through
    dRow = move.endRow - move.startRow
    dCol = move.endCol - move.startCol
    framesPerSquare = 5 # Frames to move one square
    frameCount = abs(dRow) + abs(dCol)*framesPerSquare
    for frame in range(frameCount+1):
        row, col = (move.startRow + dRow*frame/frameCount, move.startCol + dCol*frame/frameCount)
        drawBoard(screen, colours)
        drawPieces(screen, board)
        # Erase piece moved from its ending square
        colour = colours[(move.endRow + move.endCol)%2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, colour, endSquare)
        # Draw captured piece back onto ending square
        if move.pieceCaptured != "--":
            if move.isEnPassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0]=="b" else move.endRow-1
                endSquare = p.Rect(move.endCol*SQ_SIZE, enPassantRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)

            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # Draw moving pieces
        screen.blit(IMAGES[move.pieceMoved], p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvitca", 28, False, True)
    textObject = font.render(text, 0, p.Color("Black"))
    textLocation = p.Rect(0, 0, boardHeight, boardHeight).move(boardWidth/2 - textObject.get_width()/2, boardHeight/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)

import cProfile
cProfile.run("main()", "output.dat")

import pstats
from pstats import SortKey
with open("output_time.txt", "w") as f:
    p = pstats.Stats("output.dat", stream=f)
    p.sort_stats("time").print_stats()
with open("output_calls.txt", "w") as f:
    p = pstats.Stats("output.dat", stream=f)
    p.sort_stats("calls").print_stats()

