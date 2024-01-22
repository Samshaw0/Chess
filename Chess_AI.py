import random as r
from functools import lru_cache
pieceScore = {"K":0, "P":1, "Q":9, "R":5, "B":3, "N":3}
checkmate = 1000

def findRandomMove(validMoves):
    return r.choice(validMoves)

def findBestMove():
    root = node(None, [], None, None)
    root.developTree(validMoves, gs) #builds the intial tree
    for i in range(100):
        makeMoveCount = 0
        move = root.findBestMove()
        while len(move.children)!=0:
            gs.makeMove(move.move)
            makeMoveCount += 1
            move = move.findBestMove()
            move.developTree(gs.getValidMoves(), gs)
            for j in range(makeMoveCount): gs.undoMove()            
    
    return root.findBestMove().move


def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove: return -checkmate # Black wins
        else: checkmate # White wins
    elif gs.stalemate: return 0
    elif gs.repetition: return 0
    squareStrength = [0.16, 0.18, 0.2, 0.22, 0.22, 0.2, 0.18, 0.16]
    score = 0
    numberOfPieces = 0
    for row in gs.board:
        for col in row:
            if col[1] in ["B", "Q", "R", "N"]: numberOfPieces+=1
    endgameMultiplier = 1 if numberOfPieces<6 else -1 # In endgames you want an active king otherwise you want a passive king
    for row in range(len(gs.board)):
        for square in range(len(gs.board[0])):
            piece = gs.board[row][square]
            colourMultiplier = 1 if piece[0]=="w" else -1
            if piece[1] not in ["K", "P", "-"]:
                score = score + (pieceScore[piece[1]] + squareStrength[row]*squareStrength[square])*colourMultiplier
            elif piece[1] == "K":
                score = score + (pieceScore[piece[1]] + squareStrength[row]*squareStrength[square]*endgameMultiplier)*colourMultiplier
            elif piece[1] == "P":
                score = score + (pieceScore[piece[1]] + squareStrength[row]*squareStrength[square] + 0.0025*pawnChain(gs.board, (row, square), gs.whiteToMove))*colourMultiplier
    return round(score,5)


def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0]=="w":
                score = score + pieceScore[square[1]]
            elif square[0]=="b": score = score - pieceScore[square[1]]
    return score

def pawnChain(board, square, whiteToMove): # Enter square as a tuple
    # takes the coords of a pawn and a returns whether it makes a pawn chain (any pawns diagonal)
    coords = [[square[0]+1, square[1]+1], [square[0]+1, square[1]-1]]
    numberOfChains = 0
    for coord in coords:
        if coord[0]<=7 and coord[0]>=0 and coord[1]<=7 and coord[1]>=0:
            if board[coord[0]][coord[1]] == ("w" if whiteToMove else "b") + "P":
                numberOfChains+=1
    return numberOfChains

class node():
    def __init__(self, parent, children, score, move):
        self.parent = parent
        self.children = children
        self.score = score
        self.move = move
        
    def developTree(self, validMoves, gs): # need to do the + and - for b/w
        maxMoveScore = -9999999
        for move in validMoves:
            gs.makeMove(move)
            score = scoreBoard(gs)
            gs.undoMove()
            self.children.append(node(self, [], score, move))
            if score>maxMoveScore: maxMoveScore = score
        self.score = maxMoveScore

    def findBestMove(self):
        maxMove = self.children[0]
        for move in self.children:
            if move.score > maxMove.score: maxMove=move
        return maxMove
            






















