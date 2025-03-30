import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH, HEIGHT = 800, 600
BOARD_SIZE = 400
SQUARE_SIZE = BOARD_SIZE // 8
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chromachess")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT = (247, 247, 105, 128)  # Yellow highlight with some transparency
CURSOR = (0, 255, 0, 180)  # Green cursor with some transparency

# Define piece colors
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Create a simple board representation
board = [
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
]

# Initialize player inventories
red_inventory = []
blue_inventory = []

# Game state variables
selected_piece = None
selected_pos = None
cursor_pos = [0, 0]  # Start at top-left corner
valid_moves = []
current_player = 'blue'  # blue goes first

# Font for displaying text
font = pygame.font.SysFont('Arial', 24)
instruction_font = pygame.font.SysFont('Arial', 16)

def draw_board():
    for row in range(8):
        for col in range(8):
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    # Highlight valid moves
    for row, col in valid_moves:
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        s.fill(HIGHLIGHT)
        screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
    
    # Highlight selected piece
    if selected_pos:
        row, col = selected_pos
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        s.fill((255, 165, 0, 128))  # Orange highlight
        screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
    
    # Draw cursor
    s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
    s.fill(CURSOR)
    screen.blit(s, (cursor_pos[1] * SQUARE_SIZE, cursor_pos[0] * SQUARE_SIZE))

