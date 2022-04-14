import json
import time
from . import chess
from . import spinner
import heapq

class Controller(chess.Controller):
	def onmouseup(self, ev):
		if self.dragging_chess is None: return
		x, y = ev.x.data(), ev.y.data()
		i2, j2 = self.chess_board.plate.pixel_to_nearest_pos(x, y)
		px, py = self.chess_board.plate.pos_to_pixel(i2, j2)
		near = chess._distance(x, y, px, py) < self.chess_board.setting.chess_size
		succ = False
		if near:
			succ, captured = self._move_chess_to(self.dragging_chess, i2, j2)
		self._move_chess_img(self.dragging_chess, x, y)
		if succ:
			if (captured is not None) and (captured.type=='King'):
				javascript.alert("红方胜出!")
				self.restart()
				return
			self.player = 'Black'
		self.dragging_chess = None
		if self.player=='Black':
			self.blacks_turn()

	def blacks_turn(self):
		spinner.show()
		self.chess_board.rotate_board()
		# move = auto_move(self.chess_board)
		try:
			from . import ajax
			board_key = _board_key(self.chess_board) # board_key 可变为 JSON
			move = ajax.rpc.rpc_auto_move(board_key)
		except RuntimeError as ex:
			javascript.alert(str(ex))
			return
		self.chess_board.rotate_board()
		spinner.hide()
		if move is None:
			javascript.alert("红方胜出!")
			self.restart()
			return
		i1,j1,i2,j2 = move
		i1,j1,i2,j2 = 8-i1,9-j1,8-i2,9-j2
		chess = self.chess_board.board_map[(i1,j1)]
		succ, captured = self._move_chess_to(chess, i2, j2)
		assert succ
		px, py = self.chess_board.plate.pos_to_pixel(i1, j1)
		self._move_chess_img(chess, px, py)
		if (captured is not None) and (captured.type=='King'):
			javascript.alert("黑方胜出!")
			self.restart()
			return
		self.player = 'Red'


def _chess_moves(chess):
	moves = []
	if chess.type=='Rock':
		for x in range(chess.x+1,9):
			if chess.can_move_to(x, chess.y):
				moves.append((x, chess.y))
			else:
				break
		for x in range(chess.x-1,-1,-1):
			if chess.can_move_to(x, chess.y):
				moves.append((x, chess.y))
			else:
				break
		for y in range(chess.y+1, 10):
			if chess.can_move_to(chess.x, y):
				moves.append((chess.x, y))
			else:
				break
		for y in range(chess.y-1, -1, -1):
			if chess.can_move_to(chess.x, y):
				moves.append((chess.x, y))
			else:
				break
	elif chess.type=='Cannon':
		for x in range(0, 9):
			if chess.can_move_to(x, chess.y):
				moves.append((x, chess.y))
		for y in range(0, 10):
			if chess.can_move_to(chess.x, y):
				moves.append((chess.x, y))
	elif chess.type in ('Knight','Guard','Bishop','Pawn','King'):
		for dx,dy in chess.allowed_moves:
			if chess.can_move_to(chess.x+dx, chess.y+dy):
				moves.append((chess.x+dx, chess.y+dy))
		if chess.type=='King':
			for y in (7,8,9):
				if chess.can_move_to(chess.x, y):
					moves.append((chess.x, y))
	else:
		raise
	return moves

def _get_next_moves(board):
	chesses = [chess for _, chess in board.board_map.items()]
	move_to_board = {}
	for chess in chesses:
		if chess.player=='Black': continue
		for x, y in _chess_moves(chess):
			board_key = []
			for c in chesses:
				if c is chess:
					board_key.append((c.player, c.type, x, y))
				elif (c.x==x) and (c.y==y):
					pass
				else:
					board_key.append((c.player, c.type, c.x, c.y))
			board_key.sort()
			move_key = (chess.player, chess.type, chess.x, chess.y, x, y)
			move_to_board[move_key] = tuple(board_key)
	return move_to_board

def _reverse_boardkey(board_key):
	reversed = [('Red' if p=='Black' else 'Black', t, 8-x, 9-y) for p,t,x,y in board_key]
	reversed.sort()
	return tuple(reversed)

def _board_from_key(board_key):
	board = chess.ChessBoard()
	board.board_map = {}
	types = {'Rock':chess.Rock, 'Knight':chess.Knight, 'Bishop':chess.Bishop, 
				'Guard':chess.Guard, 'King':chess.King, 'Cannon':chess.Cannon, 'Pawn':chess.Pawn}
	for player, type, x, y in board_key:
		board.board_map[(x,y)] = types[type](board, player, x, y)
	return board

def _board_key(board):
	board_key = [(c.player, c.type, c.x, c.y) for _, c in board.board_map.items()]
	board_key.sort()
	return tuple(board_key)


