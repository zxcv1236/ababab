import pygame
import sys
import json
from tkinter import Tk, filedialog, simpledialog

# 初始化Pygame
pygame.init()

# 设置棋盘大小
BOARD_SIZE = 10
CELL_SIZE = 40
BOARD_WIDTH = BOARD_SIZE * CELL_SIZE
BOARD_HEIGHT = BOARD_SIZE * CELL_SIZE

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# 创建屏幕对象
screen = pygame.display.set_mode((BOARD_WIDTH + 400, BOARD_HEIGHT))
pygame.display.set_caption("国际跳棋游戏")

# 加载棋子图片
RED_PIECE = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
pygame.draw.circle(RED_PIECE, RED, (CELL_SIZE // 2, CELL_SIZE // 2), CELL_SIZE // 2)
BLUE_PIECE = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
pygame.draw.circle(BLUE_PIECE, BLUE, (CELL_SIZE // 2, CELL_SIZE // 2), CELL_SIZE // 2)

# 初始化棋盘状态
board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
initial_board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

for i in range(3):
    for j in range(BOARD_SIZE):
        if (i + j) % 2 == 1:
            board[i][j] = 'red'
            initial_board[i][j] = 'red'
        if (BOARD_SIZE - 1 - i + j) % 2 == 1:
            board[BOARD_SIZE - 1 - i][j] = 'blue'
            initial_board[BOARD_SIZE - 1 - i][j] = 'blue'

# 记录当前选中的棋子
selected_piece = None
turn = 'red'
moves = []
game_log = []
current_move_index = -1
LOGS_PER_PAGE = 10
log_page = 0
red_player = "Red Player"
blue_player = "Blue Player"

def draw_board():
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            color = WHITE if (i + j) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            piece = board[i][j]
            if piece == 'red':
                screen.blit(RED_PIECE, (j * CELL_SIZE, i * CELL_SIZE))
            elif piece == 'blue':
                screen.blit(BLUE_PIECE, (j * CELL_SIZE, i * CELL_SIZE))

def draw_ui():
    pygame.draw.rect(screen, GRAY, (BOARD_WIDTH, 0, 400, BOARD_HEIGHT))
    font = pygame.font.Font(None, 24)
    
    turn_text = font.render(f"Turn: {red_player if turn == 'red' else blue_player}", True, BLACK)
    screen.blit(turn_text, (BOARD_WIDTH + 10, 10))
    
    tips_text = font.render("Tips: Make your move", True, BLACK)
    screen.blit(tips_text, (BOARD_WIDTH + 10, 40))

    save_button = pygame.Rect(BOARD_WIDTH + 10, 70, 180, 30)
    pygame.draw.rect(screen, BLACK, save_button)
    save_text = font.render("Save", True, WHITE)
    screen.blit(save_text, (BOARD_WIDTH + 70, 75))
    
    load_button = pygame.Rect(BOARD_WIDTH + 10, 110, 180, 30)
    pygame.draw.rect(screen, BLACK, load_button)
    load_text = font.render("Load", True, WHITE)
    screen.blit(load_text, (BOARD_WIDTH + 70, 115))

    back_initial_button = pygame.Rect(BOARD_WIDTH + 10, 150, 180, 30)
    pygame.draw.rect(screen, BLACK, back_initial_button)
    back_initial_text = font.render("Back to Initial", True, WHITE)
    screen.blit(back_initial_text, (BOARD_WIDTH + 35, 155))

    back_end_button = pygame.Rect(BOARD_WIDTH + 10, 190, 180, 30)
    pygame.draw.rect(screen, BLACK, back_end_button)
    back_end_text = font.render("Back to End", True, WHITE)
    screen.blit(back_end_text, (BOARD_WIDTH + 45, 195))

    prev_button = pygame.Rect(BOARD_WIDTH + 10, 230, 180, 30)
    pygame.draw.rect(screen, BLACK, prev_button)
    prev_text = font.render("<--", True, WHITE)
    screen.blit(prev_text, (BOARD_WIDTH + 85, 235))

    next_button = pygame.Rect(BOARD_WIDTH + 10, 270, 180, 30)
    pygame.draw.rect(screen, BLACK, next_button)
    next_text = font.render("-->", True, WHITE)
    screen.blit(next_text, (BOARD_WIDTH + 85, 275))

    # 显示走步记录
    pygame.draw.rect(screen, WHITE, (BOARD_WIDTH + 10, 310, 380, BOARD_HEIGHT - 320))
    pygame.draw.rect(screen, BLACK, (BOARD_WIDTH + 10, 310, 380, BOARD_HEIGHT - 320), 2)
    
    move_font = pygame.font.Font(None, 20)
    for index, move in enumerate(game_log[log_page * LOGS_PER_PAGE:(log_page + 1) * LOGS_PER_PAGE]):
        move_text = move_font.render(f"{index + 1 + log_page * LOGS_PER_PAGE}: {move[0]} from {move[1][0]} to {move[1][1]}", True, BLACK)
        screen.blit(move_text, (BOARD_WIDTH + 15, 315 + index * 20))

    # 分页按钮
    prev_page_button = next_page_button = None
    if log_page > 0:
        prev_page_button = pygame.Rect(BOARD_WIDTH + 10, BOARD_HEIGHT - 50, 100, 30)
        pygame.draw.rect(screen, BLACK, prev_page_button)
        prev_page_text = font.render("Previous", True, WHITE)
        screen.blit(prev_page_text, (BOARD_WIDTH + 15, BOARD_HEIGHT - 45))
    if (log_page + 1) * LOGS_PER_PAGE < len(game_log):
        next_page_button = pygame.Rect(BOARD_WIDTH + 130, BOARD_HEIGHT - 50, 100, 30)
        pygame.draw.rect(screen, BLACK, next_page_button)
        next_page_text = font.render("Next", True, WHITE)
        screen.blit(next_page_text, (BOARD_WIDTH + 135, BOARD_HEIGHT - 45))

    return (save_button, load_button, back_initial_button, back_end_button, prev_button, next_button,
            prev_page_button, next_page_button)

def get_cell(pos):
    x, y = pos
    return y // CELL_SIZE, x // CELL_SIZE

def save_game():
    Tk().withdraw()
    filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if filepath:
        with open(filepath, 'w') as file:
            json.dump({"board": board, "turn": turn, "moves": moves, "game_log": game_log, "red_player": red_player, "blue_player": blue_player}, file)

def load_game():
    Tk().withdraw()
    filepath = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if filepath:
        with open(filepath, 'r') as file:
            data = json.load(file)
            global board, turn, moves, game_log, current_move_index, log_page, red_player, blue_player
            board = data["board"]
            turn = data["turn"]
            moves = data["moves"]
            game_log = data["game_log"]
            red_player = data["red_player"]
            blue_player = data["blue_player"]
            current_move_index = -1
            log_page = 0

def back_to_initial():
    global board, turn, current_move_index, log_page
    board = [row.copy() for row in initial_board]
    turn = 'red'
    current_move_index = -1
    log_page = 0

def back_to_end():
    global current_move_index, log_page
    current_move_index = len(game_log) - 1
    log_page = len(game_log) // LOGS_PER_PAGE
    replay_moves(current_move_index)

def replay_moves(index):
    global board, turn
    board = [row.copy() for row in initial_board]
    turn = 'red'
    for move in game_log[:index + 1]:
        piece, (start, end) = move
        board[start[0]][start[1]] = None
        board[end[0]][end[1]] = piece
        turn = 'blue' if turn == 'red' else 'red'

def next_move():
    global current_move_index, log_page
    if current_move_index < len(game_log) - 1:
        current_move_index += 1
        replay_moves(current_move_index)
        log_page = current_move_index // LOGS_PER_PAGE

def prev_move():
    global current_move_index, log_page
    if current_move_index >= 0:
        current_move_index -= 1
        replay_moves(current_move_index)
        log_page = current_move_index // LOGS_PER_PAGE

def next_page():
    global log_page
    if (log_page + 1) * LOGS_PER_PAGE < len(game_log):
        log_page += 1

def prev_page():
    global log_page
    if log_page > 0:
        log_page -= 1

def choose_players():
    Tk().withdraw()
    red_name = simpledialog.askstring("Red Player", "Enter name for Red Player:")
    blue_name = simpledialog.askstring("Blue Player", "Enter name for Blue Player:")
    return red_name or "Red Player", blue_name or "Blue Player"

def choose_turn():
    font = pygame.font.Font(None, 36)
    red_button = pygame.Rect(100, 100, 200, 50)
    blue_button = pygame.Rect(100, 200, 200, 50)
    running = True
    while running:
        screen.fill(WHITE)
        pygame.draw.rect(screen, RED, red_button)
        pygame.draw.rect(screen, BLUE, blue_button)
        red_text = font.render(red_player, True, WHITE)
        blue_text = font.render(blue_player, True, WHITE)
        screen.blit(red_text, (150, 115))
        screen.blit(blue_text, (150, 215))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if red_button.collidepoint(pos):
                    return 'red'
                elif blue_button.collidepoint(pos):
                    return 'blue'

# 游戏主循环
red_player, blue_player = choose_players()
turn = choose_turn()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if pos[0] < BOARD_WIDTH:
                row, col = get_cell(pos)
                if selected_piece:
                    if board[row][col] is None and (row + col) % 2 == 1:
                        board[row][col] = selected_piece
                        game_log.append((selected_piece, (selected_piece_pos, (row, col))))
                        selected_piece = None
                        turn = 'blue' if turn == 'red' else 'red'
                elif board[row][col] == turn:
                    selected_piece = board[row][col]
                    selected_piece_pos = (row, col)
                    board[row][col] = None
            else:
                save_button, load_button, back_initial_button, back_end_button, prev_button, next_button, prev_page_button, next_page_button = draw_ui()
                if save_button.collidepoint(pos):
                    save_game()
                elif load_button.collidepoint(pos):
                    load_game()
                elif back_initial_button.collidepoint(pos):
                    back_to_initial()
                elif back_end_button.collidepoint(pos):
                    back_to_end()
                elif prev_button.collidepoint(pos):
                    prev_move()
                elif next_button.collidepoint(pos):
                    next_move()
                elif prev_page_button and prev_page_button.collidepoint(pos):
                    prev_page()
                elif next_page_button and next_page_button.collidepoint(pos):
                    next_page()

    screen.fill(WHITE)
    draw_board()
    draw_ui()
    pygame.display.flip()

pygame.quit()
sys.exit()