def draw_pieces():
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != ' ':
                color = RED if piece.isupper() else BLUE
                pygame.draw.circle(screen, color, 
                                   (col * SQUARE_SIZE + SQUARE_SIZE // 2, 
                                    row * SQUARE_SIZE + SQUARE_SIZE // 2), 
                                   SQUARE_SIZE // 3)
                
                # Draw piece type (simplified)
                text = font.render(piece.upper(), True, WHITE)
                text_rect = text.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2, 
                                                 row * SQUARE_SIZE + SQUARE_SIZE // 2))
                screen.blit(text, text_rect)

def draw_inventories():
    # Draw Red's inventory
    pygame.draw.rect(screen, (220, 220, 220), (BOARD_SIZE + 20, 50, 150, 200))
    text = font.render("Red's Pieces", True, RED)
    screen.blit(text, (BOARD_SIZE + 30, 20))
    
    for i, piece in enumerate(red_inventory):
        pygame.draw.circle(screen, RED, (BOARD_SIZE + 50, 80 + i * 30), 10)
        text = font.render(piece.upper(), True, WHITE)
        screen.blit(text, (BOARD_SIZE + 45, 75 + i * 30))
    
    # Draw Blue's inventory
    pygame.draw.rect(screen, (220, 220, 220), (BOARD_SIZE + 20, 350, 150, 200))
    text = font.render("Blue's Pieces", True, BLUE)
    screen.blit(text, (BOARD_SIZE + 30, 320))
    
    for i, piece in enumerate(blue_inventory):
        pygame.draw.circle(screen, BLUE, (BOARD_SIZE + 50, 380 + i * 30), 10)
        text = font.render(piece.upper(), True, WHITE)
        screen.blit(text, (BOARD_SIZE + 45, 375 + i * 30))

def draw_current_player():
    text = font.render(f"Current Player: {current_player.capitalize()}", True, 
                      BLUE if current_player == 'blue' else RED)
    screen.blit(text, (BOARD_SIZE + 30, HEIGHT - 80))
    
    # Draw instructions
    instructions = [
        "Controls:",
        "Arrow Keys - Move cursor",
        "SPACE - Select/Move piece"
    ]
    
    for i, line in enumerate(instructions):
        text = instruction_font.render(line, True, BLACK)
        screen.blit(text, (BOARD_SIZE + 30, HEIGHT - 50 + i * 20))

def get_valid_moves(row, col):
    """Get valid moves for the selected piece (simplified rules)"""
    piece = board[row][col]
    moves = []
    
    # Check if it's the current player's piece
    if (piece.isupper() and current_player == 'red') or (piece.islower() and current_player == 'blue'):
        # Simplified movement rules
        if piece.upper() == 'P':  # Pawn
            direction = -1 if piece.isupper() else 1
            # Move forward
            if 0 <= row + direction < 8 and board[row + direction][col] == ' ':
                moves.append((row + direction, col))
            # Capture diagonally
            for c in [col-1, col+1]:
                if 0 <= c < 8 and 0 <= row + direction < 8:
                    target = board[row + direction][c]
                    if target != ' ':
                        if (piece.isupper() and target.islower()) or (piece.islower() and target.isupper()):
                            moves.append((row + direction, c))
        
        elif piece.upper() == 'R':  # Rook
            # Move horizontally and vertically
            for direction in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                for i in range(1, 8):
                    r, c = row + direction[0] * i, col + direction[1] * i
                    if not (0 <= r < 8 and 0 <= c < 8):
                        break
                    if board[r][c] == ' ':
                        moves.append((r, c))
                    elif (piece.isupper() and board[r][c].islower()) or (piece.islower() and board[r][c].isupper()):
                        moves.append((r, c))
                        break
                    else:
                        break
        
        elif piece.upper() == 'N':  # Knight
            for dr, dc in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] == ' ' or (piece.isupper() and board[r][c].islower()) or (piece.islower() and board[r][c].isupper()):
                        moves.append((r, c))
        
        elif piece.upper() == 'B':  # Bishop
            # Move diagonally
            for direction in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                for i in range(1, 8):
                    r, c = row + direction[0] * i, col + direction[1] * i
                    if not (0 <= r < 8 and 0 <= c < 8):
                        break
                    if board[r][c] == ' ':
                        moves.append((r, c))
                    elif (piece.isupper() and board[r][c].islower()) or (piece.islower() and board[r][c].isupper()):
                        moves.append((r, c))
                        break
                    else:
                        break
        
        elif piece.upper() == 'Q':  # Queen
            # Move like rook and bishop combined
            for direction in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                for i in range(1, 8):
                    r, c = row + direction[0] * i, col + direction[1] * i
                    if not (0 <= r < 8 and 0 <= c < 8):
                        break
                    if board[r][c] == ' ':
                        moves.append((r, c))
                    elif (piece.isupper() and board[r][c].islower()) or (piece.islower() and board[r][c].isupper()):
                        moves.append((r, c))
                        break
                    else:
                        break
        
        elif piece.upper() == 'K':  # King
            # Move one square in any direction
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    r, c = row + dr, col + dc
                    if 0 <= r < 8 and 0 <= c < 8:
                        if board[r][c] == ' ' or (piece.isupper() and board[r][c].islower()) or (piece.islower() and board[r][c].isupper()):
                            moves.append((r, c))
    
    return moves

def handle_space_key():
    global selected_piece, selected_pos, valid_moves, current_player
    
    row, col = cursor_pos
    print(f"Cursor position: {row}, {col}")
    print(f"Current player: {current_player}")
    
    # If no piece is selected, try to select one
    if selected_piece is None:
        piece = board[row][col]
        print(f"Trying to select piece: {piece}")
        if piece != ' ':
            # Check if it's the current player's piece
            if (piece.isupper() and current_player == 'red') or (piece.islower() and current_player == 'blue'):
                selected_piece = piece
                selected_pos = (row, col)
                valid_moves = get_valid_moves(row, col)
                print(f"Selected piece {piece} at {row}, {col}")
                print(f"Valid moves: {valid_moves}")
            else:
                print("Not your piece!")
    
    # If a piece is already selected, try to move it
    else:
        # Check if the cursor position is a valid move
        if (row, col) in valid_moves:
            # If there's an opponent's piece, capture it
            if board[row][col] != ' ':
                captured_piece = board[row][col]
                if current_player == 'red':
                    red_inventory.append(captured_piece)
                else:
                    blue_inventory.append(captured_piece)
            
            # Move the piece
            board[row][col] = selected_piece
            board[selected_pos[0]][selected_pos[1]] = ' '
            
            # Switch player
            current_player = 'blue' if current_player == 'red' else 'red'
            
            # Reset selection
            selected_piece = None
            selected_pos = None
            valid_moves = []
        
        # If it's not a valid move, deselect the piece
        elif (row, col) != selected_pos:
            selected_piece = None
            selected_pos = None
            valid_moves = []

def main():
    global cursor_pos
    
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    cursor_pos[0] = max(0, cursor_pos[0] - 1)
                elif event.key == pygame.K_DOWN:
                    cursor_pos[0] = min(7, cursor_pos[0] + 1)
                elif event.key == pygame.K_LEFT:
                    cursor_pos[1] = max(0, cursor_pos[1] - 1)
                elif event.key == pygame.K_RIGHT:
                    cursor_pos[1] = min(7, cursor_pos[1] + 1)
                elif event.key == pygame.K_SPACE:
                    handle_space_key()

        screen.fill(WHITE)
        draw_board()
        draw_pieces()
        draw_inventories()
        draw_current_player()
        pygame.display.flip()
        
        clock.tick(30)  # Limit to 30 FPS

if __name__ == "__main__":
    main()
