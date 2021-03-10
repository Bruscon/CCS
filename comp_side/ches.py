# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 20:10:55 2021

@author: Nick Brusco
"""
import chess, os, subprocess, time, sys

#os.chdir('C:\\Users\\Nick Brusco\\Documents\\projs\\ccs\\lc0')
proc = subprocess.Popen("C:\\Users\\Nick Brusco\\Documents\\projs\\ccs\\lc0\\lc0.exe", universal_newlines = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE)
time.sleep(1.5)

for i in range(5):
    print(proc.stderr.readline())
    
print(proc.stdin.write(r"go nodes 100"))
proc.stdin.flush()
proc.stdout.flush()
proc.stderr.flush()
sys.stdout.flush()
sys.stdin.flush()
sys.stderr.flush()

print(proc.stdout.readline())
breakpoint()

board = chess.Board()


board.push(chess.Move.from_uci("c2c4"))
print(board) 