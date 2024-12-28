from math import inf, sqrt, log, floor
from random import randint
from copy import deepcopy
import time

boards = 0

# tree node
class Node:
    def __init__(self, board, player_id, row, col):
        self.wins = 0.0
        self.games = 0.0
        self.row = row
        self.col = col
        self.board = board
        self.player_id = player_id
        self.children = []

# Monte Carlo Tree Search algorithm
def mcts(node, expanding=False):
    global boards
    boards += 1
    #print(boards)

    node.games += 1
    from game import TicTacToeGame as game

    status = game.check_status(global_game, node.board)
    if status != "ongoing":
        if status == "X" or status == "O":
            node.wins += 1
        return

    row_sel = -1
    col_sel = -1
    if node.player_id == "X":
        next_player = "O" 
    else:
        next_player = "X"
    next_board = deepcopy(node.board)
    if len(node.children) == 25:
        max_upp_conf_bound = -inf # maximum upper confidence bound
        for child in node.children:
            upper_conf_bound = child.wins / child.games + sqrt(log(node.games) / child.games)
            if upper_conf_bound > max_upp_conf_bound:
                max_upp_conf_bound = upper_conf_bound
                row_sel = child.row
                col_sel = child.col

    elif not expanding:
        for row in range(5):
            for col in range(5):
                if node.board[row][col].label != "":
                    continue
                next_board = deepcopy(node.board)
                next_board[row][col] = next_board[row][col]._replace(label = node.player_id)
                next_node = Node(next_board, next_player, row, col)
                is_child = False
                for child in node.children:
                    if child.board == next_board:
                        next_node = child
                        is_child = True
                if not is_child:
                    node.children.append(next_node)
                mcts(next_node, True)
    else:
        move = randint(0, 24)
        col = move % 5
        row = floor(move / 5)
        while node.board[row][col].label != "":
            move = randint(0, 24)
            col = move % 5
            row = floor(move / 5)
        next_board[row][col] = next_board[row][col]._replace(label = node.player_id)
        next_node = Node(next_board, next_player, row, col)
        is_child = False
        for child in node.children:
            if child.board == next_board:
                next_node = child
                is_child = True
        if not is_child:
            node.children.append(next_node)
        mcts(next_node, expanding)

    node.wins = 0
    node.games = 0
    if node.children:
        for child in node.children:
            node.wins += child.games - child.wins
            node.games += child.games

# checks if there is any way for anyone to still win
# this may take a while
def game_sanity_check(board, turn):
    for i in range(5):
        for j in range(5):
            if board[i][j].label == "":
                board[i][j].label = turn
                status = game.check_status(global_game, board)
                if status == "X" or status == "O":
                    return True
                else:
                    ret = game_sanity_check(board, "O" if turn == "X" else "X")
                    if ret:
                        return True
                board[i][j].label = ""
    return False
    

def ai_ask_tie(current_moves, current_player):
    cnt = 0;
    for row in range(5):
        for col in range(5):
            if board[row][col].label != "":
                cnt = cnt + 1
    if cnt <= 13:
        return False
    board = deepcopy(current_moves)
    ret = game_sanity_check(board, current_player)
    return not ret


def ai_ask_move(current_game, current_moves, player, turn_length):
    global boards
    boards = 0

    global global_game
    global_game = current_game

    board = deepcopy(current_moves)

    row = -1
    col = -1
    root = Node(board, player, row, col)
    start = time.time()
    while time.time() < start + turn_length:
        mcts(root)

    best_score = -inf
    for child in root.children:
        if child.wins / child.games > best_score:
            row = child.row
            col = child.col
            best_score = child.wins / child.games

    if row == -1 or col == -1:
        print("aici")
        move = randint(0, 24)
        col = move % 5
        row = floor(move / 5)
        while board[row][col].label != "":
            move = randint(0, 24)
            col = move % 5
            row = floor(move / 5)

    print(board)
    print(boards)
    return (row, col, player)
