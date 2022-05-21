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
		self.chess_board.rotate_board()  # 翻转之后相当于在操作红方棋子
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
		i1,j1,i2,j2 = move  # i1,j1为棋子的位置，i2,j2为要移动的位置，均为数组坐标
		i1,j1,i2,j2 = 8-i1,9-j1,8-i2,9-j2	# 得到黑方棋子和移动位置的正确坐标
		chess = self.chess_board.board_map[(i1,j1)]
		succ, captured = self._move_chess_to(chess, i2, j2)	# 移动到i2,j2，如果成功则chess里的存储的数组坐标会变为i2,j2
		assert succ
		px, py = self.chess_board.plate.pos_to_pixel(i1, j1)
		self._move_chess_img(chess, px, py)		# HTML上让图片从i1,j1移动到chess里存储的位置，即i2,j2
		if (captured is not None) and (captured.type=='King'):
			javascript.alert("黑方胜出!")
			self.restart()
			return
		self.player = 'Red'


# 得到棋子的所有移动方式，这里默认移动的是红色棋子
def _chess_moves(chess):
	moves = []
	if chess.type=='Rock':
		for x in range(chess.x+1,9):  # 搜索车向右移动的所有走法
			if chess.can_move_to(x, chess.y):
				moves.append((x, chess.y))
			else:
				break
		for x in range(chess.x-1,-1,-1): # 搜索车向左移动的所有走法
			if chess.can_move_to(x, chess.y):
				moves.append((x, chess.y))
			else:
				break
		for y in range(chess.y+1, 10):  # 搜索车向上移动的所有走法
			if chess.can_move_to(chess.x, y):
				moves.append((chess.x, y))
			else:
				break
		for y in range(chess.y-1, -1, -1):  # 搜索车向下移动的所有走法
			if chess.can_move_to(chess.x, y):
				moves.append((chess.x, y))
			else:
				break
	elif chess.type=='Cannon':
		for x in range(0, 9):  	# 炮有些特殊，它是遍历自己所在的行和列上的所有位置
			if chess.can_move_to(x, chess.y):
				moves.append((x, chess.y))
		for y in range(0, 10):
			if chess.can_move_to(chess.x, y):
				moves.append((chess.x, y))
	elif chess.type in ('Knight','Guard','Bishop','Pawn','King'): # 其他棋子都有移动限制，根据移动限制进行移动
		for dx,dy in chess.allowed_moves:
			if chess.can_move_to(chess.x+dx, chess.y+dy):
				moves.append((chess.x+dx, chess.y+dy))
		if chess.type=='King':  # 将的移动有一点特殊，它会检查能否直接攻击对方的将
			for y in (7,8,9): 
				if chess.can_move_to(chess.x, y):
					moves.append((chess.x, y))
	else:
		raise
	return moves

# 红方棋子移动后棋盘的状态
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
				elif (c.x==x) and (c.y==y):  # 如果有被吃掉的棋子，则不记录下来
					pass
				else:
					board_key.append((c.player, c.type, c.x, c.y))
			board_key.sort()
			move_key = (chess.player, chess.type, chess.x, chess.y, x, y)
			move_to_board[move_key] = tuple(board_key)
	# 字典里的key是将要移动的棋子，棋子的拥有者，棋子的起始数组坐标，移动到的数组坐标
	# 字典里key对应的item是移动这颗棋子后棋盘的状态
	return move_to_board

# 和rotate_board作用一致，翻转棋子，这主要是为了给board_key类型的棋盘使用的
def _reverse_boardkey(board_key):
	reversed = [('Red' if p=='Black' else 'Black', t, 8-x, 9-y) for p,t,x,y in board_key]
	reversed.sort()
	return tuple(reversed)

# 将board_key类型的棋盘转换为ChessBoard类型的棋盘
def _board_from_key(board_key):
	board = chess.ChessBoard()
	board.board_map = {}
	types = {'Rock':chess.Rock, 'Knight':chess.Knight, 'Bishop':chess.Bishop, 
				'Guard':chess.Guard, 'King':chess.King, 'Cannon':chess.Cannon, 'Pawn':chess.Pawn}
	for player, type, x, y in board_key:
		board.board_map[(x,y)] = types[type](board, player, x, y)
	return board

