import time
import random

from . import chess
from . import spinner
from . import ajax
from . import  auto_chess
from . import chessvalue

class ControllerPro(chess.Controller):
    def __init__(self, chess_board, bothAI = False):
        super(ControllerPro, self).__init__(chess_board)
        self.bothAI = bothAI
        self.run = False # 给AI进行判断

    def onmousedown(self, ev):
        # 电脑对战的时候重写onmousedown事件
        if(self.bothAI): return

        super(ControllerPro, self).onmousedown(ev)
    
    def onmousemove(self, ev):
        # 电脑对战的时候重写onmousedown事件
        if(self.bothAI): return

        super(ControllerPro, self).onmousemove(ev)
    
    def onmouseup(self, ev):
        if(self.bothAI):
            self.run = not self.run
            while(self.run):
                result = self.AIcontrol()
                if result is not None:
                    self.run = False
                    return
                time.sleep(.5)

        else:
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
                    javascript.alert("红方胜出!" if self.player == 'Red' else "黑方胜出!")
                    self.restart()
                    return
                self.player = changePlayer(self.player)
            self.dragging_chess = None
            
            # 如果下棋正常，那么就轮到AI方下棋
            if succ:
                self.AIcontrol()

    def AIcontrol(self):
        spinner.show()
        if(self.player == 'Black'): self.chess_board.rotate_board()
		# move = auto_move(self.chess_board)
        try:
            board_key = auto_chess._board_key(self.chess_board) # board_key 可变为 JSON
            move = ajax.rpc.rpc_auto_move(board_key)
        except RuntimeError as ex:
            javascript.alert(str(ex))
            return
        if(self.player == 'Black'): self.chess_board.rotate_board()
        spinner.hide() 

        if move is None:
            javascript.alert("黑方胜出！" if self.player == 'Black' else "红方胜出!")
            self.restart()
            return 'Finished'
        i1,j1,i2,j2 = move  # i1,j1为棋子的位置，i2,j2为要移动的位置，均为数组坐标

        if(self.player == 'Black'): i1,j1,i2,j2 = 8-i1,9-j1,8-i2,9-j2

        chess = self.chess_board.board_map[(i1,j1)]
        succ, captured = self._move_chess_to(chess, i2, j2)	# 移动到i2,j2，如果成功则chess里的存储的数组坐标会变为i2,j2
        assert succ
        px, py = self.chess_board.plate.pos_to_pixel(i1, j1)
        self._move_chess_img(chess, px, py)		# HTML上让图片从i1,j1移动到chess里存储的位置，即i2,j2
        if (captured is not None) and (captured.type=='King'):
            javascript.alert("黑方胜出！" if self.player == 'Black' else "红方胜出!")
            self.restart()
            return 'Finished'
        
        self.player = changePlayer(self.player)
        return None


def changePlayer(player):
    if player == 'Red':
        return 'Black'
    elif player == 'Black':
        return 'Red'

# 后端要调用的代码
# AI默认第一个下的是红方
# 传入的棋盘是chessBoard类型的

board_explore = None
name_change = {
    'King':'将',
    'Guard': '士',
    'Bishop': '象',
    'Knight': '马',
    'Rock': '车',
    'Cannon': '炮',
    'Pawn': '兵'
}
# 开局下法
beginMove = [
    #当头炮(炮二平五或炮八平五)
    ('Red', 'Cannon', 7, 2, 4, 2),
    ('Red', 'Cannon', 1, 2, 4, 2),
    #飞相(相三进五)
    ('Red', 'Bishop', 6, 0, 4, 2),
    #仙人指路
    ('Red', 'Pawn', 2, 3, 2, 4),
    #屏风马
    ('Red', 'Knight', 7, 0, 6, 2),
    ('Red', 'Knight', 1, 0 ,2, 2),
]
# 判断是否为开局，我方(红方)没有棋子动，而对方(黑方)没有或者只有一枚棋子动即为开局
def isBegin(board):
    blackMove = 0
    for pos,chess in board.board_map.items():
        if chess.player == 'Black':
            pos = (8-pos[0], 9-pos[1])
        move = False
        if chess.type == 'King':
            if pos not in ((4,0),):
                move = True
        elif chess.type == 'Cannon':
            if pos not in ((1,2), (7,2)):
                move = True
        elif chess.type == 'Knight':
            if pos not in ((1,0), (7,0)):
                move = True
        elif chess.type == 'Rock':
            if pos not in ((0,0), (8,0)):
                move = True
        elif chess.type == 'Pawn':
            if pos not in ((0,3), (2,3), (4,3), (6,3), (8,3)):
                move = True
        elif chess.type == 'Guard':
            if pos not in ((3,0), (5,0)):
                move = True
        elif chess.type == 'Bishop':
            if pos not in ((2,0), (6,0)):
                move = True
        
        if move and (chess.player == 'Red'):
            return False
        elif move and (chess.player == 'Black'):
            blackMove = blackMove+1
        
        if blackMove > 1:
            return False

    return True

def auto_move(board):
    global board_explore
    if board_explore is None:
        board_explore = BoardExplore(board, 8)
    else:
        board_explore.reload(board)
    
    board_explore.IterSearch()
    
    return board_explore.bestmove[2:]


