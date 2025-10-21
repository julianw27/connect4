#!/usr/bin/env python3
import bottle
import json


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


# _______________POST REQUEST HANDLER TO CHECK WINNER_____________
@bottle.route('/check_winner', method='POST')
def check_winner_endpoint():
    print("=== CHECK_WINNER CALLED ===")
    
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
            return json.dumps(False)
    else:
        print("ERROR: No 'value' in form data")
        return json.dumps(False)
    
    # Check for winner and return result as JSON
    has_winner = check_winner(board)
    print(f"Returning: {has_winner}")
    return json.dumps(has_winner)

# __________MAIN PROGRAM ENTRY POINT_____________
if __name__ == '__main__':
    print("Connect Four Winner Check Service starting on port 8736...")
    print("  POST /check_winner - Check if there's a winner on the board")
    bottle.run(host='::', port=8736)