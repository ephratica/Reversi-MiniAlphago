from board import Board
import random
import copy
from math import sqrt, log


class Node:
    def __init__(self, bd: Board, parent=None, color=None, action=None):
        self.times = 0  # 已访问次数
        self.reward = 0.0  # 收益值
        self.bd = bd  # 棋盘状态
        self.child = []  # 子节点
        self.parent = parent  # 父节点
        self.color = color  # 该节点颜色
        self.action = action  # 该节点动作

    def if_cannot(self):
        return len(self.child) == len(list(self.bd.get_legal_actions(self.color)))


class AIPlayer:
    """
    AI 玩家
    """

    def __init__(self, color, depth=1200):
        """
        玩家初始化
        :param color: 下棋方，'X' - 黑棋，'O' - 白棋
        """

        self.color = color
        self.C = 2.1  # 超参数C
        self.depth = depth  # 搜索深度

    def if_end(self, bd: Board):
        b_list = list(bd.get_legal_actions('X'))
        w_list = list(bd.get_legal_actions('O'))

        is_over = len(b_list) == 0 and len(w_list) == 0
        return is_over

    def random_extend(self, node: Node):
        board = copy.deepcopy(node.bd)
        color = node.color
        while not self.if_end(board):
            actions = list(board.get_legal_actions(color))
            if len(actions) == 0:
                if color == 'X':
                    color = 'O'
                else:
                    color = 'X'
                continue
            action = random.choice(actions)
            board._move(action, color)
            if color == 'X':
                color = 'O'
            else:
                color = 'X'
        winner, score = board.get_winner()
        if winner == 2:
            reward = 0
        elif winner == 0:
            reward = 30 + score
        else:
            reward = -(30 + score)

        if self.color == 'O':
            reward *= -1
        return reward

    def get_ucb(self, node: Node):
        mx_score = -float('inf')
        best_son = []
        for son in node.child:
            if son.times == 0:
                best_son = son
                break
            x = float(son.reward) / float(son.times)
            y = sqrt(2.0*log(float(node.times))/float(son.times))
            score = x + self.C*y
            if score == mx_score:
                best_son.append(son)
            if score > mx_score:
                best_son = [son]
                mx_score = score
        if len(best_son) == 0:
            return None
        return random.choice(best_son)

    def expand(self, node: Node):
        actions = set(list(node.bd.get_legal_actions(node.color)))
        if len(actions) == 0:
            return node.parent
        son_actions = set([i.action for i in node.child])
        actions = list(actions - son_actions)
        action = random.choice(actions)
        new_board = copy.deepcopy(node.bd)
        new_board._move(action, node.color)
        if node.color == 'X':
            new_color = 'O'
        else:
            new_color = 'X'
        new_node = Node(bd=new_board, parent=node, color=new_color, action=action)
        node.child.append(new_node)
        return node.child[-1]

    def back(self, node: Node, reward):
        while node.parent is not None:
            node.times += 1
            if node.parent.color == self.color:
                node.reward += reward
            else:
                node.reward -= reward
            node = node.parent
        return 0

    def select_policy(self, node: Node):
        while not self.if_end(node.bd):
            if not node.if_cannot():
                return self.expand(node)
            else:
                if self.get_ucb(node) is None:
                    break
                else:
                    node = self.get_ucb(node)
        return node

    def UCTSearch(self, now: Node, times):
        for t in range(times):
            v = self.select_policy(now)
            reward = self.random_extend(v)
            self.back(v, reward)
            best_child = self.get_ucb(now)
        return best_child.action

    def get_move(self, board):
        """
        根据当前棋盘状态获取最佳落子位置
        :param board: 棋盘
        :return: action 最佳落子位置, e.g. 'A1'
        """
        if self.color == 'X':
            player_name = '黑棋'
        else:
            player_name = '白棋'
        print("请等一会，对方 {}-{} 正在思考中...".format(player_name, self.color))

        # -----------------请实现你的算法代码--------------------------------------
        bd = copy.deepcopy(board)
        root = Node(bd=bd, color=self.color)
        root.times = 1
        action = self.UCTSearch(root, self.depth)
        # ------------------------------------------------------------------------

        return action