# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 20:10:55 2021

@author: Nick Brusco
"""
import chess, time, pexpect

class Ches:
    def __init__(self):

        self.board = chess.Board()
        self.leela= pexpect.spawn('wine lc0/lc0.exe')
        self.leela.expect('(s).')
        time.sleep(.3)
        #self.leela.send('go nodes 100\r\n')

    def getmove(self):
        self.leela.expect("bestmove")
        move = str(self.leela.readline()).split()[1][:4]
        self.board.push_san(move)
        return(move)

    def sendmove(self, move):
        try:
            self.board.push_san((move))
        except:
            print("INVALID MOVE: " + move)
            return(False)
        fen = self.board.fen()
        self.leela.send("position fen " + fen)
        time.sleep(.1)
        self.leela.send("\r\ngo nodes 100\r\n")

        return True

    def brd(self):
        print(self.board)

    def startwhite(self):
        fen = self.board.fen()
        self.leela.send("position fen " + fen)
        time.sleep(.1)
        self.leela.send("\r\ngo nodes 100\r\n")
