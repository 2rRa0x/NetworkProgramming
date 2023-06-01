import tkinter as tk
import tkinter.messagebox as messagebox
import socket
import threading

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 4445
BUFFER_SIZE = 1024

WIDTH = 500
HEIGHT = 500
BOARD_ROWS = 6
BOARD_COLS = 7
SQUARE_SIZE = HEIGHT // (BOARD_ROWS + 1)

'''
board = [[0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0]]

'''

# Initialize the game board
board = [[0] * BOARD_COLS for _ in range(BOARD_ROWS)]

# Create the main window
root = tk.Tk()
root.title("Connect 4")

# Create a canvas widget to draw the game board
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
canvas.pack()

# Initialize player name and create a client socket to connect to the server
player_name = ""

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))

def draw_board():
    canvas.delete("all")
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            x = col * SQUARE_SIZE
            y = (row + 1) * SQUARE_SIZE

            canvas.create_rectangle(x, y, x + SQUARE_SIZE, y + SQUARE_SIZE, outline="blue", fill="white")

    # Draw the player pieces on the board
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            player = board[row][col]
            if player in [1, 2]:
                x = col * SQUARE_SIZE + SQUARE_SIZE // 2
                y = row * SQUARE_SIZE + SQUARE_SIZE + SQUARE_SIZE // 2
                color = "red" if player == 1 else "yellow"
                canvas.create_oval(x - SQUARE_SIZE // 2, y - SQUARE_SIZE // 2, x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2, fill=color)

def handle_click(event):
    col = event.x // SQUARE_SIZE
    if is_valid_move(col):
        drop_piece(col, 1)
        draw_board()
        client_socket.send(str(col).encode())
        if check_winner(1):
            show_winner_message(1)
            reset_board()

def is_valid_move(col):
    return board[0][col] == 0

def drop_piece(col, player):
    for row in range(BOARD_ROWS - 1, -1, -1):
        if board[row][col] == 0:
            board[row][col] = player
            break

def check_winner(player):
    # Check rows
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS - 3):
            if board[row][col] == board[row][col + 1] == board[row][col + 2] == board[row][col + 3] == player:
                return True

    # Check columns
    for col in range(BOARD_COLS):
        for row in range(BOARD_ROWS - 3):
            if board[row][col] == board[row + 1][col] == board[row + 2][col] == board[row + 3][col] == player:
                return True

    # Check diagonals (down-right)
    for row in range(BOARD_ROWS - 3):
        for col in range(BOARD_COLS - 3):
            if board[row][col] == board[row + 1][col + 1] == board[row + 2][col + 2] == board[row + 3][col + 3] == player:
                return True

    # Check diagonals (up-right)
    for row in range(3, BOARD_ROWS):
        for col in range(BOARD_COLS - 3):
            if board[row][col] == board[row - 1][col + 1] == board[row - 2][col + 2] == board[row - 3][col + 3] == player:
                return True

    return False

def show_winner_message(player):
    winner = "Red" if player == 1 else "Yellow"
    message = f"{winner} player wins!\n\nDo you want to continue with a new game?"
    choice = messagebox.askquestion("Game Over", message)
    if choice == 'yes':
        reset_board()
    else:
        root.quit()

def reset_board():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            board[row][col] = 0
    draw_board()

def set_player_name():
    global player_name
    player_name = entry_name.get()

def exit_game():
    choice = messagebox.askquestion("Exit Game", "Are you sure you want to exit the game?")
    if choice == 'yes':
        client_socket.close()
        root.quit()

def receive_data():
    while True:
        try:
            data = client_socket.recv(BUFFER_SIZE).decode()
            if data:
                col = int(data)
                drop_piece(col, 2)
                draw_board()
                if check_winner(2):
                    show_winner_message(2)
                    reset_board()
        except ConnectionAbortedError:
            break

def start_game():
    root.geometry("600x600")  # Set window size
    threading.Thread(target=receive_data).start()

    # Create frames
    name_frame = tk.Frame(root)
    board_frame = tk.Frame(root)

    # Pack frames
    name_frame.pack()
    board_frame.pack()

    # Create and pack GUI elements in name_frame
    global label_name
    label_name = tk.Label(name_frame, text="Enter Your Name:")
    label_name.pack()

    global entry_name
    entry_name = tk.Entry(name_frame)
    entry_name.pack()

    # Function to handle the "Set Name" button click
    def set_name_and_start_board():
        set_player_name()
        label_name.config(text=f"Player Name: {player_name}")  # Update the player name label
        button_set_name.pack_forget()  # Remove the "Set Name" button
        entry_name.pack_forget()  # Remove the entry name widget
        label_name.pack_forget()  # Remove the label name widget
        create_board()  # Display the board and exit button

    button_set_name = tk.Button(name_frame, text="Set Name", command=set_name_and_start_board)
    button_set_name.pack()

     # Function to create and pack board-related GUI elements
    def create_board():
        button_exit = tk.Button(board_frame, text="Exit", command=exit_game)
        button_exit.pack()

        canvas = tk.Canvas(board_frame, width=WIDTH, height=HEIGHT)
        canvas.pack()

        # Bind event and draw initial board
        root.bind("<Button-1>", handle_click)
        draw_board()



    root.mainloop()

if __name__ == '__main__':
    start_game()