class BoardNode:
	win_score = 10000
	def __init__(self, board, board_key=None, move_key=None, depth=0):
		self.board = board
		self.board_key = _board_key(board) if board_key is None else board_key
		self.move_key = move_key
		self.depth = depth
		self.children = []
		self.parents = []
		self.score = self._estimate_score()
		self.best_child = None

	def _estimate_score(self):
		has_r_king = False
		score_r = 0
		score_b = 0
		score_r_cross = 0
		score_b_cross = 0
		chess_scores = {'Rock':30, 'Knight':10, 'Bishop':3, 
				'Guard':3, 'King':1, 'Cannon':10, 'Pawn':1}
		cross_river_factor = 1.1
		attack_factor = 0.2
		for (x,y),c in self.board.board_map.items():
			if c.player=='Red':
				if y<5:
					score_r = score_r + chess_scores[c.type]
					if c.type=='King': has_r_king=True
				else:
					score_r_cross = score_r_cross + chess_scores[c.type]
			else:
				if y>4:
					score_b = score_b+ chess_scores[c.type]
				else:
					score_b_cross = score_b_cross + chess_scores[c.type]
		if not has_r_king:
			return -BoardNode.win_score
		r_attack = max(0, score_r_cross-score_b) * attack_factor
		b_attack = max(0, score_b_cross-score_r) * attack_factor
		score_r = (score_r + (score_r_cross*cross_river_factor)) + r_attack
		score_b = (score_b + (score_b_cross*cross_river_factor)) + b_attack
		return score_r - score_b

	def same_as_ancester(self, boardkey):
		for p in self.parents:
			if p.board_key==boardkey: return True
			if p.same_as_ancester(boardkey): return True
		return False

	def expand(self):
		assert self.best_child is None
		move_to_board = _get_next_moves(self.board)
		for movekey, boardkey in move_to_board.items():
			boardkey = _reverse_boardkey(boardkey)
			if self.same_as_ancester(boardkey): continue
			if boardkey in board_explorer.board_cache:
				board_node = board_explorer.board_cache[boardkey]
			else:
				board = _board_from_key(boardkey)
				board_node = BoardNode(board, boardkey, movekey, self.depth+1)
				board_explorer.board_cache[boardkey] = board_node
				heapq.heappush(board_explorer.heap, board_node)
			board_node.parents.append(self)
			self.children.append(board_node)
			board_node.update_parents()

	def __lt__(self, other):
		# 使headq优先扩展最有可能的路径
		if (self.depth<=1) and (other.depth<=1):
			return self.score < other.score
		if self.depth<=1: return True
		if other.depth<=1: return False
		return (self.score,self.depth) < (other.score,other.depth)

	def update_score(self):
		self.best_child = None
		for c in self.children:
			if (self.best_child is None) or (self.score < (-c.score)):
				self.score = -c.score
				self.best_child = c
		self.update_parents()

	def update_parents(self):
		p_score = -self.score
		for p in self.parents:
			if (p.best_child is None) or (p.score < p_score):
				p.score = p_score
				p.best_child = self
				p.update_parents()
			elif (p.best_child is self) and (p.score > p_score):
				p.update_score()

class BoardExplorer:
	def __init__(self, time_limit):
		self.board_cache = None
		self.heap = None
		self.time_limit = time_limit
	def run(self, board):
		board_node = BoardNode(board)
		self.board_cache = {}
		self.heap = [board_node]
		start_time = time.time()
		explored = 0
		while True:
			if (time.time()-start_time) > self.time_limit: break
			if len(board_explorer.heap)==0: break
			node = heapq.heappop(board_explorer.heap)
			score0 = node.score
			if score0 in (-BoardNode.win_score, BoardNode.win_score):
				continue # winned or lossed
			node.expand()
			# print(f'\n--- exploring#{explored} depth:{node.depth} score:{score0}>{node.score} ---')
			# print(node.board.board_map_text())
			explored = explored + 1
			elapsed = time.time()-start_time
		print(f'{explored} nodes were explored in {round(elapsed*100)/100} seconds')
		self.board_cache = None
		self.heap = None
		# _dump_tree(board_node)
		return board_node

def _dump_tree(node):
	import math
	with open('tree.txt', 'w') as fp:
		def dump_node(n,B=''):
			move = '' if n.move_key is None else '_'.join([str(e) for e in n.move_key])
			fp.write(f' ({B}{move}{round(n.score*100)/100}'.replace('-','_'))
			if len(n.children)==0:
				fp.write(' _')
			else:
				for c in n.children:
					dump_node(c,'B' if c==n.best_child else '')
			fp.write(')')
		dump_node(node)


board_explorer = BoardExplorer(3)

def auto_move(board):
	board_node = board_explorer.run(board)
	if board_node.best_child is None:
		return None
	# print('board_node.score', board_node.score)
	# print('board_node.best_child.move_key', board_node.best_child.move_key)
	# print('board_node.best_child.score', board_node.best_child.score)
	return board_node.best_child.move_key[2:]

def run_app():
	chess_board = chess.ChessBoard()
	javascript.document.body.appendChild(chess_board.elt())
	Controller(chess_board)

