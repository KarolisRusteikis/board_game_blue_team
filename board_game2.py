import tkinter as tk
from tkinter import simpledialog, messagebox
import random

class BoardGame:
    def __init__(self, num_players, player_names):
        self.num_players = num_players
        self.players = []
        self.current_player_index = 0
        self.current_step = 0
        self.special_events = {
            42: ("Teleport", 55),
            55: ("Teleport", 42),
            69: ("Teleport", 33),
            33: ("Teleport", 69),
            25: "RollOneMoreTime",
            75: "RollOneMoreTime",
            50: "SkipNextTurn",
            90: "SkipNextTurn",
            95: "SkipNextTurn",
            99: "SkipNextTurn"
        }

        self.create_board(player_names)

    def create_board(self, player_names):
        self.board_size = 10
        self.board = [[0] * self.board_size for _ in range(self.board_size)]

        tile_count = 1
        for i in range(self.board_size // 2):
            for j in range(i, self.board_size - i):
                self.board[i][j] = tile_count
                tile_count += 1

            for j in range(i + 1, self.board_size - i):
                self.board[j][self.board_size - i - 1] = tile_count
                tile_count += 1

            for j in range(self.board_size - i - 2, i - 1, -1):
                self.board[self.board_size - i - 1][j] = tile_count
                tile_count += 1

            for j in range(self.board_size - i - 2, i, -1):
                self.board[j][i] = tile_count
                tile_count += 1

        self.special_icons = {
            42: ">>",
            55: "O",
            69: "<<",
            33: "O",
            25: "G",
            75: "G",
            50: "|",
            90: "|",
            95: "|",
            99: "|"
        }

        self.players = [{"name": name, "icon": name[0].upper(), "position": 0} for name in player_names]

    def roll_dice(self):
        return random.randint(1, 6) + random.randint(1, 6)

    def move_player(self, steps):
        self.players[self.current_player_index]["position"] += steps
        self.current_step = steps

        if self.players[self.current_player_index]["position"] in self.special_events:
            event = self.special_events[self.players[self.current_player_index]["position"]]
            if event == "RollOneMoreTime":
                return "RollOneMoreTime"
            elif event == "SkipNextTurn":
                return "SkipNextTurn"
            else:
                destination = event[1]
                self.players[self.current_player_index]["position"] = destination
                return f"Teleported to {destination}"

        return f"Moved {steps} steps"

    def switch_player(self):
        self.current_player_index = (self.current_player_index + 1) % self.num_players

    def check_winner(self):
        return any(player["position"] >= self.board_size ** 2 for player in self.players)

    def update_board(self, canvas):
        canvas.delete("all")
        cell_size = 80  # Double the size of the tiles
        for i in range(self.board_size):
            for j in range(self.board_size):
                x = j * cell_size
                y = i * cell_size
                tile_number = self.board[i][j]

                # Draw coiled snake-like pathway
                if (
                    (i == 0 or i == self.board_size - 1)
                    or (j == 0 and i <= self.board_size // 2)
                    or (j == self.board_size - 1 and i >= self.board_size // 2)
                ):
                    canvas.create_rectangle(
                        x, y, x + cell_size, y + cell_size, fill="white", outline="black"
                    )
                elif (
                    (j == 0 or j == self.board_size - 1)
                    or (i == self.board_size // 2 - 1 and j >= self.board_size // 2)
                    or (i == self.board_size // 2 and j <= self.board_size // 2)
                ):
                    canvas.create_rectangle(
                        x, y, x + cell_size, y + cell_size, fill="white", outline="black"
                    )

                # Display player icons, tile numbers, and special icons
                for player in self.players:
                    if player["position"] == tile_number:
                        canvas.create_text(
                            x + cell_size // 2, y + cell_size // 2, text=player["icon"], font=("Arial", 20, "bold")
                        )
                canvas.create_text(x + cell_size // 2, y + cell_size // 2, text=tile_number, font=("Arial", 12))

                if tile_number in self.special_icons:
                    icon = self.special_icons[tile_number]
                    canvas.create_text(x + cell_size // 2, y + cell_size // 2, text=icon, font=("Arial", 12))


class PlayerNameInputGUI:
    def __init__(self, root, num_players):
        self.root = root
        self.num_players = num_players
        self.player_names = []
        self.current_player_index = 0
        self.setup_gui()

    def setup_gui(self):
        self.root.title("Player Name Input")

        self.label = tk.Label(self.root, text=f"Enter name for Player {self.current_player_index + 1}:")
        self.label.pack()

        self.entry = tk.Entry(self.root)
        self.entry.pack()

        self.button = tk.Button(self.root, text="Submit", command=self.get_player_name)
        self.button.pack()

    def get_player_name(self):
        name = self.entry.get().strip()
        if name:
            self.player_names.append(name)
            self.current_player_index += 1

            if self.current_player_index < self.num_players:
                self.label.config(text=f"Enter name for Player {self.current_player_index + 1}:")
                self.entry.delete(0, tk.END)
            else:
                self.root.destroy()
        else:
            messagebox.showwarning("Invalid Input", "Please enter a valid name.")


class MainGameGUI:
    def __init__(self, root, board_game):
        self.root = root
        self.board_game = board_game

        self.setup_gui()

    def setup_gui(self):
        self.root.title("Dice Board Game")

        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack()

        self.roll_button = tk.Button(self.root, text="Roll Dice", command=self.roll_dice)
        self.roll_button.pack()

        self.board_canvas = tk.Canvas(self.root, width=800, height=800, bg="white")  # Double the canvas size
        self.board_canvas.pack()

        self.update_board()
        self.update_status()

    def roll_dice(self):
        steps = self.board_game.roll_dice()
        event_result = self.board_game.move_player(steps)

        self.update_board()
        self.update_status()

        if self.board_game.check_winner():
            winner_name = self.board_game.players[self.board_game.current_player_index]["name"]
            messagebox.showinfo("Game Over", f"{winner_name} wins!")
            self.root.destroy()
        else:
            if event_result == "RollOneMoreTime":
                self.roll_button.config(state=tk.NORMAL)
            elif event_result == "SkipNextTurn":
                self.board_game.switch_player()
                self.update_status()
                self.roll_button.config(state=tk.NORMAL)
            else:
                self.board_game.switch_player()
                self.update_status()
                self.roll_button.config(state=tk.NORMAL)

    def update_board(self):
        self.board_game.update_board(self.board_canvas)

    def update_status(self):
        player = self.board_game.players[self.board_game.current_player_index]
        status_text = (
            f"{player['name']}'s turn\n"
            f"Dice Rolled: {self.board_game.current_step}\n"
            f"Moved to step {player['position']}\n"
        )
        self.status_label.config(text=status_text)


if __name__ == "__main__":
    root_input = tk.Tk()
    num_players = simpledialog.askinteger("Number of Players", "Enter the number of players (2-4):", minvalue=2, maxvalue=4)
    if num_players:
        player_name_input_gui = PlayerNameInputGUI(root_input, num_players)
        root_input.mainloop()

        player_names = player_name_input_gui.player_names

        if player_names:
            root_game = tk.Tk()
            board_game = BoardGame(num_players, player_names)
            main_game_gui = MainGameGUI(root_game, board_game)
            root_game.mainloop()
