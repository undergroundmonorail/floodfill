#!/bin/python2

from __future__ import division

import sys
import operator
import textwrap

try:
	# multiplatform ANSI colours
	from colorama import init
	init()
except InputError:
	# if they don't have colorama, that's fine
	pass

# http://code.activestate.com/recipes/134892/
from getch import *

def boardformat(board):
	"""Return the board converted to a list of rows, with non-digits and empty
	lines stripped
	"""
	return [filter(str.isdigit,list(row)) for row in board.split('\n') if row]

def boardstring(board):
	"""Return a string representing the board in a human-friendly way"""
	
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
	
	b = ''
	for i, r in enumerate(board):
		for j, e in enumerate(r):
			b += colour_dict[e] + ('*' if i==j==len(board)//2 else ' ') + e
				
		b += '\033[0m\n'
	
	return b[:-1]

def adjacent_equal(board, value=None, y=None, x=None, matched=None):
	"""Returns the X, Y coordinates of each cell that neighbours the center cell
	and shares its value, as well as the matching neighbours of those cells, and
	so on
	"""
	# New contains each matching cell that this layer of depth found. Stored
	# seperately so we don't get dupes
	new = []
	
	# Setup for first iteration
	if x is None:
		x = len(board) // 2
		y = len(board) // 2
		
		# list[-1] is the last element of the list. This means that lists will wrap
		# going backwards, which is behaviour we don't want. A row of illegal
		# characters is added to the end and a single illegal character is added to
		# each row, so that board[-1][z] or board[z][-1] never matches
		board = [row + ['X'] for row in board]
		board.append(list('X'*len(board)))
	
		value = board[y][x]
		matched = [(y, x)]
		new = [(y, x)]
		
	# Coords of all neighbours
	neighbours = [(y + n, x + m) for n, m in [(-1, 0), (0, 1), (1, 0), (0, -1)]]
	for n, m in neighbours:
		# Recurse for each matching neighbour, unless it's been done
		if board[n][m] == value and (n, m) not in matched:
			matched.append((n, m))
			new += adjacent_equal(board, value, n, m, matched) + [(n, m)]
	
	return new

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

def main(args):
	if len(args) < 2:
		sys.exit('Usage: ./flood boardfile.txt')
	
	with open(args[1]) as f:
		board = boardformat(f.read())
	
	# Ensure that the input is a square with odd dimensions
	if len(set(map(len, board) + [len(board)])) != 1:
		sys.exit('Error: The board must be square.')
	if not len(board) % 2:
		sys.exit('Error: The board must have odd dimensions.')
	
	sys.stdout.write('\033[2J')
	moves = 0
	
	# Game loop
	while True:
		sys.stdout.write('\033[H')
		print boardstring(board)
		current_group = adjacent_equal(board)
		print textwrap.dedent("""\
		                      Moves: {}           
		                      Matched: {}%           """.format(
		                      moves, len(current_group)/(len(board)**2)*100))
		# Break when every cell is the same
		if len(set(sum(board, []))) == 1:
			sys.exit('Congratulations!')
		moves += user_input(board, current_group)
	
if __name__ == '__main__':
	main(sys.argv)
