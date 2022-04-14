
import math

def html(tag, attrs=None, style=None):
	elt = javascript.document.createElement(tag)
	if attrs is not None:
		for k,v in attrs.items():
			elt.setAttribute(k,v)
	if style is not None:
		style = ';'.join([f'{k}:{v}' for k,v in style.items()])
		elt.setAttribute('style',style)
	return elt

class SettingLarge:
	offset_x = 29
	offset_y = 29-3
	grid_size_x = 59
	grid_size_y = 61
	plate_size = 535
	chess_size = 55

def _distance(x1, y1, x2, y2):
	return math.sqrt(((x1-x2)**2) + ((y1-y2)**2))

class Plate:
	def __init__(self, setting):
		self.setting = setting
		style = {'opacity':0.65, 'width':setting.plate_size,
				'position':'absolute','left':'0px','top':'0px'}
		self.elt = html('img', {'src':'chess-img/plate.png', 'draggable':'false'}, style=style)
	def pos_to_pixel(self, i, j):
		x = self.setting.offset_x + (i * self.setting.grid_size_x)
		y = self.setting.offset_y + ((9 - j) * self.setting.grid_size_y)
		return x, y	
	def pixel_to_nearest_pos(self, x, y):
		index = None
		min_dis = None
		for i in range(9):
			for j in range(10):
				px, py = self.pos_to_pixel(i, j)
				dis = _distance(x, y, px, py)
				if (index is None) or (dis < min_dis):
					index, min_dis = (i,j), dis
		return index

class ChessMan:
	pos_range=(0,0,8,9)
	def __init__(self, board, player, type, x, y):
		self.board = board
		self.player = player
		self.type = type
		self.x = x
		self.y = y

	def clone(self):
		return type(self)(self.board, self.type, self.x, self.y)

	def can_move_to(self, x, y):
		if (x<self.pos_range[0]) or (y<self.pos_range[1]): return False
		if (x>self.pos_range[2]) or (y>self.pos_range[3]): return False
		chess = self.board.board_map.get((x, y))
		if (chess is not None) and (chess.player==self.player): 
			return False
		dx = x-self.x
		dy = y-self.y
		if (dx==0) and (dy==0): return False
		if not hasattr(self, 'allowed_moves'): return True
		if (dx, dy) in self.allowed_moves: return True
		return False

class King(ChessMan):
	def __init__(self, board, player, x, y):
		super(King, self).__init__(board, player, 'King', x, y)
		self.allowed_moves=((-1,0),(1,0),(0,-1),(0,1))
		self.pos_range=(3,0,5,2)
	def can_move_to(self, x, y):
		if super(King, self).can_move_to(x, y):
			return True
		if (self.x==x) and (self.y<y):
			cs = self.board._chesses_between(self.x, self.y, x, y)
			if cs==0:
				dest = self.board.board_map.get((x, y))
				if dest is not None:
					return dest.type == self.type
		return False

class Rock(ChessMan):
	def __init__(self, board, player, x, y):
		super(Rock, self).__init__(board, player, 'Rock', x, y)
	def can_move_to(self, x, y):
		if (self.x!=x) and (self.y!=y): return False
		if not super(Rock, self).can_move_to(x, y):
			return False
		if self.board._chesses_between(self.x, self.y, x, y) > 0:
			return False
		dest = self.board.board_map.get((x,y))
		if dest is None:
			return True
		return dest.player != self.player

class Cannon(ChessMan):
	def __init__(self, board, player, x, y):
		super(Cannon, self).__init__(board, player, 'Cannon', x, y)
	def can_move_to(self, x, y):
		if (self.x!=x) and (self.y!=y): return False
		if not super(Cannon, self).can_move_to(x, y): 
			return False
		cs = self.board._chesses_between(self.x, self.y, x, y)
		dest = self.board.board_map.get((x,y))
		if cs==0:
			return dest is None
		elif cs==1:
			return (dest is not None) and (dest.player != self.player)
		return False

class Knight(ChessMan):
	def __init__(self, board, player, x, y):
		super(Knight, self).__init__(board, player, 'Knight', x, y)
		self.allowed_moves=((-2,-1),(-2,1),(-1,-2),(-1,2),(2,-1),(2,1),(1,-2),(1,2))
	def can_move_to(self, x, y):
		if not super(Knight, self).can_move_to(x, y):
			return False
		dx = x-self.x
		dy = y-self.y
		if dx == (-2): block = (self.x-1,self.y)
		elif dx == 2: block = (self.x+1,self.y)
		elif dy == (-2): block = (self.x,self.y-1)
		elif dy == 2: block = (self.x,self.y+1)
		else: return False
		return block not in self.board.board_map

