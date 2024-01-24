import PySimpleGUI as sg
import random

def get_player_names():
    layout = [[sg.Text("Player 1 name:"), sg.InputText()],
              [sg.Text("Player 2 name:"), sg.InputText()],
              [sg.Button('Ok')]]
    window = sg.Window("Enter Player Names", layout)
    event, values = window.read()
    window.close()
    return values[0], values[1]

def roll_dice():
    return random.randint(1, 6), random.randint(1, 6)

def calculate_position(pos):
    row, col = divmod(pos, 10)

    if row % 2 == 1:
        col = 9 - col

    return row, col

def update_board(window, player_positions, player_names, dice_roll_info, event_info):
    board = [['   ' for _ in range(10)] for _ in range(10)]
    special_steps = [42, 69]
    special_steps_result = [33, 66]

    for i, pos in enumerate(player_positions):
        row, col = calculate_position(pos)
        board[row][col] = f'{player_names[i][0]}'

    for r in range(10):
        for c in range(10):
            pos = r * 10 + c if r % 2 == 0 else r * 10 + (9 - c)
            if pos in skip_turn_steps:
                color = 'yellow'
            elif pos in extra_turn_steps:
                color = 'red'
            elif pos in special_steps:
                color = 'pink'
            elif pos in special_steps_result:
                color = 'black'
            else:
                color = 'white'
            cell_value = f'{pos + 1}\n{board[r][c]}'
            window[f'-CELL-{r}-{c}-'].update(cell_value, button_color=('black', color))

    window['-EVENT-INFO-'].update(event_info)

    window['-DICE-INFO-'].update(f'{player_names[current_player]} rolled the dice:\n'
                                f'Dice Roll: {dice_roll_info["dice1"]} + {dice_roll_info["dice2"]}\n'
                                f'Moved from {dice_roll_info["start_pos"] + 1} to {dice_roll_info["end_pos"] + 1}')


def main():
    player_names = get_player_names()

    global player_positions, current_player, window

    sg.theme('BlueMono')

    layout = [[sg.Button('', size=(4, 2), key=f'-CELL-{r}-{c}-') for c in range(10)] for r in range(10)]
    layout.append([sg.Text('Dice Roll:', font=('Helvetica', 14)), sg.Text('', size=(5, 1), key='-DICE-ROLL-')])
    layout.append([sg.Text('', size=(50, 3), key='-DICE-INFO-')])
    layout.append([sg.Text('', size=(50, 1), key='-EVENT-INFO-')])
    layout.append([sg.Button('Roll Dice'), sg.Button('Exit')])

    window = sg.Window('Dice Board Game', layout)

    player_positions = [0, 0]
    current_player = 0
    extra_rolls = [0, 0]
    skip_turn = [False, False]

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        if event == 'Roll Dice':
            event_info = ''

            total_dice = 0
            num_rolls = 1 + extra_rolls[current_player]
            extra_rolls[current_player] = 0

            for _ in range(num_rolls):
                dice1, dice2 = roll_dice()
                total_dice += dice1 + dice2

            start_pos = player_positions[current_player]
            player_positions[current_player] += total_dice
            end_pos = player_positions[current_player]

            if end_pos == 42:
                player_positions[current_player] = 66
                event_info = f'{player_names[current_player]} teleported to 66!'
            elif end_pos == 69:
                player_positions[current_player] = 33
                event_info = f'{player_names[current_player]} teleported to 33!'
            elif end_pos in skip_turn_steps:
                skip_turn[current_player] = True
                event_info = f'{player_names[current_player]} skipped the turn!'
            elif end_pos in extra_turn_steps:
                extra_rolls[current_player] = 1
                event_info = f'{player_names[current_player]} got an extra turn!\n'

            player_positions[current_player] = min(player_positions[current_player], 99)

            update_board(window, player_positions, player_names, {
                'dice1': dice1,
                'dice2': dice2,
                'start_pos': start_pos,
                'end_pos': end_pos
            }, event_info)

            if player_positions[current_player] >= 99:
                sg.popup(f'{player_names[current_player]} wins!')
                window.close()
                return

            # Switch to the next player after handling the event
            current_player = 1 - current_player

            # Reset skip_turn flag for the next turn
            skip_turn[0] = False
            skip_turn[1] = False

    window.close()
    
skip_turn_steps = [15, 35, 55, 75, 95]
extra_turn_steps = [20, 40, 60, 80]

if __name__ == '__main__':
    main()
