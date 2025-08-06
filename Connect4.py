import numpy as np
import pygame
import sys
import math
import random
from datetime import datetime
import pytz

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER_PIECE = 2
AI_PIECE = 1


def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board


def drop_piece(board, row, col, piece, remaining_time=15, animate=False):
    if animate:
        pos_y = 0
        speed = 10
        color = RED if piece == 1 else YELLOW

        target_y = height - int(row * SQUARESIZE + SQUARESIZE/2)

        while pos_y < target_y:
            pos_y += speed
            if pos_y > target_y:
                pos_y = target_y

            draw_board(board, remaining_time, False, "00:00:00") # Redraw board
            pygame.draw.circle(screen, color, (int(col*SQUARESIZE+SQUARESIZE/2), int(pos_y)), RADIUS)
            pygame.display.update()
            pygame.time.Clock().tick(60)

    board[row][col] = piece


def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0


def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r


def print_board(board):
    print(np.flip(board, 0))


def winning_move(board, piece):
    # Check horizontal location for win
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][
                c + 3] == piece:
                return True


    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][
                c] == piece:
                return True

    # Check for positive sloped diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][
                c + 3] == piece:
                return True

    # Check for negative sloped diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][
                c + 3] == piece:
                return True

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(0) == 1:
        score -= 4

    return score

def score_position(board, piece):
    score = 0

    ## Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    ## Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c+4]
            score += evaluate_window(window, piece)

    ## Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+4]
            score += evaluate_window(window, piece)

    ## Score posiive sloped diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    ## Score negative sloped diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else: # Game is over, no more valid moves
                return (None, 0)
        else: # Depth is zero
            return (None, score_position(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE, 0, animate=False)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else: # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE, 0, animate=False)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def pick_best_move(board):
    return minimax(board, 5, -math.inf, math.inf, True)[0]

def reset_game():
    global board, game_over, turn, turn_start_time
    board = create_board()
    game_over = False
    turn = 1
    turn_start_time = pygame.time.get_ticks()

def draw_board(board, remaining_time, game_over, toronto_time):
    screen.fill(BLACK)

    # Draw the title
    title_font = pygame.font.SysFont("monospace", 80, bold=True)
    title_label = title_font.render("CONNECT4", 1, YELLOW)
    title_rect = title_label.get_rect(center=(width/2, SQUARESIZE/2 - 20))
    screen.blit(title_label, title_rect)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)

    if game_over:
        # Draw the restart button
        RESTART_BUTTON_COLOR = (0, 255, 0)
        RESTART_BUTTON_BORDER_COLOR = (0, 100, 0)
        RESTART_BUTTON_X = width/2 - 70
        RESTART_BUTTON_Y = height/2 + 50
        RESTART_BUTTON_WIDTH = 140
        RESTART_BUTTON_HEIGHT = 40

        pygame.draw.rect(screen, RESTART_BUTTON_BORDER_COLOR, (RESTART_BUTTON_X - 2, RESTART_BUTTON_Y - 2, RESTART_BUTTON_WIDTH + 4, RESTART_BUTTON_HEIGHT + 4))
        pygame.draw.rect(screen, RESTART_BUTTON_COLOR, (RESTART_BUTTON_X, RESTART_BUTTON_Y, RESTART_BUTTON_WIDTH, RESTART_BUTTON_HEIGHT))
        font = pygame.font.SysFont("monospace", 20)
        label = font.render("Restart", 1, BLACK)
        screen.blit(label, (RESTART_BUTTON_X + 30, RESTART_BUTTON_Y + 10))

    # Draw the timer
    TIMER_X = 10
    TIMER_Y = 10
    font = pygame.font.SysFont("monospace", 20)
    label = font.render(f"Time: {int(remaining_time)}", 1, YELLOW)
    screen.blit(label, (TIMER_X, TIMER_Y))

    # Draw the time
    font = pygame.font.SysFont("monospace", 20)
    label = font.render(f"{toronto_time}", 1, YELLOW)
    screen.blit(label, (width - 200, 10))

    pygame.display.update()


board = create_board()
game_over = False
turn = 1

pygame.init()

try:
    pygame.mixer.init()
    pygame.mixer.music.load('music.mp3')
    pygame.mixer.music.play(-1)
    sonar_ping_sound = pygame.mixer.Sound('sonar-ping.wav')
    ping_sound = pygame.mixer.Sound('ping.wav')
    win_sound = pygame.mixer.Sound('win.wav')
    lose_sound = pygame.mixer.Sound('you-lose.wav')
except pygame.error:
    print("Mixer not available")
    sonar_ping_sound = None
    ping_sound = None
    win_sound = None
    lose_sound = None

turn_start_time = pygame.time.get_ticks()

SQUARESIZE = 120

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)
draw_board(board, 15, game_over, "00:00:00")
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEMOTION:
            if not game_over:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                if turn == 1:
                    pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE / 2)), RADIUS)
        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_over:
                posx = event.pos[0]
                posy = event.pos[1]
                RESTART_BUTTON_X = width/2 - 70
                RESTART_BUTTON_Y = height/2 + 50
                RESTART_BUTTON_WIDTH = 140
                RESTART_BUTTON_HEIGHT = 40
                if RESTART_BUTTON_X <= posx <= RESTART_BUTTON_X + RESTART_BUTTON_WIDTH and RESTART_BUTTON_Y <= posy <= RESTART_BUTTON_Y + RESTART_BUTTON_HEIGHT:
                    reset_game()

            elif turn == 1:
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARESIZE))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    if ping_sound:
                        ping_sound.play()
                    drop_piece(board, row, col, 2, remaining_time, True)

                    if winning_move(board, 2):
                        game_over = True

                    print_board(board)

                    turn += 1
                    turn = turn % 2
                    turn_start_time = pygame.time.get_ticks()

    if not game_over:
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - turn_start_time) / 1000
        remaining_time = 15 - elapsed_time

        if remaining_time <= 0:
            if turn == 1:  # Human player's turn
                turn += 1
                turn = turn % 2
                turn_start_time = pygame.time.get_ticks()

        if turn == 0:
            col = pick_best_move(board)

            if col is None:
                game_over = True
            elif is_valid_location(board, col):
                #pygame.time.wait(500)
                row = get_next_open_row(board, col)
                if sonar_ping_sound:
                    sonar_ping_sound.play()
                drop_piece(board, row, col, 1, remaining_time, True)

                if winning_move(board, 1):
                    game_over = True

                print_board(board)

                turn += 1
                turn = turn % 2
                turn_start_time = pygame.time.get_ticks()

    toronto_tz = pytz.timezone('America/Toronto')
    toronto_time = datetime.now(toronto_tz).strftime("%I:%M:%S %p")
    draw_board(board, remaining_time, game_over, toronto_time)

    if game_over:
        if turn == 1: # AI won
            if lose_sound:
                lose_sound.play()
            label = myfont.render("You Lose!", 1, RED)
            label_rect = label.get_rect(center=(width/2, SQUARESIZE/2 + 50))
            screen.blit(label, label_rect)
        else: # Human won
            if win_sound:
                win_sound.play()
            label = myfont.render("You Win!", 1, YELLOW)
            label_rect = label.get_rect(center=(width/2, SQUARESIZE/2 + 50))
            screen.blit(label, label_rect)

    pygame.display.update()
