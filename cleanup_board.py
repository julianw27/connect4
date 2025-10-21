#!/usr/bin/env python3
import bottle
import json

# Convert board state to 42-position boolean array for cleanup
# Position 41 = top-left corner, position 0 = bottom-right corner
# Row by row from top to bottom, left to right within each row
# Any coin needs cleanup = true, empty space = false
def get_coin_positions_for_cleanup(board):
    cleanup_positions = []
    
    for row in range(6):      # 0,1,2,3,4,5 (top to bottom)
        for col in range(7):  # 0,1,2,3,4,5,6 (left to right)
            has_coin = (board[row][col] != 0)
            cleanup_positions.append(has_coin)
    
    # Reverse the array so position 41 is top-left, position 0 is bottom-right
    cleanup_positions.reverse()
    return cleanup_positions


# __________POST REQUEST HANDLER FOR CLEANUP ARRAY_____________
@bottle.route('/cleanup', method='POST')
def cleanup():
    print("=== CLEANUP CALLED ===")
    
    # Receive data from CPEE
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
            return json.dumps([])
    else:
        print("ERROR: No 'value' in form data")
        return json.dumps([])
    
    # Get cleanup positions for the board and return as JSON
    cleanup_positions = get_coin_positions_for_cleanup(board)
    print(f"Returning cleanup array: {cleanup_positions}")
    return json.dumps(cleanup_positions)

# __________MAIN PROGRAM ENTRY POINT_____________
if __name__ == '__main__':
    print("Connect Four Cleanup Service starting on port 8735...")
    print("  POST /cleanup_board - Convert board state to 42-position cleanup array")
    bottle.run(host='::', port=8735)