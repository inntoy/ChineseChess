
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

# 单位为像素
class SettingLarge:
	offset_x = 29
	offset_y = 29-3
	grid_size_x = 59
	grid_size_y = 61
	plate_size = 535
	chess_size = 55

def _distance(x1, y1, x2, y2):
	return math.sqrt(((x1-x2)**2) + ((y1-y2)**2))

''' 
	棋盘里的数组大小为9x10，下标从0开始，原点在左下角的棋盘上，x轴向右，y轴向上
	像素坐标在图片左上角，x轴向右，y轴向下
'''
class Plate:
	def __init__(self, setting):
		self.setting = setting
		style = {'opacity':0.65, 'width':setting.plate_size,
				'position':'absolute','left':'0px','top':'0px'}
		self.elt = html('img', {'src':'chess-img/plate.png', 'draggable':'false'}, style=style)
	# 输入棋子的数组坐标(下标从0开始)，返回像素坐标
	def pos_to_pixel(self, i, j):
		x = self.setting.offset_x + (i * self.setting.grid_size_x)
		y = self.setting.offset_y + ((9 - j) * self.setting.grid_size_y)
		return x, y	
	# 返回距离像素坐标最近的数组坐标
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

# 棋子的父类，board为chessBoard类(棋盘)，player为拥有这个棋子的玩家，type为棋子的类型，x和y为棋子的数组坐标
class ChessMan:
	# 棋子能放置的范围(数组坐标)
	pos_range=(0,0,8,9)
	def __init__(self, board, player, type, x, y):
		self.board = board
		self.player = player
		self.type = type
		self.x = x
		self.y = y

	# 复制一个一模一样的棋子
	def clone(self):
		return type(self)(self.board, self.type, self.x, self.y)

	'''
	输入移动到的数组坐标，返回能否将棋子放置到此处
	一共四个检查
	1. 移动到的位置是否规定的移动范围内
	2. 移动到的位置上是否有棋子以及满不满足吃的要求
	3. 是否原地移动
	4. 当前棋子是否有自己的移动限制，如果有则进行检查
	【注意】不检查终点和起点之间有没有棋子，同时默认移动的是红方的棋子
	'''
	def can_move_to(self, x, y, show=False):
		if (x<self.pos_range[0]) or (y<self.pos_range[1]): 
			if show: print("移动到的位置(%d,%d)超出范围(%d,%d)"%(x,y, self.pos_range[0], self.pos_range[1]))
			return False
		if (x>self.pos_range[2]) or (y>self.pos_range[3]): 
			if show: print("移动到的位置(%d,%d)超出范围(%d,%d)"%(x,y, self.pos_range[2], self.pos_range[3]))
			return False

		chess = self.board.board_map.get((x, y))
		if (chess is not None) and (chess.player==self.player): 
			if show: print("禁止移动，移动处为本方棋子")
			return False

		dx = x-self.x
		dy = y-self.y
		if (dx==0) and (dy==0): 
			if show: print("不允许原地移动")
			return False	# 不允许原地移动

		# 判断当前对象里是否存在移动要求，存在则进行判断，不存在意味可以移动
		if not hasattr(self, 'allowed_moves'): return True
		if (dx, dy) in self.allowed_moves: 
			if show: print("移动方式超出移动限制")
			return True
		return False

# 将
class King(ChessMan):
	def __init__(self, board, player, x, y):
		super(King, self).__init__(board, player, 'King', x, y)
		# 将的移动限制和范围限制
		self.allowed_moves=((-1,0),(1,0),(0,-1),(0,1))
		self.pos_range=(3,0,5,2)
	def can_move_to(self, x, y, show=False):
		if super(King, self).can_move_to(x, y):
			return True
		# 如果双方将之间没有棋子间隔，可以直接移动到对方将的位置上
		if (self.x==x) and (self.y<y):
			cs = self.board._chesses_between(self.x, self.y, x, y)
			if cs==0:
				dest = self.board.board_map.get((x, y))
				if dest is not None:
					return dest.type == self.type
		return False

# 车
class Rock(ChessMan):
	def __init__(self, board, player, x, y):
		super(Rock, self).__init__(board, player, 'Rock', x, y)
	def can_move_to(self, x, y, show=False):
		# 车只能沿直线移动
		if (self.x!=x) and (self.y!=y): return False
		if not super(Rock, self).can_move_to(x, y):
			return False
		# 起点和终点之间如果有其他棋子，则不允许移动
		if self.board._chesses_between(self.x, self.y, x, y) > 0:
			return False

		# 这里重复检查了终点处的棋子
		dest = self.board.board_map.get((x,y))
		if dest is None:
			return True
		return dest.player != self.player

