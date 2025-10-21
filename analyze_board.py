#!/usr/bin/env python3
import bottle
import json
import random
import requests

# IP Address of the Banana PI in the internal network
PI_ADDRESS = "131.159.6.7"

# _____ CHECK IF THERE IS A WINNER _______
def check_winner(board):
    rows = len(board)
    cols = len(board[0]) if rows else 0
    
    # Checking for horizontal wins
    for r in range(rows):
        for c in range(cols - 3):
            v = board[r][c]
            if v != 0 and all(board[r][c + i] == v for i in range(4)):
                return True

    # Checking for vertical wins
    for c in range(cols):
        for r in range(rows - 3):
            v = board[r][c]
            if v != 0 and all(board[r + i][c] == v for i in range(4)):
                return True

    # Checking for diagonal wins (top-left to bottom-right)
    for r in range(rows - 3):
        for c in range(cols - 3):
            v = board[r][c]
            if v != 0 and all(board[r + i][c + i] == v for i in range(4)):
                return True

    # Checking for diagonal wins (bottom-left to top-right)
    for r in range(3, rows):
        for c in range(cols - 3):
            v = board[r][c]
            if v != 0 and all(board[r - i][c + i] == v for i in range(4)):
                return True
    
    return False

# Check for the first empty row in a column
def first_empty_row(board, col):
    for r in range(len(board)-1, -1, -1):
        if board[r][col] == 0:
            return r
    return None


# Choose the best move for the robot (player 2 - BLUE)
def choose_move(board):

    # 1. Check for winning move for BLUE robot
    for col in range(7):
        r = first_empty_row(board, col)
        if r is None: 
            continue
        board[r][col] = 2 # Simulate BLUE move
        if check_winner(board):
            board[r][col] = 0
            return col # Found winning move
        board[r][col] = 0
    
    # 2. Block opponent from winning
    for col in range(7):
        r = first_empty_row(board, col)
        if r is None: 
            continue
        board[r][col] = 1 # Simulate opponent move
        if check_winner(board):
            board[r][col] = 0
            return col # Found blocking move
        board[r][col] = 0
    
    # 3. Look for moves that create multiple winning opportunities
    for col in range(7):
        r = first_empty_row(board, col)
        if r is None: 
            continue
        board[r][col] = 2
        
        # Count how many ways it could win next turn
        win_opportunities = 0
        for test_col in range(7):
            test_r = first_empty_row(board, test_col)
            if test_r is None: 
                continue
            board[test_r][test_col] = 2
            if check_winner(board):
                win_opportunities += 1
            board[test_r][test_col] = 0
        
        board[r][col] = 0
        
        if win_opportunities >= 2:
            return col # Found a move creating multiple threats
    
    # 4. Avoid dangerous moves that give opponent immediate wins
    safe_moves = []
    for col in range(7):
        r = first_empty_row(board, col)
        if r is None:
            continue
        
        # Check if this move gives opponent a winning opportunity
        board[r][col] = 2
        gives_opponent_win = False
        
        for test_col in range(7):
            test_r = first_empty_row(board, test_col)
            if test_r is not None:
                board[test_r][test_col] = 1
                if check_winner(board):
                    gives_opponent_win = True
                board[test_r][test_col] = 0
                if gives_opponent_win:
                    break
        
        board[r][col] = 0
        
        if not gives_opponent_win:
            safe_moves.append(col) # This move is safe
    
    # 5. From safe moves, prefer center as much as possible
    if safe_moves:
        center_safe = [col for col in safe_moves if col in [2, 3, 4]]
        if center_safe:
            return random.choice(center_safe)
        return random.choice(safe_moves)
    
    # 6. Fallback pick any available move, prefer center
    for col in [3, 2, 4, 1, 5, 0, 6]:
        if first_empty_row(board, col) is not None:
            return col
    return None

# _____________POST REQUEST HANDLER TO CAPTURE BOARD STATE USING BANANA PI___________
@bottle.route('/capture_board', method='POST')
def capture_board():
    print("=== CAPTURE_BOARD CALLED ===")
    pi_url = f"http://{PI_ADDRESS}:9547/capture_board" # Pi server URL
    response = requests.post(pi_url, timeout=90) # Forward request to Pi
    board_data = response.json() # Get board data from Pi response
    print(f"Board received from Pi")
    return json.dumps(board_data) # Return board data as JSON to CPEE


# _______________POST REQUEST HANDLER TO ANALYZE CURRENT BOARD STATE_____________
@bottle.route('/analyze', method='POST')
def analyze():
    print("=== ANALYZE CALLED ===")
    
    # CPEE sends form data
    forms = bottle.request.forms
    print(f"Form data: {dict(forms)}")
    
    # Check for key 'value' in forms
    if 'value' in forms:
        board_data = forms.get('value')
        print(f"Received board data: {board_data}")
        
        # Parse the board data
        try:
            board = json.loads(board_data)
            print(f"Parsed board: {board}")
        except:
            print("ERROR: Could not parse board data as JSON")
            return 0
    else:
        print("ERROR: No 'value' in form data")
        return 0

    # Determine the next move and return it
    next_col = choose_move(board)
    print(f"Returning: {next_col}")
    return json.dumps(next_col)

# __________MAIN PROGRAM ENTRY POINT_____________
if __name__ == '__main__':
    print("Connect Four Analysis Service starting on port 8734...")
    print("  POST /capture_board - Forward capture request to Pi and return board data")
    print("  POST /analyze - Analyze board state and return AI move")
    print(f"  Pi Address: {PI_ADDRESS}:9547")
    bottle.run(host='::', port=8734)
