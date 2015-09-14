# Thud
A Python implementation of Discworld's Thud!

This is a simple Python backend for the boardgame Thud, which is a bit like chess but with more flying dwarves. 
It currently only uses the classic rules, but Khoom Valley rules are a planned feature.

The rules for Thud are simple, but mastering the game is challenging.  Or maybe I'm just terrible at strategic board
games.

The Board
The board is a 15x15 square, with triangles cut away in each of the corners to create an octagon.  32 Dwarves start
arrayed on all the edge positions except for the center of each short side.  8 Trolls start arrayed around an
impassable center space called the Thud Stone.

Rules:
Dwarves can move any number of squares in any direction, including horizontally, vertically, and diagonally.
Trolls can move one square in any direction.
Dwarves capture a Troll by moving into the space it occupies, but they may not move more than one space to complete a
capture.  This means a Dwarf must start their turn next to a Troll in order to make a capture.
Trolls capture dwarves by moving into a space next to them.  A troll can capture as many Dwarves as they are able to
stand next to - theoretically, this means 8, but practically it's limited to 4 or 5.

However, both Dwarves and Trolls may work together to make captures more than one space away.

Tossing/Shoving
When either Dwarves or Trolls get in a line, they may work together to throw the leading creature at their enemy.  Both
are able to throw as far as there are allies in a straight line behind them - four creatures in a line can Toss/Shove
the lead creature up to four spaces.  There is no minimum distance for a Toss/Shove.  In order for Dwarves to make a
Toss, the lead Dwarf must land on the space occupied by a target troll.  Trolls are larger, and don't fly through the
air easily, so they simply Shove their compatriots towards the Dwarves.  A Troll must land in an empty space at the end
of a shove.

# Thud Gameserver API

This backend is run on a gameserver at 192.241.198.50:12000.

There are two possible methods for a client to start a game.  Using HTTP POST you can start a game for multiple players
on the same computer.  Using a websocket connection you can allow a player to connect and choose other players to match
with.

##### HTTP POST
To start a game, POST "/start" with the following JSON data in the body:
    Start game:
        {"game": "begin",
         "player_one": "Will",
         "player_two": "Tom"}

     This returns the entire board state, along with tokens for each player so the server can ensure you're moving at
     the correct times:
        {"game": "game_token",
        "player_one": "player_one_token",
        "player_two": "player_two_token",
        "board": {"row_num": [row_data]}}

To execute a move, POST "/move" with the following JSON data in the body:

    Making a move:
    
        {"game": "correct_game_token",
        "player":"correct_player_token",
        "start": [x, y],
        "destination": [x, y]}
    
    This returns either True, a dictionary of pieces that are removed, or False if the move fails:
       
        If move is a valid move, returns true:
            True
        
        If move is a valid attack, the x,y coordinates of any possible targets:
            [[target_x, target_y]]
        
        If move is invalid, returns false:
            False


To validate a move, meaning ensure a move is valid without actually executing that move, POST "/move/validate" with the 
same JSON you would use for "/move". This does not modify board state in any way, but means you don't need to implement
game logic in your UI layer.

        
##### Websockets for single players

The weboscket connection is reached at "/match/playername".  You may not connect with a playername that is already
connected.  The websocket layer is simply a wrapper around the HTTP POST JSON data described above, where the endpoint
(i.e. "/move") is included as the key, and the JSON data is the value. i.e.:
    {"move": {JSON_Move_Data}}