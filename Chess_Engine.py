# This class is responsible for storing all the information about the current state of a chess game.
# It will also be responsible for determining the valid moves in the current position.
# It will also keep a move log.


class GameState():
    def __init__(self):
        # The board is an 8x8 2 dimensional list. Each element of the list has 2 characters
        # The first character represents colour, the second represents piece
        # The string "--" represents a space
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.boardLog = [hash("".join([piece for col in self.board for piece in col]))] # For finding repetitions
        self.moveLog = []
        self.whiteToMove = True
        self.moveFunctions = {"P":self.getPawnMoves, "R":self.getRookMoves, "N":self.getKnightMoves,
        "B":self.getBishopMoves, "Q":self.getQueenMoves, "K":self.getKingMoves}
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0,4)
        self.checkmate = False
        self.stalemate = False
        self.repetition = False
        self.enPassantPossible = () # Coords for the square for en passant
        self.enPassantPossibleLog = [self.enPassantPossible]
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                            self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]

# Takes a move as a parameter and executes it (doesn't work for en-passant, promotions, castling)
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # Logs move for undos 
        self.whiteToMove = not self.whiteToMove # Alternates black/white to move
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = "--"
        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.startRow+move.endRow)//2, move.endCol)
        else:
            self.enPassantPossible = ()

        #castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #kingside
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #moves rook
                self.board[move.endRow][7] = "--" # deletes old rook
            else: #queenside
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][0] = "--"

        #update en passant rights
        self.enPassantPossibleLog.append(self.enPassantPossible)

        #update castle rights - whenever rook/king moves
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                                self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))
        #update board log
        self.boardLog.append(hash("".join([piece for col in self.board for piece in col])))



    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.boardLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            if move.isEnPassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
            self.enPassantPossibleLog.pop()
            self.enPassantPossible = self.enPassantPossibleLog[-1]
            # Undo castle rights
            self.castleRightsLog.pop() # Get rid of castle rigths from move we are undoing
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRights = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)
            # Undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: #kingside
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = "--"
                else:
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = "--"
            self.checkmate = False
            self.stalemate = False
            self.repetition = False
            

        
    def updateCastleRights(self, move): 
        if move.pieceMoved == "wK":
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.bks = False
        # If rook castled
        if move.pieceCaptured == "wR":
            if move.endRow == 7:
                if move.endCol == 0: self.currentCastleRights.wqs = False
                elif move.endCol == 7: self.currentCastleRights.wks = False
            elif move.endRow == 0:
                if move.endCol == 0: self.currentCastleRights.bqs = False
                elif move.endCol == 7: self.currentCastleRights.bks = False



    # All moves considering checks
    def getValidMoves(self):
        tempEnPassantPossible = self.enPassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
        self.currentCastlingRights.wqs, self.currentCastlingRights.bqs) # copies current castling rights
        # 1) Generate all possible moves
        moves = self.getAllMoves()
        # 2) For each move, make the move
        # We start from back in order to avoid messing up index when we remove items
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
        # 3) Generate all opponents moves
        # 4) For each opponents move check if it takes the king. If so its not valid
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
            self.repetition = False
        if len(moves) == 0: # Checkmate or Stalemate
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False # For undoing checkmate/stalemate when we undo moves
            self.stalemate = False
        #checks for draw by repetition
        count = 0
        for transposition in self.boardLog:
            if transposition == self.boardLog[-1]: count+=1
        if count>=3: self.repetition = True
        else: self.repetition = False

        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)


        self.enPassantPossible = tempEnPassantPossible
        self.currentCastleRights = tempCastleRights
        return moves
        

    # Determines if current player in in check
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
        
    # Determines if enemy can attack square (row, col)
    def squareUnderAttack(self, row, col):
        self.whiteToMove = not self.whiteToMove # Switch to oppondents moves
        oppMoves = self.getAllMoves()
        self.whiteToMove = not self.whiteToMove # Switch back
        for move in oppMoves:
            if move.endRow == row and move.endCol == col:
                return True
        return False

    #All moves without considering checks
    def getAllMoves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0] # Accesses the first character of the item in the square
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row, col, moves)

        return moves

    def getPawnMoves(self, row, col, moves):
        if self.whiteToMove:
            if self.board[row-1][col] == "--":
                moves.append(Move((row, col), (row-1, col), self.board))
                if row == 6:
                    if self.board[row-2][col] == "--":
                        moves.append(Move((row, col), (row-2, col), self.board))
            if col-1 >= 0:
                if self.board[row-1][col-1][0] == "b":
                    moves.append(Move((row, col), (row-1, col-1), self.board))
                elif (row-1, col-1) == self.enPassantPossible:
                    moves.append(Move((row, col), (row-1, col-1), self.board, isEnPassantMove = True))
            if col+1 <= 7:
                if self.board[row-1][col+1][0] == "b":
                    moves.append(Move((row, col), (row-1, col+1), self.board))
                elif (row-1, col+1) == self.enPassantPossible:
                    moves.append(Move((row, col), (row-1, col+1), self.board, isEnPassantMove = True))
        else:
            if self.board[row+1][col] == "--":
                moves.append(Move((row, col), (row+1, col), self.board))
                if row == 1:
                    if self.board[row+2][col] == "--":
                        moves.append(Move((row, col), (row+2, col), self.board))
            if col-1 >= 0:
                if self.board[row+1][col-1][0] == "w":
                    moves.append(Move((row, col), (row+1, col-1), self.board))
                elif (row+1, col-1) == self.enPassantPossible:
                    moves.append(Move((row, col), (row+1, col-1), self.board, isEnPassantMove = True))
            if col+1 <= 7:
                if self.board[row+1][col+1][0] == "w":
                    moves.append(Move((row, col), (row+1, col+1), self.board))
                elif (row+1, col+1) == self.enPassantPossible:
                    moves.append(Move((row, col), (row+1, col+1), self.board, isEnPassantMove = True))

    def getRookMoves(self, row, col, moves):
        coords = [[1,0],[0,-1],[-1,0],[0,1]]
        cannotCaptureColour = self.whiteOrBlack(self.whiteToMove)
        canCaptureColour  = self.whiteOrBlack(not self.whiteToMove)
        for i in range(len(coords)):
            for multiplier in range(1, len(self.board)+1):
                pos = [row+(coords[i][0]*multiplier), col+(coords[i][1]*multiplier)]
                if pos[0] < 0 or pos[0] > 7 or pos[1] < 0 or pos[1] > 7 or self.board[pos[0]][pos[1]][0] == cannotCaptureColour:
                    break
                elif self.board[pos[0]][pos[1]][0] == canCaptureColour:
                    moves.append(Move((row, col), (pos[0], pos[1]), self.board))
                    break
                else:
                    moves.append(Move((row, col), (pos[0], pos[1]), self.board))

    def getKnightMoves(self, row, col, moves):
        coords = [[1,2],[2,1],[1,-2],[-2,1],[-1,2],[2,-1],[-2,-1],[-1,-2]]
        cannotCaptureColour = self.whiteOrBlack(self.whiteToMove) 
        for i in range(len(coords)):
            if col+coords[i][1] <= 7 and col+coords[i][1] >= 0:
                if row+coords[i][0] <= 7 and row+coords[i][0] >= 0:
                    if self.board[row + coords[i][0]][col + coords[i][1]][0] != cannotCaptureColour:
                        moves.append(Move((row, col), (row+coords[i][0], col+coords[i][1]), self.board))
    def getBishopMoves(self, row, col, moves):
        coords = [[1,1],[1,-1],[-1,1],[-1,-1]]
        cannotCaptureColour = self.whiteOrBlack(self.whiteToMove)
        canCaptureColour  = self.whiteOrBlack(not self.whiteToMove)
        for i in range(len(coords)):
            for multiplier in range(1, len(self.board)+1):
                pos = [row+(coords[i][0]*multiplier), col+(coords[i][1]*multiplier)]
                if pos[0] < 0 or pos[0] > 7 or pos[1] < 0 or pos[1] > 7 or self.board[pos[0]][pos[1]][0] == cannotCaptureColour:
                    break
                elif self.board[pos[0]][pos[1]][0] == canCaptureColour:
                    moves.append(Move((row, col), (pos[0], pos[1]), self.board))
                    break
                else:
                    moves.append(Move((row, col), (pos[0], pos[1]), self.board))

    def getQueenMoves(self, row, col, moves):
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

    def getKingMoves(self, row, col, moves):
        coords = [[1,0],[1,1],[1,-1],[-1,0],[-1,-1],[-1,1],[0,-1],[0,1]]
        cannotCaptureColour = self.whiteOrBlack(self.whiteToMove)
        for i in range(len(coords)):
            if col+coords[i][1] <= 7 and col+coords[i][1] >= 0:
                if row+coords[i][0] <= 7 and row+coords[i][0] >= 0:
                    if self.board[row + coords[i][0]][col + coords[i][1]][0] != cannotCaptureColour:
                        moves.append(Move((row, col), (row+coords[i][0], col+coords[i][1]), self.board))

    def getCastleMoves(self, row, col, moves):
        if self.inCheck():
            return # can't castle when in check
        if self.whiteToMove and self.currentCastlingRights.wks or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingSideCastleMoves(row, col, moves)
        if self.whiteToMove and self.currentCastlingRights.wqs or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueenSideCastleMoves(row, col, moves)
        

    def getKingSideCastleMoves(self, row, col, moves):
        if self.board[row][col+1]=="--" and self.board[row][col+2]=="--":
            if not self.squareUnderAttack(row, col+1) and not self.squareUnderAttack(row, col+2):
                moves.append(Move((row, col), (row, col+2), self.board, isCastleMove=True))

            

    def getQueenSideCastleMoves(self, row, col, moves):
        if self.board[row][col-1]=="--" and self.board[row][col-2]=="--" and self.board[row][col-2]=="--":
            if not self.squareUnderAttack(row, col-1) and not self.squareUnderAttack(row, col-2):
                moves.append(Move((row, col), (row, col-2), self.board, isCastleMove=True))

    def whiteOrBlack(self, wOrB):
        if wOrB:
            return "w"
        else:
            return "b"
        


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():

    ranksToRows = {"1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnPassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # Pawn Promotion
        self.isPawnPromotion = (self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow == 7)
        self.isCapture = self.pieceCaptured != "--"

        # En passant
        self.isEnPassantMove = isEnPassantMove
        if isEnPassantMove:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"
        #Castling
        self.isCastleMove = isCastleMove

        self.moveId = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol
        # Overiding equals methods
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveId == other.moveId
        return False

    def getChessNotation(self):
        return self.getRankfile(self.startRow, self.startCol) + self.getRankfile(self.endRow, self.endCol)

    def getRankfile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]
    
    # Overing the str() function
    def __str__(self):
        # castle moves
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"
        
        endSquare = self.getRankfile(self.endRow, self.endCol)
        # pawn moves
        if self.pieceMoved[1] == "P":
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else: return endSquare
        #piece moves
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString+="x"
        return moveString+endSquare