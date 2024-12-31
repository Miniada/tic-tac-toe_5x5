import tkinter as tk
from itertools import cycle
from tkinter import font
from tkinter import messagebox
import threading
from typing import NamedTuple
from random import randint

class Player(NamedTuple):
    label: str
    color: str

class Move(NamedTuple):
    row: int
    col: int
    label: str = ""

BOARD_SIZE = 5
COMBO_SIZE = 4
DEFAULT_PLAYERS = (
    Player(label="X", color="blue"),
    Player(label="O", color="green"),
)

class TicTacToeGame:
    def __init__(self, socket, players=DEFAULT_PLAYERS, board_size=BOARD_SIZE):
        self._players = cycle(players)
        self.board_size = board_size
        self.combo_size = COMBO_SIZE
        self.current_player = next(self._players)
        self.winner_combo = []
        self._current_moves = []
        self._has_winner = False
        self._winning_combos = []
        self._setup_board()
        self._socket = socket
        
    
    def notify(self, move):
        self._socket.send(f"{move[0]}, {move[1]}".encode())

    def _setup_board(self):
        self._current_moves = [
            [Move(row, col) for col in range(self.board_size)]
            for row in range(self.board_size)
        ]
        self._winning_combos = self._get_winning_combos()

    def _get_winning_combos(self):
        rows = [
            [[(move.row, move.col) for move in short_row]
            for short_row in [row[k:k+self.combo_size] for k in range(self.board_size - self.combo_size + 1)]]
            for row in self._current_moves
        ]
        rows = [val for row in rows for val in row]
        columns = [
            [[(move.col, move.row) for move in short_row]
            for short_row in [row[k:k+self.combo_size] for k in range(self.board_size - self.combo_size + 1)]]
            for row in self._current_moves
        ]
        columns = [val for column in columns for val in column]
        first_diagonal = [[(i, i) for i in range(j, j+self.combo_size)] for j in range(self.board_size - self.combo_size + 1)]
        below_first_diag = [(i+1, i) for i in range(self.combo_size)]
        above_first_diag = [(i, i+1) for i in range(self.combo_size)]
        second_diagonal = [[(i, self.board_size - 1 - i) for i in range(j, j+self.combo_size)] for j in range(self.board_size - self.combo_size + 1)]
        below_second_diag = [(i+1, self.board_size - 1 - i) for i in range(self.combo_size)]
        above_second_diag = [(i, self.board_size - i - 2) for i in range(self.combo_size)]
        return rows + columns + first_diagonal + second_diagonal + [below_first_diag, above_first_diag, below_second_diag, above_second_diag]

    def is_valid_move(self, move):
        row, col = move.row, move.col
        move_was_not_played = self._current_moves[row][col].label == ""
        no_winner = not self._has_winner
        return no_winner and move_was_not_played

    def check_status(self, current_moves):
        for combo in self._winning_combos:
            results = set(
                current_moves[n][m].label
                for n, m in combo
            )
            is_win = (len(results) == 1) and ("" not in results)
            if is_win:
                pos = combo.__getitem__(0)
                row = pos[0]
                col = pos[1]
                if current_moves[row][col].label == "X":
                    return "X"
                else:
                    return "O"
        played_moves = (
            move.label for row in current_moves for move in row
        )
        if all(played_moves):
            return "tie"
        return "ongoing"

    def process_move(self, move):
        row, col = move.row, move.col
        self._current_moves[row][col] = move
        for combo in self._winning_combos:
            results = set(
                self._current_moves[n][m].label
                for n, m in combo
            )
            is_win = (len(results) == 1) and ("" not in results)
            if is_win:
                self._has_winner = True
                self.winner_combo = combo
                break

    def has_winner(self):
        return self._has_winner

    def is_tied(self):
        no_winner = not self._has_winner
        played_moves = (
            move.label for row in self._current_moves for move in row
        )
        return no_winner and all(played_moves)
    
    def toggle_player(self):
        self.current_player = next(self._players)

    def reset_game(self):
        for row, row_content in enumerate(self._current_moves):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row, col)
        self._has_winner = False
        self.winner_combo = []
        self._players = cycle(DEFAULT_PLAYERS)
        self.current_player = next(self._players)

    # checks if there's still a point in playing the game
    def game_sanity_check(self):
        for combo in self._winning_combos:
            results = set(
                self._current_moves[n][m].label
                for n, m in combo
            )
            is_not_available = ("X" in results) and ("O" in results)
            if not is_not_available:
                return True
        return False