# 炮
class Cannon(ChessMan):
	def __init__(self, board, player, x, y):
		super(Cannon, self).__init__(board, player, 'Cannon', x, y)
	def can_move_to(self, x, y, show=False):
		# 炮只能沿直线移动
		if (self.x!=x) and (self.y!=y): return False
		if not super(Cannon, self).can_move_to(x, y): 
			return False

		# 炮只能隔着一个棋子攻击
		cs = self.board._chesses_between(self.x, self.y, x, y)
		dest = self.board.board_map.get((x,y))
		if cs==0:
			return dest is None
		elif cs==1:
			return (dest is not None) and (dest.player != self.player)
		return False

# 马
class Knight(ChessMan):
	def __init__(self, board, player, x, y):
		super(Knight, self).__init__(board, player, 'Knight', x, y)
		# 马的移动限制
		self.allowed_moves=((-2,-1),(-2,1),(-1,-2),(-1,2),(2,-1),(2,1),(1,-2),(1,2))
	def can_move_to(self, x, y, show=False):
		if not super(Knight, self).can_move_to(x, y):
			return False
		dx = x-self.x
		dy = y-self.y
		# 检查"马脚"处有没有棋子
		if dx == (-2): block = (self.x-1,self.y)
		elif dx == 2: block = (self.x+1,self.y)
		elif dy == (-2): block = (self.x,self.y-1)
		elif dy == 2: block = (self.x,self.y+1)
		else: return False
		return block not in self.board.board_map

# 士
class Guard(ChessMan):
	def __init__(self, board, player, x, y):
		super(Guard, self).__init__(board, player, 'Guard', x, y)
		# 士只能斜着走
		self.allowed_moves=((-1,-1),(-1,1),(1,-1),(1,1))
		self.pos_range=(3,0,5,2)