# 将ChessBoard类型的棋盘转换为board_key类型的棋盘
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
		has_b_king = False
		score_r = 0
		score_b = 0
		score_r_cross = 0
		score_b_cross = 0
		chess_scores = {'Rock':30, 'Knight':10, 'Bishop':4, 
				'Guard':3, 'King':100, 'Cannon':11, 'Pawn':1}
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
					if c.type =='King': has_b_king = True
				else:
					score_b_cross = score_b_cross + chess_scores[c.type]
		if not has_r_king:
			return -BoardNode.win_score

		complement_b = 0
		complement_r = 0
		if has_b_king: complement_b = chess_scores['King']
		if has_r_king: complement_r = chess_scores['King']
		r_attack = max(0, (score_r_cross-(score_b-complement_b))) * attack_factor
		b_attack = max(0, (score_b_cross-(score_r-complement_r))) * attack_factor

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
		# 先下一步棋
		move_to_board = _get_next_moves(self.board)
		# 遍历所有可能的棋盘结果
		for movekey, boardkey in move_to_board.items():
			# 翻转所有的棋子
			# 如果正在下棋的是黑方，那翻转后棋盘中棋子的颜色为实际情况
			# 如果正在下棋的是红方，那翻转后棋盘中棋子的颜色倒转，此时红色棋子实际为黑色棋子
			boardkey = _reverse_boardkey(boardkey) 
			# 如果翻转后的结果和祖先节点的某一次结果一样，说明这个结果已经被搜索过了，则跳过这个结果
			if self.same_as_ancester(boardkey): continue
			# 如果棋盘结果在缓存区中，提取存储的BoardNode类

			if(player_g == 'Red'):
				if boardkey in board_explorer_r.board_cache:
					board_node = board_explorer_r.board_cache[boardkey]
				else: # 如果这个结果不在缓存区中，那就将其塞入优先队列和缓存区中
					board = _board_from_key(boardkey)
					board_node = BoardNode(board, boardkey, movekey, self.depth+1)
					board_explorer_r.board_cache[boardkey] = board_node
					heapq.heappush(board_explorer_r.heap, board_node)
			elif(player_g == 'Black'):
				if boardkey in board_explorer_b.board_cache:
					board_node = board_explorer_b.board_cache[boardkey]
				else: # 如果这个结果不在缓存区中，那就将其塞入优先队列和缓存区中
					board = _board_from_key(boardkey)
					board_node = BoardNode(board, boardkey, movekey, self.depth+1)
					board_explorer_b.board_cache[boardkey] = board_node
					heapq.heappush(board_explorer_b.heap, board_node)
			board_node.parents.append(self)
			self.children.append(board_node)
			board_node.update_parents()

	# describes less than operator (<)
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
		self.board_cache = None  # 减少内存使用
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

			if(player_g == 'Red'):
				if len(board_explorer_r.heap)==0: break
				# 每次选择队头(分数值最小)的棋盘结果
				node = heapq.heappop(board_explorer_r.heap)
			elif(player_g == 'Black'):
				if len(board_explorer_b.heap)==0: break
				# 每次选择队头(分数值最小)的棋盘结果
				node = heapq.heappop(board_explorer_b.heap)

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

# 运算时间3s
board_explorer_r = BoardExplorer(6)
board_explorer_b = BoardExplorer(6)

player_g = 'Red'
# 输入chess_board，简称为board类型的棋盘，输出移动的棋子和移动的步数
def auto_move(board):
	global player_g
	if(player_g == 'Red'):
		board_node = board_explorer_r.run(board)
		player_g = 'Black'
	elif(player_g == 'Black'):
		board_node = board_explorer_b.run(board)
		player_g = 'Red'

	if board_node.best_child is None:
		return None
	# print('board_node.score', board_node.score)
	# print('board_node.best_child.move_key', board_node.best_child.move_key)
	# print('board_node.best_child.score', board_node.best_child.score)
	return board_node.best_child.move_key[2:]

class ControlBothAuto(chess.Controller):
	def __init__(self, chess_board):
		super(ControlBothAuto, self).__init__(chess_board)
		self.run = False

	def onmousedown(self, ev):
		return
	
	def onmousemove(self, ev):
		return

	def onmouseup(self, ev):
		self.run = not self.run
		while(self.run):
			result = self.turn('Red')
			if result is not None:
				self.run = False
				break
			time.sleep(0.5)

			result = self.turn('Black')
			if result is not None:
				self.run = False
				break
			time.sleep(0.5)
			

	def turn(self, player):
		spinner.show()
		if(player == 'Black'): self.chess_board.rotate_board()
		# move = auto_move(self.chess_board)
		try:
			from . import ajax
			board_key = _board_key(self.chess_board) # board_key 可变为 JSON
			move = ajax.rpc.rpc_auto_move(board_key)
		except RuntimeError as ex:
			javascript.alert(str(ex))
			return
		if(player == 'Black'): self.chess_board.rotate_board()
		spinner.hide()
		if move is None:
			javascript.alert("黑方胜出！" if player == 'Black' else "红方胜出!")
			self.restart()
			return 'Finished'
		i1,j1,i2,j2 = move  # i1,j1为棋子的位置，i2,j2为要移动的位置，均为数组坐标

		if(player == 'Black'): i1,j1,i2,j2 = 8-i1,9-j1,8-i2,9-j2

		chess = self.chess_board.board_map[(i1,j1)]
		succ, captured = self._move_chess_to(chess, i2, j2)	# 移动到i2,j2，如果成功则chess里的存储的数组坐标会变为i2,j2
		assert succ
		px, py = self.chess_board.plate.pos_to_pixel(i1, j1)
		self._move_chess_img(chess, px, py)		# HTML上让图片从i1,j1移动到chess里存储的位置，即i2,j2
		if (captured is not None) and (captured.type=='King'):
			javascript.alert("黑方胜出！" if player == 'Black' else "红方胜出!")
			self.restart()
			return 'Finished'

		if(player == 'Black'):
			self.player = 'Red'
		elif(player == 'Red'):
			self.player = 'Black'
		return None


def run_app():
	chess_board = chess.ChessBoard()
	javascript.document.body.appendChild(chess_board.elt())
	ControlBothAuto(chess_board)
	# Controller(chess_board)