class TicTacToeBoard(tk.Tk):
    def __init__(self, game, socket, mult_turn, ai_player):
        super().__init__()
        self.title("Tic-Tac-Toe Game")
        self._cells = {}
        self._game = game
        self._socket = socket
        self._create_menu()
        self._create_board_display()
        self._create_board_grid()
        self.turn = 0
        self._mult_turn = mult_turn
        if (socket != None):
            threading.Thread(target = self.receive_update, daemon = True).start()
        self.ai_player = ai_player


    def _create_board_display(self):
        display_frame = tk.Frame(master=self)
        display_frame.pack(fill=tk.X)
        self.display = tk.Label(
            master=display_frame,
            text="Ready?",
            font=font.Font(size=28, weight="bold"),
        )
        self.display.pack()

    def _create_board_grid(self):
        grid_frame = tk.Frame(master=self)
        grid_frame.pack()

        for row in range(self._game.board_size):
            self.rowconfigure(row, weight=1, minsize=50)
            self.columnconfigure(row, weight=1, minsize=75)

            for col in range(self._game.board_size):
                button = tk.Button(
                    master=grid_frame,
                    text="",
                    font=font.Font(size=36, weight="bold"),
                    fg="black",
                    width=3,
                    height=2,
                    highlightbackground="lightblue",
                )
                self._cells[button] = (row, col)
                if (self._socket == None):
                    button.bind("<ButtonPress-1>", self.play)
                    button.grid(
                        row=row,
                        column=col,
                        padx=5,
                        pady=5,
                        sticky="nsew"
                    )
                else:
                    button.bind("<ButtonPress-1>", self.mult_play)
                    button.grid(
                        row=row,
                        column=col,
                        padx=5,
                        pady=5,
                        sticky="nsew"
                    )

    def _update_button(self, clicked_btn):
        clicked_btn.config(text=self._game.current_player.label)
        clicked_btn.config(fg=self._game.current_player.color)

    def _highlight_cells(self):
        for button, coordinates in self._cells.items():
            if coordinates in self._game.winner_combo:
                button.config(highlightbackground="red")

    def _update_display(self, msg, color="black"):
        self.display["text"] = msg
        self.display["fg"] = color
        self.update()
    

    def receive_update(self):
        while True:
            message = self._socket.recv(10).decode().strip() # get opponent's move
            if (message == None or message == ""):
                continue
            print(message)
            if (message == "tie?"):
                ask = tk.messagebox.askyesno("", "Tie?")
                if ask:
                    self._update_display(msg="Tied game!", color="red")
                    self._socket.send("yes!".encode())
                    self.reset_board()
                continue
            if (message == "yes!"):
                self._update_display(msg="Tied game!", color="red")
                self.reset_board()
                continue


            if (message == "again?"):
                ask = tk.messagebox.askyesno("", "Again?")
                if ask:
                    self._socket.send("again!".encode())
                    self.reset_board()
                continue
            if (message == "again!"):
                self.reset_board()
                continue
            parts = message.split(", ")
            row, col = map(int, parts)
            keys = [k for k, (v, l) in self._cells.items() if (v, l) == (row, col)]
            if (keys == None):
                continue
            self._update_button(keys[0])
            move = Move(row, col, self._game.current_player.label)
            self._game.process_move(move)

            if self._game.is_tied():
                self._update_display(msg="Tied game!", color="red")
            elif self._game.has_winner():
                self._highlight_cells()
                msg = f'Player "{self._game.current_player.label}" won!'
                color = self._game.current_player.color
                self._update_display(msg, color)

            else:
                self._game.toggle_player()
                msg = f"{self._game.current_player.label}'s turn"
                self._update_display(msg)  
            self.turn  = (self.turn + 1) % 2

    def mult_play(self, event):
        if (self.turn != self._mult_turn):
            return
        self.play(event)

    def update_display_if_win(self):
        if self._game.is_tied():
            self._update_display(msg="Tied game!", color="red")
            return True
        elif self._game.has_winner():
            self._highlight_cells()
            msg = f'Player "{self._game.current_player.label}" won!'
            color = self._game.current_player.color
            self._update_display(msg, color)
            return True
        return False

    def ai_play(self):
        from ai import ai_ask_move
        move = ai_ask_move(self._game, self._game._current_moves, self.ai_player, 15)
        keys = [k for k, (v, l) in self._cells.items() if (v, l) == (move[0], move[1])]
        self._update_button(keys[0])
        self._game._current_moves[move[0]][move[1]] = self._game._current_moves[move[0]][move[1]]._replace(label = self.ai_player)
        self._game.process_move(Move(move[0], move[1], move[2]))
        ended = self.update_display_if_win()

        if not ended:
            self._game.toggle_player()
            msg = f"Your turn!"
            self._update_display(msg);
            self.turn = (self.turn + 1) % 2

    def play(self, event): 
        if self.ai_player != "" and self._game.current_player.label == self.ai_player:
            return
        else:
            clicked_btn = event.widget
            row, col = self._cells[clicked_btn]
            move = Move(row, col, self._game.current_player.label)
            if self._game.is_valid_move(move):
                if (self._socket != None):
                    self._game.notify(move)
                self._update_button(clicked_btn)
                self._game.process_move(move)
                ended = self.update_display_if_win()

                self.turn = (self.turn + 1) % 2
                if not ended:
                    self._game.toggle_player()
                    if self.ai_player == "":
                        clicked_btn.configure(relief='raised')
                        msg = f"{self._game.current_player.label}'s turn"
                        self._update_display(msg)
                    else:
                        clicked_btn.configure(relief='raised')
                        msg = f"Waiting for AI..."
                        self._update_display(msg)
                        self.ai_play()
                        return "break"
            

    def _create_menu(self):
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)
        menu_bar.add_command(label="Exit", command=quit)
        menu_bar.add_separator()
        if (self._socket == None):
            menu_bar.add_command(
                label="Play Again",
                command=self.reset_board
            )
        else:
            menu_bar.add_command(
                label="Play Again",
                command=self.play_again
            )
        menu_bar.add_separator()
        menu_bar.add_command(label="Tie?", command=self.ask_tie)
        menu_bar.add_separator()
        menu_bar.add_command(label="Play against AI", command=self.start_ai_play)

    def reset_board(self):
        self.turn = 0
        self._game.reset_game()
        self._update_display(msg="Ready?")
        for button in self._cells.keys():
            button.config(highlightbackground="lightblue")
            button.config(text="")
            button.config(fg="black")
        

    def play_again(self):
        self._socket.send("again?".encode())

    def send_tie_message(self):
        if (self._socket == None):
            return
        self._socket.send("tie?".encode())

    def set_ai_play_o(self):
        self.ai_player = "O"

    def set_ai_play_x(self):
        self.ai_player = "X"

    def start_ai_play(self):
        self.reset_board()
        player = randint(0, 1)
        if player == 0:
            msg = f"Your turn!"
            self._update_display(msg)
            self.set_ai_play_o()
            return
        else:
            msg = f"Waiting for AI..."
            self._update_display(msg)
            self.set_ai_play_x()
            self.ai_play()

    def ask_tie(self):
        if self._game.has_winner() != True: # locked the button when game has a winner
            if self.ai_player != "":
                playable = self._game.game_sanity_check()
                if playable:
                    tk.messagebox.showinfo("Cannot tie game", "This game is not a tie.")
                else:
                    tk.messagebox.showinfo("Tie", "Tied game!") 
                    self.reset_board()
            else:
                self.send_tie_message()
                if (self._socket == None):
                    ask = tk.messagebox.askyesno("", "Tie?")
                    if ask:
                        tk.messagebox.showinfo("Tie", "Tied game!") 
                        self.reset_board() # make tie reset the game
        else:
            msgbox = tk.messagebox.showinfo("Game ended already", "The match has already ended")

    


def main():
    game = TicTacToeGame(None)
    board = TicTacToeBoard(game, None, 0, "")
    board.mainloop()

if __name__ == "__main__":
    main()