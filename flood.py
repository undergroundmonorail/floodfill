#!/bin/python2

from __future__ import division

import os
import sys
import time
import random
import operator
import textwrap
import platform

# http://code.activestate.com/recipes/134892/
from getch import *

colour = True
try:
	# multiplatform ANSI colours
	from colorama import init
	init()
except ImportError:
	if platform.system() == 'Windows':
		print textwrap.dedent("""\
		                      Your system doesn't appear to support ANSI codes.
		                      ANSI codes are used heavily in this program to create
		                      colour and clear the screen at appropriate times.
		                      
		                      The first is to press any key other than 'c' to quit.
		                      This game isn't very good and probably isn't worth
		                      your time.
		                      
		                      The second is to press 'c' now to continue playing
		                      without ANSI codes. This will work, but it will be
		                      ugly and hard to play.
		                      
		                      The final option is to press any key other than 'c',
		                      quit the game and install the colorama python module.
		                      This module is designed to allow ANSI codes to be
		                      used on systems that don't natively support them.
		                      The module can be found here:
		                      
		                      https://pypi.python.org/pypi/colorama
		                      
		                      If you really want to play this game, I'd reccomend
		                      this. The colours really are worth it.
		                      
		                      (c)ontinue? """)
		colour = False
		if getch() != 'c':
			sys.exit()

def boardformat(board):
	"""Return the board converted to a list of rows, with non-digits and empty
	lines stripped
	"""
	return [filter(str.isdigit,list(row)) for row in board.split('\n') if row]

def boardstring(board):
	"""Return a string representing the board in a human-friendly way"""
	
	if colour:
		# Keys = strings reperesenting ints 1-6
		# Values = ANSI colour code for that number
		colour_dict = {
		                '1' : '\033[47;30m',
		                '2' : '\033[45;37m',
		                '3' : '\033[44;37m',
		                '4' : '\033[46;30m',
		                '5' : '\033[43;30m',
		                '6' : '\033[41;37m',
		              }
	else:
		colour_dict = dict(zip('123456', ['']*6)) # No colours for non-ansi systems
	
	b = ''
	for i, r in enumerate(board):
		for j, e in enumerate(r):
			b += colour_dict[e] + ('*' if i==j==len(board)//2 else ' ') + e
		
		if colour:
			b += '\033[0m'
		
		b += '\n'
	
	return b[:-1]

def adjacent_equal(board, value=None):
	"""Returns the X, Y coordinates of each cell that neighbours the center cell
	and shares its value, as well as the matching neighbours of those cells, and
	so on
	"""
	value = board[len(board) // 2][len(board) // 2]
	matched = [(len(board) // 2, len(board) // 2)]
	
	# list[-1] is the last element of the list. This means that lists will wrap
	# going backwards, which is behaviour we don't want. A row of illegal
	# characters is added to the end and a single illegal character is added to
	# each row, so that board[-1][z] or board[z][-1] never matches
	board = [row + ['X'] for row in board]
	board.append(list('X'*len(board)))
	
	while True:
		m = len(matched)
		for y, row in enumerate(board):
			for x, cell in enumerate(row):
				if cell == value and (y, x) not in matched:
					if filter(lambda c: c in matched, [(y+1,x),(y-1,x),(y,x+1),(y,x-1)]):
						matched.append((y, x))
		if len(matched) == m:
			break
	
	return matched

def paint_cells(board, cells, value):
	"""Set the specified cells on the board to the new value and return None."""
	# Fail silently if input isn't 1-6
	if value in map(str, range(1, 7)):
		for y, x in cells:
			board[y][x] = value

def user_input(board, current_group):
	"""Get one character of the user's input without echoing to the screen, then
	take the appropriate action. Return True if move was made
	"""
	s = getch()
	
	if s in map(str, range(1, 7)):
		paint_cells(board, current_group, s)
		return True
	elif s == 'q':
		sys.exit('Goodbye')
	
	return False

def ai_solve(board):
	"""Return a greedy solution for solving the board"""
	# Stop if solved
	if len(set(sum(board, []))) == 1:
		return ''
	
	board_copy = [b[:] for b in board]
	boards = {}
	for c in '123456':
		paint_cells(board_copy, adjacent_equal(board_copy), c)
		boards[c] = board_copy
		board_copy = [b[:] for b in board]
	
	# Choose the move that gets you the most cells this turn
	m = max('123456', key=lambda c:len(adjacent_equal(boards[c])))
	
	return m + ai_solve(boards[m])

def main(args):
	if len(args) < 2:
		while True:
			try:
				size = int(raw_input('What size of board would you like to play?\n> '))
				break
			except NameError:
				print 'Please enter a number.'
		
		# Add 1 if even
		size += not size % 2	
		
		board = []
		
		for i in range(size):
			board.append([])
			for j in range(size):
				board[-1].append(random.choice('123456'))
	
	else:
		with open(args[1]) as f:
			board = boardformat(f.read())
	
	# Ensure that the input is a square with odd dimensions
	if len(set(map(len, board) + [len(board)])) != 1:
		sys.exit('Error: The board must be square.')
	if not len(board) % 2:
		sys.exit('Error: The board must have odd dimensions.')
	
	sys.stdout.write('\033[2J')
	moves = 0
	
	unsolved = [b[:] for b in board]
	
	try:
		solution = ai_solve(board)
	except RuntimeError:
		solution = ''

	# Game loop
	while True:
		if colour:
			sys.stdout.write('\033[H')
		else:
			os.system('cls') # Non-ansi way to clear screen
		
		if solution:
			print 'The computer solved it in {} moves.'.format(len(solution))
			print 'Can you do better?'
		else:
			print 'The computer isn\'t smart enough to solve a board this large.'
			print 'You\'re welcome to try, though!'
		print boardstring(board)
		current_group = adjacent_equal(board)
		print textwrap.dedent("""\
		                      Moves: {}           
		                      Matched: {}%           """.format(
		                      moves, len(current_group)/(len(board)**2)*100))
		# Break when every cell is the same
		if len(set(sum(board, []))) == 1:
			break
		moves += user_input(board, current_group)
	
	print 'Congratulations!'
	print
	print 'You solved the puzzle in {} moves.'.format(moves)
	if not solution:
		sys.exit()
	print 'The computer solved it in {} moves.'.format(len(solution))
	print 'Your solution was {} moves {}.'.format(
	abs(moves - len(solution)), 'faster' if moves <= len(solution) else 'slower')
	print
	print 'Press any key to watch the computer\'s solution.'
	getch()
	
	if colour:
		sys.stdout.write('\033[2J\033[H')
	else:
		os.system('cls') # Non-ansi way to clear screen
	board = unsolved
	
	for m in solution:
		if colour:
			sys.stdout.write('\033[H')
		else:
			os.system('cls') # Non-ansi way to clear screen
		print boardstring(board)
		time.sleep(0.5)
		paint_cells(board, adjacent_equal(board), m)

	if colour:
		sys.stdout.write('\033[H')
	else:
		os.system('cls') # Non-ansi way to clear screen
	print boardstring(board)
	
if __name__ == '__main__':
	main(sys.argv)