# 相
class Bishop(ChessMan):
	def __init__(self, board, player, x, y):
		super(Bishop, self).__init__(board, player, 'Bishop', x, y)
		# 相只能走正方形对角线，并且只能在自己的一边移动
		self.allowed_moves=((-2,-2),(-2,2),(2,-2),(2,2))
		self.pos_range=(0,0,8,4)
	def can_move_to(self, x, y, show=False):
		if not super(Bishop, self).can_move_to(x, y):
			return False
		
		# 检查对角线上有没有棋子，如果有则无法移动
		block = (self.x+((x-self.x)//2), self.y+((y-self.y)//2))
		return block not in self.board.board_map

# 兵
class Pawn(ChessMan):
	def __init__(self, board, player, x, y):
		super(Pawn, self).__init__(board, player, 'Pawn', x, y)

		# 兵只能往前，左，右走
		self.allowed_moves=((0,1),(-1,0),(1,0))
		# 兵的移动范围
		self.pos_range=(0,3,8,9)
	def can_move_to(self, x, y, show=False):
		if not super(Pawn, self).can_move_to(x, y):
			return False
		# 兵在过河前只能往前走
		return (self.y>=5) or (x==self.x)

# 棋盘，会存储棋子的位置以及棋盘的像素大小
class ChessBoard:
	def __init__(self, setting=None):
		if setting is None:
			setting = SettingLarge()
		self.setting = setting
		self._elt = None  # 棋盘的div，里面只保存棋子的DOM对象
		self._init_board()

	# 将红黑方棋子对调((0,0)转换到(8,9))
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

	# 在棋盘的字典里创立所有的棋子
	def _init_board(self):
		# 棋盘字典里存储棋子的对象(下棋用)
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
				self.board_map[(x,y)] = t(self, 'Red', x, y)  # 棋盘，阵营，数组坐标
		init_red()
		self.rotate_board()
		init_red()

	# 只能检测横或竖线上有几个棋子
	def _chesses_between(self, x1, y1, x2, y2):
		if (x1!=x2) and (y1!=y2):
			return 0
		# 竖线
		if x1==x2:
			cs = [self.board_map.get((x1,y)) 
				for y in (range(y1+1,y2) if y1<y2 else range(y2+1,y1))]
		# 横线
		if y1==y2:
			cs = [self.board_map.get((x,y1)) 
				for x in (range(x1+1,x2) if x1<x2 else range(x2+1,x1))]
		return len([c for c in cs if c is not None])

	# 根据棋盘字典，重新在DOM里创建所有棋子的图片对象
	def _refresh_elt(self):
		while self._elt.lastChild.data() is not None:
			self._elt.removeChild(self._elt.lastChild)
		self.plate = Plate(self.setting)
		self._elt.appendChild(self.plate.elt)

		# 图像字典主要存储棋子的DOM对象，只用于修改属性(显示用)
		self.img_map = {}

		size = (self.setting.chess_size / 2)
		for (i,j), chess in self.board_map.items():
			x,y = self.plate.pos_to_pixel(i,j)
			style = {'position':'absolute','left':f'{x-size}px','top':f'{y-size}px','width':f'{self.setting.chess_size}px','opacity':0.95, 'z-index':'0'}
			img = html('img', {'src':f'chess-img/{chess.player}_{chess.type.lower()}.png','draggable':'false'}, style)
			self._elt.appendChild(img)
			self.img_map[(i,j)]=img  # 只要修改这里的对象DOM里也会发生改变

			# 对于黑方的棋子，都旋转180度
			if chess.player == 'Black':
				setattr(img.style, 'transform', 'rotateZ(180deg)')

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
		self.player = 'Red'  # 当前回合的下棋方
		self.chess_board._init_board()
		self.chess_board._refresh_elt()

	'''
	0. 检查此时是否有棋子正在拖拽中，如果有则退出
	1. 获取距离鼠标点击坐标最近的棋盘上的坐标
	2. 检查鼠标点击的坐标和棋盘上坐标是否距离大于棋子距离
	3. 检查棋盘坐标上是否有棋子；如果有，是否是当前下棋方的
	4. 获得相应棋子的图片DOM对象，并修改其属性
	'''
	def onmousedown(self, ev):
		if self.dragging_chess is not None:
			return
		x, y = ev.x.data(), ev.y.data()
		i, j = self.chess_board.plate.pixel_to_nearest_pos(x, y)
		px, py = self.chess_board.plate.pos_to_pixel(i, j)
		if _distance(x, y, px, py) > self.chess_board.setting.chess_size:
			return
		if (i,j) not in self.chess_board.board_map:
			return
		chess = self.chess_board.board_map[(i,j)]
		if chess.player!=self.player:
			return 
		self.dragging_chess = chess
		img = self.chess_board.img_map[(i,j)]
		setattr(img.style, 'z-index', '1')  # 注意这里z-index的值是一个字符

	# 对于黑方，移动到的坐标会进行变换，并且棋盘也会进行调换
	def _can_move_chess_to(self, chess, i2, j2):
		if self.player=='Black':
			i2,j2 = 8-i2, 9-j2
			self.chess_board.rotate_board()
		succ = chess.can_move_to(i2,j2)
		if self.player=='Black':
			self.chess_board.rotate_board()
		return succ
	
	'''
	移动棋子到目标点，输入要移动的棋子和目标点坐标，返回运行结果和被吃掉的棋子(如果移动成功且目标点有敌方棋子时)
	注意，这个函数对于拖拽的棋子不会影响其在HTML上的显示，只会影响其在数组里的值和位置
	'''
	def _move_chess_to(self, chess, i2, j2):
		if not self._can_move_chess_to(chess, i2, j2):
			return False, None

		# 接下来是移动棋子需要在棋盘以及在HTML上做的处理
		i1, j1 = chess.x, chess.y
		chess.x, chess.y = i2, j2
		# 删除掉该棋子在棋盘字典和图像字典上的信息(没有在HTML上删除)
		img = self.chess_board.img_map[(i1,j1)]
		del self.chess_board.board_map[(i1,j1)]
		del self.chess_board.img_map[(i1,j1)]
		captured = None
		if (i2,j2) in self.chess_board.board_map:
			# 删除被吃掉的棋子在棋盘字典里的信息
			captured = self.chess_board.board_map[(i2,j2)]
			del self.chess_board.board_map[(i2,j2)]
			# 删掉该棋子在图像字典和DOM对象里的信息(网页上完全删除这个棋子的图像)
			img0 = self.chess_board.img_map[(i2,j2)]
			del self.chess_board.img_map[(i2,j2)]
			self.chess_board.elt().removeChild(img0)

		# 这里只是修改了两个字典里存储的信息，还没有在HTML对修改的信息进行显示
		self.chess_board.board_map[(i2,j2)] = chess
		self.chess_board.img_map[(i2,j2)] = img
		return True, captured

	'''
	x0,y0为鼠标点击抬起(结束)时的像素坐标，为图像移动的起点
	chess里的数组坐标i,j，对应的像素坐标px,py，为图像移动的终点
	如果棋子顺利移动到目标位置，那么这里的px,py就是目标位置数组坐标的像素坐标
	如果棋子没有顺利移动到目标位置，那么这里的px,py就是棋子原始位置的像素坐标
	'''
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
		i2, j2 = self.chess_board.plate.pixel_to_nearest_pos(x, y)  # 鼠标抬起时的最近的数组坐标
		px, py = self.chess_board.plate.pos_to_pixel(i2, j2)
		near = _distance(x, y, px, py) < self.chess_board.setting.chess_size
		if near:
			succ, captured = self._move_chess_to(self.dragging_chess, i2, j2)
			if succ:
				if (captured is not None) and (captured.type=='King'):
					javascript.alert(f"{'红' if self.player=='Red' else '黑'}方胜出!")
					self.restart()
					return
				self.player = 'Red' if self.player=='Black' else 'Black'  # 更换下棋方
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