# 需要传入chessBoard类型的棋盘
class BoardExplore:
    def __init__(self, board, limitTime = 3):
        assert board is not None
        self.board = board
        self.historylist = {}   # 历史表，可以用于判断哪步下法先进行搜索，键为下法(全部为红方视角下的下法)，值为值得搜索的分数(高度的平方)
        self.replacementlist = {}   # 置换表，用于减少搜索时间，加深搜索深度，键为棋盘局面，值为该局面分数
        self.limitTime = limitTime  # 总共能运行的时间，单位秒
        self.depth = 1      # 要进行搜索的深度
        self.bestmove = None    # 最好的下法
        self.win = 10000    # 红方获胜分数的上界，黑方就是-win
        self.MAXPLY = 200  # 如果score>win-MAXPLY(score<-win+MAXPLY)，则此分数为红方(黑方)获胜的情况
        self.WIN_VALUE = self.win - self.MAXPLY  # 红方获胜分数的下界， 黑方就是-WIN_VALUE
        self.draw = 0      # 平局分数，如果是红方逼和，则为draw的分数，此时下法就会偏保守，反之(-draw)则会偏激进，设置为0则表示均衡
        self.BAN_VALUE = self.win-100 # 长将判负的分数

        self.nodeNum = 0    # 进行了局面评估的节点数量

        self.killermove = {}  # 杀手走法，每一层都有杀手走法(除了根结点)，每次AI下棋时要清除这个列表里的数据
        self.parentlist = set() # 棋盘情况的父节点，用于检查重复情况，只在静态搜索时使用
        
        self.checkdepth = 0  # 由于将军延伸导致的深度变化
        self.depthToRoot = 0    # 当前节点相对于根结点的深度，只有在变换棋盘的时候才会发生改变
        self.MAX_DEPTH = 20    # 最大搜索深度
        self.DICT_ITEM_MAXNUM = 1 << 20 # 字典里项目的最大项数

        self.HASH_ALPH = 0  # 节点确定为alpha节点，即值不超过下界(从极大值方的角度看)
        self.HASH_BETA = 1  # 节点确定为beta节点，即值不小于上界(从极大值方的角度看)
        self.HASH_PV = 2    # 节点为pv节点，值确定在一定范围内
    
    # 重新加载棋盘
    def reload(self, board):
        self.board = board

    # 检查玩家的“将”棋是否存在
    def hasKing(self, player):
        for _, piece in self.board.board_map.items():
            if(piece.player == player) and (piece.type == 'King'):
                return True
        return False

    # 修改胜利情况下的分数，主要是用在将得分存入置换表中
    # 这里的深度要为当前节点到根结点的高度
    def modifyScore(self, score, depth=0):
        r_score = score
        # 将分数存入置换表时要做的处理
        if score > (self.win - self.MAXPLY):      # 红方获胜的情况
            r_score = r_score + depth
        elif score < ((0-self.win) + self.MAXPLY):   # 黑方获胜的情况
            r_score = r_score - depth
        return r_score

    # TODO 评估棋子的子力
    def evaluateChess(self, chess):

        if chess.player == 'Red':
            return chessvalue.ChessValue.RedPositionValue[chess.type][chess.y][chess.x] + chessvalue.ChessValue.ChessBasicValue[chess.type]
        elif chess.player == 'Black':
            return chessvalue.ChessValue.BlackPositionValue[chess.type][chess.y][chess.x] + chessvalue.ChessValue.ChessBasicValue[chess.type]

    # TODO 评估局面函数，这里的深度depth为从当前评估节点到根结点的深度
    def evaluate(self, player, depth=0):
        
        # 先判断当前下棋方是否被将死
        # 注意，当前下棋方被将死说明对面下的好，这时候要根据对面是什么方来给分数
        # 如果对面是红方，则返回正无穷或一个较大的数字，反之返回负无穷或一个较小的数字
        if(not self.hasKing(player)):
            if(player == 'Red'): # 红方输了
                return (-self.win) + depth
            else: # 黑方输了
                return self.win - depth

        # 评分方式，红方棋子减去黑方棋子的分数
        score = 0
        # 统计一下此时各方拥有的棋子数
        # redChess = {'King': 0,'Guard': 0,'Bishop': 0,'Knight': 0,'Cannon': 0,'Rock': 0,'Pawn': 0}
        # blackChess = {'King': 0,'Guard': 0,'Bishop': 0,'Knight': 0,'Cannon': 0,'Rock': 0,'Pawn': 0}
        
        for _,chess in self.board.board_map.items():
            if chess.player == 'Red':
                score = score + self.evaluateChess(chess)
                # 如果出现窝心马(马在将九格的中心时)，则会扣分
                if (chess.type == 'Knight') and ((chess.x == 4) and (chess.y == 1)):
                    score = score - 20
            else:
                score = score - self.evaluateChess(chess)
                # 黑方出现窝心马则会加分
                if (chess.type == 'Knight') and ((chess.x == 4) and (chess.y == 8)):
                    score = score + 20

        return score
    
    # 改变棋盘，如果有吃子则返回被吃的棋子
    # 返回的被吃的棋子是正确的坐标
    def changeBoard(self, move, maximizingPlayer):
        # 如果是黑方下棋，则需要对坐标进行改变
        # TODO: 传入的move是tuple类型，要先转为list类型
        this_move = [_ for _ in move]
        if not maximizingPlayer:
            this_move[0] = 'Black'
            this_move[2] = 8-this_move[2]  # chess.x
            this_move[3] = 9-this_move[3]  # chess.y
            this_move[4] = 8-this_move[4]  # x
            this_move[5] = 9-this_move[5]  # y
        
        # print('change, move: ', this_move)
        captureChess = self.board.board_map.get((this_move[4], this_move[5]))
        chess = self.board.board_map.get((this_move[2], this_move[3]))
        # 如果棋子不存在，则报错
        assert chess is not None

        # 距离根结点的深度+1
        self.depthToRoot = self.depthToRoot+1

        # 删掉当前的棋子和将要被移动到的位子上的棋子(如果有)
        del self.board.board_map[(this_move[2], this_move[3])]
        if captureChess is not None:
            del self.board.board_map[(this_move[4], this_move[5])]
        # 更新棋子的位子并插入到board_map上
        chess.x = this_move[4]
        chess.y = this_move[5]
        self.board.board_map[(chess.x, chess.y)] = chess

        return captureChess

    # 恢复棋盘，如果有子被占领则恢复
    def recoverBoard(self, move, maximizingPlayer, captureChess=None):
        # 如果是黑方下棋，要先恢复正确的坐标
        this_move = [_ for _ in move]
        if not maximizingPlayer:
            this_move[0] = 'Black'
            this_move[2] = 8-this_move[2]  # chess.x
            this_move[3] = 9-this_move[3]  # chess.y
            this_move[4] = 8-this_move[4]  # x
            this_move[5] = 9-this_move[5]  # y
            
        # print("recover, move: ", this_move)
        # 此时棋子已经移动到了x，y坐标上了
        chess = self.board.board_map.get((this_move[4], this_move[5]))
        assert chess is not None
        
        # 距离根结点的深度-1
        self.depthToRoot = self.depthToRoot-1

        # 删除这个棋子
        del self.board.board_map[(chess.x, chess.y)]
        # 重新添加几个棋子
        chess.x = this_move[2]
        chess.y = this_move[3]
        self.board.board_map[(chess.x, chess.y)] = chess
        # 如果有棋子被吃掉就重新添加回棋盘
        if captureChess is not None:
            self.board.board_map[(captureChess.x, captureChess.y)] = captureChess

    # 给吃子着法进行排序
    # 注意:如果着法是红方的着法，调用这个函数前不需要调用board.rotate_board函数
    # 如果着法是黑方的着法，调用这个函数前必须要调用board.rotate_board函数，这是因为isProtect函数要在红方的视角下判断
    def sortCapMove(self, moves_cap, maximizingPlayer=None):
        for idx, move in enumerate(moves_cap):
            loss_score = 0  # 丢失这枚进行攻击的棋子的分数
            get_score = 0   # 被吃的棋子的分数
            
            capChess = self.board.board_map.get((move[4], move[5]))
            # 假如有不吃子的着法，给最低分数
            if capChess is None:
                if len(move) == 7: move = move[:-1] + (-self.win,)
                elif len(move) == 6: move = move + (-self.win)
                moves_cap[idx] = move
                continue
            # 假如被吃的棋子为帅，那么直接给最高分
            elif capChess.type == 'King':
                if len(move) == 7: move = move[:-1] + (self.win,)
                elif len(move) == 6: move = move + (self.win)
                moves_cap[idx] = move
                continue

            attackChess = self.board.board_map.get((move[2], move[3]))

            if self.isProtected(capChess, attackChess):
                loss_score = self.evaluateChess(attackChess)

            get_score = self.evaluateChess(capChess)

            # 当移动最后一行存在分数时
            #    0         1           2        3    4  5   6
            # (player, chess.type, chess.x. chess.y, x, y, score)
            if len(move) == 7:
                move = move[:-1] + (get_score-loss_score,)
            elif len(move) == 6:
                move = move + (get_score-loss_score,)

            moves_cap[idx] = move
        
        # NOTE：不知道这个方法是否被能实现
        if len(moves_cap) > 0:
            moves_cap.sort(key=lambda a:a[-1], reverse=True)
    
    # 输出在玩家视角下的棋子信息
    def _printChessMessage(self, chess):
        return "(%d, %d)处%s方的%s"%(8-chess.x, 9-chess.y, changePlayer(chess.player), chess.type)
    
    # 输出棋盘情况，是我们玩家视角下的棋盘(不是电脑视角下的)
    def _printBoard(self):
        for y in range(10):
            for x in range(9):
                show_x = 8-x
                show_y = y
                show_chess = self.board.board_map.get((show_x,show_y))
                if show_chess is not None:
                    player = '黑' if show_chess.player == 'Red' else '红'
                    type = name_change[show_chess.type]
                    print("%s%s(%d,%d)"%(player,type,8-show_chess.x,9-show_chess.y), end='\t')
                else:
                    print('    (%d,%d)'%(x,9-y), end='\t')
            print()
        

    # 检查棋子是否被保护，这里要模仿攻击棋子已经吃掉了当前的棋子
    # 注意：如果棋子的坐标要和self.board上的一致(不能只使用_correctMove函数)。
    # 如果是黑方着法，调用这个函数前一定要使用board.rotate_board函数
    def isProtected(self, c_chess, a_chess = None):
        assert c_chess is not None

        # 删除攻击棋子和被吃掉的棋子，移动攻击棋子到被吃掉的棋子处
        del self.board.board_map[(c_chess.x, c_chess.y)]
        if(a_chess is not None):
            a_chess_x = a_chess.x
            a_chess_y = a_chess.y
            del self.board.board_map[(a_chess.x, a_chess.y)]
            a_chess.x = c_chess.x
            a_chess.y = c_chess.y
            self.board.board_map[(c_chess.x, c_chess.y)] = a_chess
        
        player = c_chess.player
        protected = False
        for _, _chess in self.board.board_map.items():
            # 是同阵营的棋子且可以移动到当前棋子处
            if(_chess.player == player) and (_chess.can_move_to(c_chess.x, c_chess.y)):
                protected = True
                break
        
        # 重新把棋子添加回去
        if(a_chess is not None):
            del self.board.board_map[(c_chess.x, c_chess.y)]
            a_chess.x = a_chess_x
            a_chess.y = a_chess_y
            self.board.board_map[(a_chess.x, a_chess.y)] = a_chess
        self.board.board_map[(c_chess.x, c_chess.y)] = c_chess
        return protected


    # 改进的alpha-beta减枝算法，这里称为pvs(主要変例搜索法)
    # 极大方玩家为红方，极小方玩家为黑方，这里的depth为还要进行搜索的深度，也为该结点在树中的高度
    def pvs(self, alpha, beta, depth, maximizingPlayer):
        # 定义本层玩家名称，以及当前节点的取值的界限
        # 对于极大层(红方)玩家，界限是下界，初始值为负无穷或一个比较小的分数，当前节点目标是使取值的下界尽可能大
        # 对于极小层(黑方)玩家，界限是上界，初始值为正无穷或一个比较大的分数，当前节点目标是使取值的上界尽可能小
        player, limit = ('Red', 0-self.win) if maximizingPlayer else ('Black', self.win)
        bestmove = None     # 当前节点的最好走法，一般是出现截断或者节点的值刚好在规定范围内的情况
        alpha_move = None   # 没有产生截断，同时节点值不在规定范围内的解法
        now_board = (player,)+auto_chess._board_key(self.board)

        # 1. 如果此时自己的帅已经被吃了，则返回应该有的分数
        if not self.hasKing(player):
            self.nodeNum = self.nodeNum + 1
            return self.evaluate(player, self.depthToRoot)
        # 1.5 到达0深度后直接使用静态搜索
        elif(depth == 0):
            self.nodeNum = self.nodeNum + 1
            score = self.Quiesearch(alpha, beta, maximizingPlayer)
            return score
        
        # 2. 检查重复局面    
        # 优先判断是否存在重复局面，如果存在则判平或判负
        if now_board in self.parentlist:
            # 长将直接判负
            if (self.InCheck(maximizingPlayer)):
                print("长将， {}方判负".format('红' if maximizingPlayer else '黑')) # 这是真实情况下的输出
                score = self.BAN_VALUE-self.depthToRoot if maximizingPlayer else (-self.BAN_VALUE)+self.depthToRoot
                if self.show:
                    self._printBoard()
                    self.show = False
                return score
            else:
                print("相同局面，平局")
                return self.draw if maximizingPlayer else (-self.draw)
        
        # 3. 检查是否到达最大搜索深度，如果达到则直接返回评估结果
        if self.depthToRoot > self.MAX_DEPTH:
            return self.evaluate(player, self.depthToRoot)


        # 4. 检查置换表中是否有合理的走法
        rep_move = None
        if now_board in self.replacementlist:
            # 先获得置换表下法和此下法的分数
            rep_move = self.replacementlist[now_board][2]
            score = self.replacementlist[now_board][1]
            # 如果是根结点，则不进行置换表裁剪
            if self.isroot:
                self.isroot = False
            # 置换表里的下法是否大于本节点的继续搜索深度，如果是获胜情况，则不受深度限制
            elif (self.replacementlist[now_board][0] >= depth) or ((score > self.WIN_VALUE) or (score < (-self.WIN_VALUE))):
                continueCheck = False
                # 判断置换表中下法是否为长将判负的情况，如果是则不能直接使用，只能使用其中的下法
                if maximizingPlayer and ((score > self.WIN_VALUE) and (score <= self.BAN_VALUE)):
                    continueCheck = True
                elif (not maximizingPlayer) and ((score < (-self.WIN_VALUE)) and (score >= (-self.BAN_VALUE))):
                    continueCheck = True
                
                if not continueCheck:
                    # 修正分数
                    if maximizingPlayer and (score > self.WIN_VALUE):score = score - self.depthToRoot 
                    elif (score < (-self.WIN_VALUE)): score = score + self.depthToRoot

                    # 判断能否使用置换表进行替换，如果表中项为beta或alpha节点，那么只有当分数超出了范围才能裁剪
                    # 对于极大值方，beta节点指值不小于此分数，alpha节点指值不大于此分数
                    # 对于极小值方，beta节点指值不大于此分数，alpha节点指值不小于此分数
                    flag = self.replacementlist[now_board][3]
                    # 极大值方
                    if maximizingPlayer:
                        if (flag == self.HASH_BETA):
                            if score >= beta:
                                return score
                        elif(flag == self.HASH_ALPH):
                            if score <= alpha:
                                return score
                        else:
                            return score
                    # 极小值方
                    else:
                        if (flag == self.HASH_BETA):
                            if (score <= alpha):
                                return score
                        elif(flag == self.HASH_ALPH):
                            if score >= beta:
                                return score
                        else:
                            return score

             

        # 将当前棋盘加入祖先列表中
        self.parentlist.add(now_board)

        #————————————————————————————————获得下法—————————————————————————————————
        # 如果是极小层方(黑方)下棋，则把棋盘倒转过来
        if(not maximizingPlayer):
            self.board.rotate_board()
        
        # TODO:获得所有下法，并且分为置换表着法，杀手(killer)着法，吃子着法和不吃子着法
        moves = []
        moves_cap = []  # 吃子着法
        moves_nocap = [] # 不吃子着法
        moves_kill = []  # 杀手着法
        move_rep = None  # 启发式走法
        for _, chess in self.board.board_map.items():
            if chess.player == 'Black': continue
            for x, y in auto_chess._chess_moves(chess):
                # 在历史表里查找当前走法的分数，因为字典的键不能用list类型，所以要用tuple
                '''注意，对于黑方来说，move里的坐标是翻转后的坐标，这里先不进行改变'''
                move = ('Red', chess.type, chess.x, chess.y, x, y)
                score = self.historylist[move] if move in self.historylist else 0
                move = move + (score,)

                # NOTE：因为得到的所有着法最后一个值为历史表中的值，置换表走法和杀手走法里的着法不包括这一项，所以要用move[:-1]去比较
                # 先判断当前着法是否属于置换表中的着法，如果是则该着法有先执行
                if move[:-1] == rep_move:
                    move_rep = [move]
                    continue
                # 如果存在吃子情况
                if self.board.board_map.get((x, y)) is not None:
                    moves_cap.append(move)
                # 除此之外，如果是不吃子的着法，查看它是否属于杀手走法
                elif (self.killermove.get((self.depthToRoot, maximizingPlayer)) is not None) and (move[:-1] in self.killermove[(self.depthToRoot, maximizingPlayer)]):
                    moves_kill.append(move)
                else:
                    moves_nocap.append(move)
                

        # 对吃子着法进行排序，这个函数一定要在正确的棋盘下使用，它不会修正坐标
        self.sortCapMove(moves_cap)
        # 如果是黑方下棋，得到所有下法后要把棋盘翻转回去
        if(not maximizingPlayer):
            self.board.rotate_board()

        # 通过历史表中每一种下法的分数，给没有吃子的下法从大到小排序
        moves_nocap.sort(key=lambda a:a[-1], reverse=True)
        # 整合所有的下法
        if (move_rep is not None) and (len(moves_kill) > 0):
            moves = (move_rep + (moves_cap + (moves_kill + (moves_nocap))))
        elif (move_rep is not None) and (len(moves_kill) == 0):
            moves = (move_rep + (moves_cap + (moves_nocap)))
        elif (move_rep is None) and (len(moves_kill) > 0):
            moves = (moves_cap + (moves_kill + (moves_nocap)))
        else:
            moves = moves_cap + moves_nocap

        #—————————————————————————————————————————————————————————————————————————
        
        #————————————————————————————————搜索最佳下法—————————————————————————————————
        notFoundPv = True
        nodeFlag = self.HASH_ALPH
        for move in moves:
            score = None

            if(maximizingPlayer):
                # 1. 下这一步
                capture_chess = self.changeBoard(move, maximizingPlayer)

                newDepth = depth - 1
                isCheck = self.InCheck(maximizingPlayer)
                # 2.1 将军延伸
                if isCheck:
                    newDepth = depth
                    self.checkdepth = self.checkdepth+1
                # 2.2 使用pvs搜索(零窗口搜索范围为(alpha, alpha+1))
                if notFoundPv:
                    # 下这一步能得到的分数，是否比本层的下界大，如果大则更新本层下界
                    score = self.pvs(alpha, beta, newDepth, False)
                else:
                    # 先使用零窗口情况进行搜索
                    score = self.pvs(alpha, alpha+1, newDepth, False)
                    # 如果是主要变例(即分数在规定范围内)，则在(score, beta)的范围内搜索下面的节点
                    if (alpha < score) and (score < beta):
                        score = self.pvs(score, beta, newDepth, False)
                    # 如果分数不小于上界beta，那说明肯定是要被裁剪的情况，这时不需要再进行搜索了
                if isCheck:
                    self.checkdepth = self.checkdepth-1
                
                # if (depth >= 2) and (self.depth >= 2):
                #     print("(搜索深度%d，当前深度%d)时,"%(self.depth, depth),self._correctMove(move, False), "下法分数：%d, 上下界(%d,%d)"%(score, alpha, beta))

                # 3. 撤销这一步棋，将棋盘恢复成原来的样子
                self.recoverBoard(move, maximizingPlayer, capture_chess)

                '''
                注意下面这一步！！！
                本层为极大层，上一层就是极小层，上面那一层希望本层所有节点取值的上界越小越好。
                通过一些计算，上一层得到了希望的取值范围，即[alpha,beta]，所以要判断本层节点的取值在不在这个范围内
                因为本层为极大层，所以所有节点都在扩展下界。如果当前节点的下界limit超过了上一层给本层规定的上界beta，
                那么当前节点可以不需要再进行搜索了(因为当前节点的下界只会更大不会更小)，因此可以直接结束本层的搜索
                次剪枝策略称为beta剪枝(根据上界beta减少下一层节点的节点搜索数量)

                注意根结点隶属于极大层，此时不会进行裁剪(因为没有上一层了)
                '''
                # 4. 查看本次着法能否提高本节点的下界值，如果能则更新下界值alpha
                # 只保留能产生截断和主要变例的节点值
                if score > limit:
                    limit = score
                    alpha_move = move[:-1]
                    if score >= beta:
                        nodeFlag = self.HASH_BETA
                        bestmove = move[:-1]
                        break
                    if score > alpha:
                        nodeFlag = self.HASH_PV
                        bestmove = move[:-1]
                        alpha = score
                        notFoundPv = False

            else: # 本层为极小层
                # 1. 下这一步
                capture_chess = self.changeBoard(move, maximizingPlayer)

                newDepth = depth - 1
                isCheck = self.InCheck(maximizingPlayer)
                # 将军延伸
                if isCheck:
                    newDepth = depth
                    self.checkdepth = self.checkdepth+1
                # 使用pvs搜索(零窗口搜索范围为(beta-1, beta))
                if notFoundPv:
                    score = self.pvs(alpha, beta, newDepth, True)
                else:
                    score = self.pvs(beta-1, beta, newDepth, True)
                    # 分数在规定范围内，因此为主要变例，此时重新搜索
                    if (alpha < score) and (score < beta):
                        score = self.pvs(alpha, score, newDepth, True)
                if isCheck:
                    self.checkdepth = self.checkdepth-1

                # 3. 撤销这一步棋，将棋盘恢复成原来的样子
                self.recoverBoard(move, maximizingPlayer, capture_chess)

                # if (depth >= 2) and (self.depth >= 2):
                #     print("(搜索深度%d，当前深度%d)时,"%(self.depth, depth),self._correctMove(move, True), "下法分数：%d, 上下界(%d,%d)"%(score, alpha, beta))

                # 4. 对得分进行分析，获取走法
                # 如果本层上界比预定上界还要小，则更新
                # 上一层为极大层，给所有输入本层的节点规定了下界alpha
                # 此时上界一直在变，当上界小于规定的下界alpha时，停止搜索
                # 此剪枝策略称为alpha剪枝(根据下界alpha减少下一层节点的节点搜索数量)
                if score < limit:
                    limit = score
                    alpha_move = move[:-1]
                    if score <= alpha:
                        nodeFlag = self.HASH_BETA
                        bestmove = move[:-1]
                        break
                    if score < beta:
                        nodeFlag = self.HASH_PV
                        bestmove = move[:-1]
                        beta = score
                        notFoundPv = False

        #—————————————————————————————————————————————————————————————————————————

        #————————————————————————————————对下法进行一些处理—————————————————————————————————
        # 1. 将最好的下法保存进历史表里(如果最好下法不为空时)
        if bestmove is not None:
            if bestmove not in self.historylist:
                self.historylist[bestmove] = 0
            self.historylist[bestmove] = self.historylist[bestmove] + (depth * depth)
        

        # 2. 当此时为根结点时(当前深度为搜索深度且此时为极大方下棋)
        if (depth == self.depth) and maximizingPlayer:
            self.bestmove = bestmove
        
        # 3. 将下法添加到置换表中
        replaceNode = self.replacementlist.get(now_board)
        if bestmove is not None: 
            # 置换表中还没有该节点时，直接最佳走法存入置换表中
            if replaceNode is None:
                self.replacementlist[now_board] = [depth, self.modifyScore(limit, self.depthToRoot), bestmove, nodeFlag]
            # 置换表中存在该节点，如果当前走法的深度不小于置换表中走法的深度，就更新
            elif depth >= replaceNode[0]:
                self.replacementlist[now_board] = [depth, self.modifyScore(limit, self.depthToRoot), bestmove, nodeFlag]
        # 如果此时是没有发生截断的节点，也保存此走法，但深度设置为0
        elif(alpha_move is not None):
            if replaceNode is None:
                self.replacementlist[now_board] = [0, self.modifyScore(limit, self.depthToRoot), alpha_move, nodeFlag]
            elif (replaceNode[0] == 0):
                self.replacementlist[now_board] = [0, self.modifyScore(limit, self.depthToRoot), alpha_move, nodeFlag]

        # 4. 将该下法放入杀手着法表中，每一层的杀手下法不超过2个
        if bestmove is not None:
            item = (self.depthToRoot, maximizingPlayer)
            if item not in self.killermove:
                self.killermove[item] = []
            self.killermove[item].append(bestmove)
            if len(self.killermove[item]) > 2:
                del self.killermove[item][0]          
        
        # 5. 在祖先列表中删除当前棋盘局面
        self.parentlist.discard(now_board)

        # 返回此层的界限值
        return limit

    def _correctMove(self, move, maximizingPlayer):
        if maximizingPlayer:
            return move
        elif not maximizingPlayer:
            this_move = [_ for _ in move]
            this_move[0] = 'Black'
            this_move[2] = 8-this_move[2]  # chess.x
            this_move[3] = 9-this_move[3]  # chess.y
            this_move[4] = 8-this_move[4]  # x
            this_move[5] = 9-this_move[5]  # y
            return tuple(this_move)
    
    # 检测我方是否被将军
    def InCheck(self, maximizingPlayer):
        player = 'Red' if maximizingPlayer else 'Black'

        # 先找到我方帅的位置
        pos_king = None
        for pos,chess in self.board.board_map.items():
            if (chess.player == player) and (chess.type == 'King'):
                pos_king = pos
                break
        if pos_king is None:
            return False

        for _, chess in self.board.board_map.items():
            # 只检查对面的棋子是否能攻击到我方的帅
            if chess.player == player: continue
            
            if chess.can_move_to(pos_king[0], pos_king[1]):
                return True
        return False
    
    # NOTE 由于此时只需要得到分数，所以这里的alpha-beta和上面的pvs过程有细微区别
    # 静态搜索，只搜索吃子的走法
    def Quiesearch(self, alpha, beta, maximizingPlayer):
        player, limit = ('Red', -self.win) if maximizingPlayer else ('Black', self.win)

        # 1. 检查重复局面
        isCheck = None
        now_board = (player,) + auto_chess._board_key(self.board)
        if now_board in self.parentlist:
            # 长将直接判负
            isCheck = self.InCheck(maximizingPlayer)
            if isCheck:
                score = self.BAN_VALUE-self.depthToRoot if maximizingPlayer else (-self.BAN_VALUE)+self.depthToRoot
                return score
            return self.draw if maximizingPlayer else (-self.draw)
        
        # 2. 检查是否到达最大深度，如果达到则直接返回评估值
        if self.depthToRoot > self.MAX_DEPTH:
            return self.evaluate(player, self.depthToRoot)
        

        # 3. 获得相应的下法
        moves = []
        if isCheck is None: isCheck = self.InCheck(maximizingPlayer)
        # 如果被将军就搜索所有下法
        if isCheck:

            # print("————————————被将军了，当前棋盘情况为—————————————————")
            # self._printBoard()
            if(not maximizingPlayer): self.board.rotate_board()

            # 以红方视角下棋，获得所有的下法
            for _, chess in self.board.board_map.items():
                if chess.player is 'Black': continue
                for x, y in auto_chess._chess_moves(chess):
                    move = ('Red', chess.type, chess.x, chess.y, x, y)
                    score = self.historylist[move] if move in self.historylist else 0
                    move = move + (score,)
                    moves.append(move)

            if(not maximizingPlayer): self.board.rotate_board()
            moves.sort(key=lambda a:a[-1], reverse=True)
        else:
            # 如果没被将军就先评估当前棋面分数
            if maximizingPlayer:
                limit = max(limit, self.evaluate(player, self.depthToRoot))
                alpha = max(limit, alpha)
                if alpha >= beta:
                    return limit
            else:
                limit = min(limit, self.evaluate(player, self.depthToRoot))
                beta = min(limit, beta)
                if beta <= alpha:
                    return limit

            # 获得吃子的走法，并根据Mvv/Lva进行排序，还是以红方的视角下棋
            if(not maximizingPlayer): self.board.rotate_board()
            moves_notGood = []
            for _, chess in self.board.board_map.items():
                if chess.player is 'Black': continue
                for x, y in auto_chess._chess_moves(chess):
                    capChess = self.board.board_map.get((x, y))
                    # 先不考虑吃士，象以及不过河的兵的走法
                    # 当其余吃子走法太少时，可以考虑吃士和象的走法
                    if (capChess is not None):
                        if (capChess.type in ('Guard', 'Bishop')):
                            moves_notGood.append(('Red', chess.type, chess.x, chess.y, x, y))
                        elif ((capChess.type == 'Pawn') and (capChess.y > 4)): continue
                        else:
                            move = ('Red', chess.type, chess.x, chess.y, x, y, 0)
                            moves.append(move)
            if len(moves) <= 1:
                moves = moves_notGood
            # 这个函数一定要在正确的棋盘下使用，它不会修正坐标
            self.sortCapMove(moves, maximizingPlayer)
            if(not maximizingPlayer): self.board.rotate_board()

        # 确定要下棋的时候再把当前局面放入祖父表内
        self.parentlist.add(now_board)
        

        # 4. 对得到的所有走法进行遍历
        for move in moves:

            if maximizingPlayer:
                captureChess = self.changeBoard(move=move, maximizingPlayer=maximizingPlayer)
                # 被将军时，只下一轮，搜索不被将军时最好下法的分数值，如果无论怎么走都会被将军，则直接返回判负的分数
                if isCheck:
                    if not self.InCheck(maximizingPlayer):
                        score = self.evaluate(player, self.depthToRoot)
                        # print("**静态搜索中，已被将军** 当前下法为{}, 分数为{}, 本节点下界为({})".format(self._correctMove(move, not maximizingPlayer), score, limit))
                        limit = max(limit, score)
                        alpha = max(limit, alpha)
                    self.recoverBoard(move, maximizingPlayer, captureChess)
                else:
                    limit = max(limit, self.Quiesearch(alpha, beta, False))
                    alpha = max(limit, alpha)
                    self.recoverBoard(move, maximizingPlayer, captureChess)

                if alpha >= beta:
                    break
            else:
                captureChess = self.changeBoard(move=move, maximizingPlayer=maximizingPlayer)
                # 被将军时
                if isCheck:
                    if not self.InCheck(maximizingPlayer):
                        score = self.evaluate(player, self.depthToRoot)
                        # print("**静态搜索中，已被将军** 当前下法为{}, 分数为{}, 本节点上界为({})".format(self._correctMove(move, not maximizingPlayer), score, limit))
                        limit = min(limit, score)
                        beta = min(limit, beta)
                    self.recoverBoard(move, maximizingPlayer, captureChess)
                else:
                    limit = min(limit, self.Quiesearch(alpha, beta, True))
                    beta = min(limit, beta)
                    self.recoverBoard(move, maximizingPlayer, captureChess)
                if beta <= alpha:
                    break

        self.parentlist.discard(now_board)

        # 如果一个吃子的走法都没走过，那么limit就为初始的上限值
        score = limit
        if limit in (self.win, -self.win):
            # 红方没有吃子的走法
            if maximizingPlayer: score = -(self.win - self.depthToRoot)
            else: score = self.win -  self.depthToRoot
        return score

    # 迭代加深搜索
    def IterSearch(self):
        # 设置初始搜索深度
        self.depth = 1
        # 开始搜索前清空杀手着法表
        self.killermove.clear()
        start_time = time.time()

        begin, move = self.getBeginMove()
        if begin:
            print("\n**********开局***********")
            if (move is not None):
                self.bestmove = move
                print("开局下法为{}".format(self._correctMove(move, False)))
                return 

        print("\n**********开始搜索***********")
        while self.depth <= 20:
            if (time.time()-start_time) > self.limitTime: break
            # 清空祖先列表，重置探索的节点数量和将军深度
            self.parentlist = set()
            self.nodeNum = 0
            self.checkdepth = 0
            self.isroot = True
            
            self.show = True
            tmp = self.pvs(0-self.win, self.win, self.depth, True)
            print("搜索深度为{}时的最好下法{}, 分数为{}".format(self.depth, self._correctMove(self.bestmove, False), tmp))
            self.depth = self.depth + 1
            print("探索了%d个进行了局面评估的节点"%self.nodeNum)
            print(self.checkdepth, self.depthToRoot)

        # 结束前清空历史表或给历史表里存在的着法的值都乘上1/4
        for item in self.historylist:
            self.historylist[item] = self.historylist[item] >> 2
        self._printBoard()

    # 判断当前游戏是否已经开始，并给出相应的下法(模拟开局表)
    def getBeginMove(self):
        move = None
        begin = False
        if not isBegin(self.board):
            return (begin, move)
        begin = True
        # 清空历史表和置换表
        self.replacementlist.clear()
        self.historylist.clear()
        # 获取相应下法
        if len(self.board.board_map) == 32:
            chess = self.board.board_map.get((4,7))
            rand = random.randint(0,1)
            if (chess is not None):
                # 对方飞相
                if (chess.type == 'Bishop'):
                    # 右相飞中
                    if self.board.board_map.get((6,9)) is None:
                        move = ('Red', 'Cannon', 1,2,5,2)  # 左过宫炮
                        return (begin, move)
                    else: # 左相飞中
                        move = ('Red', 'Cannon', 7,2,3,2)  # 右过宫炮
                        return (begin, move)
                # 对方中炮
                if (chess.type == 'Cannon'):
                    # 右炮提中
                    if self.board.board_map.get((7,7)) is None:
                        move = ('Red', 'Knight', 7,0,6,2) if rand==0 else None  # 右马
                        return (begin, move)
                    else: # 左炮提中
                        move = ('Red', 'Knight', 1,0,2,2) if rand==0 else None # 左马
                        return (begin, move)

            # 对方仙人指路(兵七进一)
            chess = self.board.board_map.get((2,5))
            if chess is not None:
                # 炮2平5(中炮)或者跳马二选一
                move = ('Red', 'Cannon', 7,2,4,2) if rand==0 else ('Red', 'Knight', 7,0,6,2)
                return (begin, move)
            else:# 兵三进一
                chess = self.board.board_map.get((6,5))
                if chess is not None:
                    move = ('Red', 'Cannon', 1,2,4,2) if rand==0 else ('Red', 'Knight', 1,0,2,2)
                    return (begin, move)
            
            move = beginMove[random.randint(0,len(beginMove)-1)]
            return (begin, move)
        elif len(self.board.board_map) == 31: # 对面把炮打过来了
            if self.board.board_map[(1,0)].type == 'Cannon':
                move = ('Red', 'Rock', 0,0,1,0)
            else:
                move = ('Red', 'Rock', 8,0,7,0)
            return (begin, move)




def run_app():
	chess_board = chess.ChessBoard()
	javascript.document.body.appendChild(chess_board.elt())
	ControllerPro(chess_board)