class Guard(ChessMan):
	def __init__(self, board, player, x, y):
		super(Guard, self).__init__(board, player, 'Guard', x, y)
		self.allowed_moves=((-1,-1),(-1,1),(1,-1),(1,1))
		self.pos_range=(3,0,5,2)

class Bishop(ChessMan):
	def __init__(self, board, player, x, y):
		super(Bishop, self).__init__(board, player, 'Bishop', x, y)
		self.allowed_moves=((-2,-2),(-2,2),(2,-2),(2,2))
		self.pos_range=(0,0,8,4)
	def can_move_to(self, x, y):
		if not super(Bishop, self).can_move_to(x, y):
			return False
		block = (self.x+((x-self.x)//2), self.y+((y-self.y)//2))
		return block not in self.board.board_map

class Pawn(ChessMan):
	def __init__(self, board, player, x, y):
		super(Pawn, self).__init__(board, player, 'Pawn', x, y)
		self.allowed_moves=((0,1),(-1,0),(1,0))
		self.pos_range=(0,3,8,9)
	def can_move_to(self, x, y):
		if not super(Pawn, self).can_move_to(x, y):
			return False
		return (self.y>=5) or (x==self.x)

class ChessBoard:
	def __init__(self, setting=None):
		if setting is None:
			setting = SettingLarge()
		self.setting = setting
		self._elt = None
		self._init_board()

	def rotate_board(self):
		board_map = [((i,j),chess) for (i,j),chess in self.board_map.items()]
		self.board_map.clear()
		for (i,j),chess in board_map:
			chess.x = 8-i
			chess.y = 9-j
			chess.player = 'Red' if chess.player=='Black' else 'Black'
			self.board_map[(chess.x,chess.y)] = chess

	# for debugging
	def board_map_text(self):
		name = {'Red-Pawn':'兵','Black-Pawn':'卒',
				'Red-Bishop':'相','Black-Bishop':'象',
				'Red-Guard':'仕','Black-Guard':'士',
				'Red-Cannon':'炮','Black-Cannon':'炮',
				'Red-Knight':'马','Black-Knight':'马',
				'Red-Rock':'车','Black-Rock':'车',
				'Red-King':'帅','Black-King':'将'}
		text = [['　' for x in range(9)] for y in range(10)]
		for (i,j),chess in self.board_map.items():
			text[9-j][i] = name[f'{chess.player}-{chess.type}']
		return '\n'.join([''.join([c for c in l]) for l in text])

	def _init_board(self):
		self.board_map = {}
		def init_red():
			cs = []
			cs.append(((0,0),Rock))
			cs.append(((1,0),Knight))
			cs.append(((2,0),Bishop))
			cs.append(((3,0),Guard))
			cs.append(((4,0),King))
			cs.append(((5,0),Guard))
			cs.append(((6,0),Bishop))
			cs.append(((7,0),Knight))
			cs.append(((8,0),Rock))
			cs.append(((1,2),Cannon))
			cs.append(((7,2),Cannon))
			for i in range(5):
				cs.append(((i*2,3),Pawn))
			for (x,y),t in cs:
				self.board_map[(x,y)] = t(self, 'Red', x, y)
		init_red()
		self.rotate_board()
		init_red()

	def _chesses_between(self, x1, y1, x2, y2):
		if (x1!=x2) and (y1!=y2):
			return 0
		if x1==x2:
			cs = [self.board_map.get((x1,y)) 
				for y in (range(y1+1,y2) if y1<y2 else range(y2+1,y1))]
		if y1==y2:
			cs = [self.board_map.get((x,y1)) 
				for x in (range(x1+1,x2) if x1<x2 else range(x2+1,x1))]
		return len([c for c in cs if c is not None])

	def _refresh_elt(self):
		while self._elt.lastChild.data() is not None:
			self._elt.removeChild(self._elt.lastChild)
		self.plate = Plate(self.setting)
		self._elt.appendChild(self.plate.elt)
		self.img_map = {}
		size = (self.setting.chess_size / 2)
		for (i,j), chess in self.board_map.items():
			x,y = self.plate.pos_to_pixel(i,j)
			style = {'position':'absolute','left':f'{x-size}px','top':f'{y-size}px','width':f'{self.setting.chess_size}px','opacity':0.95, 'z-index':'0'}
			img = html('img', {'src':f'chess-img/{chess.player}_{chess.type.lower()}.png','draggable':'false'}, style)
			self._elt.appendChild(img)
			self.img_map[(i,j)]=img

	def elt(self):
		if self._elt is None:
			self._elt = html('div')
			self._refresh_elt()
		return self._elt

class Controller:
	def __init__(self, chess_board):
		self.chess_board = chess_board
		elt = chess_board.elt()
		elt.bind('mouseup', self.onmouseup)
		elt.bind('mousedown', self.onmousedown)
		elt.bind('mousemove', self.onmousemove)
		self.restart()

	def restart(self):
		self.dragging_chess = None
		self.player = 'Red'
		self.chess_board._init_board()
		self.chess_board._refresh_elt()

	def onmousedown(self, ev):
		x, y = ev.x.data(), ev.y.data()
		i, j = self.chess_board.plate.pixel_to_nearest_pos(x, y)
		px, py = self.chess_board.plate.pos_to_pixel(i, j)
		if _distance(x, y, px, py) > self.chess_board.setting.chess_size:
			return
		if (i,j) not in self.chess_board.board_map:
			return
		chess = self.chess_board.board_map[(i,j)]
		if chess.player!=self.player:
			return False
		self.dragging_chess = chess
		img = self.chess_board.img_map[(i,j)]
		setattr(img.style, 'z-index', '1')

	def _can_move_chess_to(self, chess, i2, j2):
		if self.player=='Black':
			i2,j2 = 8-i2, 9-j2
			self.chess_board.rotate_board()
		succ = chess.can_move_to(i2,j2)
		if self.player=='Black':
			self.chess_board.rotate_board()
		return succ

	def _move_chess_to(self, chess, i2, j2):
		if not self._can_move_chess_to(chess, i2, j2):
			return False, None
		i1, j1 = chess.x, chess.y
		chess.x, chess.y = i2, j2
		img = self.chess_board.img_map[(i1,j1)]
		del self.chess_board.board_map[(i1,j1)]
		del self.chess_board.img_map[(i1,j1)]
		captured = None
		if (i2,j2) in self.chess_board.board_map:
			captured = self.chess_board.board_map[(i2,j2)]
			del self.chess_board.board_map[(i2,j2)]
			img0 = self.chess_board.img_map[(i2,j2)]
			del self.chess_board.img_map[(i2,j2)]
			self.chess_board.elt().removeChild(img0)
		self.chess_board.board_map[(i2,j2)] = chess
		self.chess_board.img_map[(i2,j2)] = img
		return True, captured

	def _move_chess_img(self, chess, x0, y0, animation_time=.5, animation_frames=25):
		i, j = chess.x, chess.y
		img = self.chess_board.img_map[(i,j)]
		px, py = self.chess_board.plate.pos_to_pixel(i, j)
		size = self.chess_board.setting.chess_size/2
		player = self.player
		dragging_chess = self.dragging_chess
		self.player = None
		self.dragging_chess = None
		import time
		frames = int(animation_frames*animation_time)
		for i in range(frames):
			x = x0+((px-x0)*((i+1)/frames))
			y = y0+((py-y0)*((i+1)/frames))
			img.style.left = f'{x-size}px'
			img.style.top = f'{y-size}px'
			time.sleep(1/animation_frames)
		assert x==px, (x,px)
		setattr(img.style, 'z-index', '0')
		self.player = player
		self.dragging_chess = dragging_chess

	def onmouseup(self, ev):
		if self.dragging_chess is None: return
		x, y = ev.x.data(), ev.y.data()
		i2, j2 = self.chess_board.plate.pixel_to_nearest_pos(x, y)
		px, py = self.chess_board.plate.pos_to_pixel(i2, j2)
		near = _distance(x, y, px, py) < self.chess_board.setting.chess_size
		if near:
			succ, captured = self._move_chess_to(self.dragging_chess, i2, j2)
			if succ:
				if (captured is not None) and (captured.type=='King'):
					javascript.alert(f"{'红' if self.player=='Red' else '黑'}方胜出!")
					self.restart()
					return
				self.player = 'Red' if self.player=='Black' else 'Black'
		self._move_chess_img(self.dragging_chess, x, y)
		self.dragging_chess = None

	def onmousemove(self, ev):
		if self.dragging_chess is None: return
		i,j = self.dragging_chess.x, self.dragging_chess.y
		img = self.chess_board.img_map[(i,j)]
		size = self.chess_board.setting.chess_size/2
		img.style.left = f'{ev.x.data()-size}px'
		img.style.top = f'{ev.y.data()-size}px'


def run_app():
	chess_board = ChessBoard()
	javascript.document.body.appendChild(chess_board.elt())
	Controller(chess_board)
	