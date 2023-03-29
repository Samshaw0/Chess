import random as r

pieceScore = {"K":0, "P":1, "Q":9, "R":5, "B":3, "N":3}
checkmate = 1000
stalemate = 0
DEPTH = 2

def findRandomMove(validMoves):
    return r.choice(validMoves)

def findBestMove(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = checkmate
    bestPlayerMove = None
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentMoves = gs.getValidMoves()
        opponentMaxScore = -checkmate
        if gs.checkmate: opponentMaxScore = -checkmate
        elif gs.stalemate: opponentMaxScore = stalemate
        else:
            for opponentMove in opponentMoves:
                gs.makeMove(opponentMove)
                gs.getValidMoves()
                if gs.checkmate: score = checkmate
                elif gs.stalemate: score = stalemate
                else:
                    score = -turnMultiplier * scoreMaterial(gs.board)
                if score > opponentMaxScore:
                    opponentMaxScore = score
                gs.undoMove()
        if opponentMinMaxScore > opponentMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = [playerMove]
        elif opponentMinMaxScore == opponentMaxScore: bestPlayerMove.append(playerMove)
        gs.undoMove()
    return findRandomMove(bestPlayerMove)

def findBestMoveMinMax(gs, validMoves):
    # Helper method to find first recursive call
    global nextMove
    nextMove = None
    findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    return r.choice(nextMove)

def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)
    if whiteToMove:
        maxScore = -checkmate
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-1, not whiteToMove)
            if score > maxScore: 
                maxScore = score
                if depth == DEPTH: nextMove = [move]
            elif score==maxScore and depth==DEPTH: nextMove.append(move)
            gs.undoMove()
        return maxScore
    else:
        minScore = checkmate
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-1, whiteToMove)
            if score < minScore:
                minScore = score
                if depth==DEPTH: nextMove = [move]
            elif score == minScore and depth==DEPTH:
                nextMove.append(move)
            gs.undoMove()
        return minScore


def scoreBoard(gs):
    if gs.checkmate:
        if gs.whtieToMove: return -checkmate # Black wins
        else: checkmate # White wins
    elif gs.stalemate: return stalemate

    score = 0
    for row in gs.board:
        for square in row:
            if square[0]=="w":
                score = score + pieceScore[square[1]]
            elif square[0]=="b": score = score - pieceScore[square[1]]
    return score


def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0]=="w":
                score = score + pieceScore[square[1]]
            elif square[0]=="b": score = score - pieceScore[square[1]]
    return score