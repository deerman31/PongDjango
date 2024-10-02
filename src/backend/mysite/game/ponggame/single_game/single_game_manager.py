from typing import List
import uuid
from ..game_logic import Game

class GameRoom:
    def __init__(self, room_name: str):
        self.room_name: str = room_name
        self.player1 = None
        self.player2 = None
        self.game: Game = None
        self.winner_name:str = ""
    
    def add_player(self, add_player) -> None:
        if self.player1 and self.player2:
            return
        if not self.player1:
            self.player1 = add_player
        else:
            self.player2 = add_player
        if self.player1 and self.player2:
            game: Game = Game(self.player1, self.player2)
            self.game = game
    
    def remove_memver(self, player) -> None:
        if self.player1 == player or self.player2 == player:
            if self.player1 == player:
                self.player1 = None
            else:
                self.player2 = None


class SingleGameManager:
    def __init__(self):
        self.rooms: List[GameRoom] = []
    
    def assign_room(self, player) -> GameRoom:
        for room in self.rooms:
            #if room.player1 == player or room.player2:
            if room.player1 == player or room.player2 == player:
                return None
            if not room.player1 or not room.player2:
                room.add_player(player)
                return room

        new_room_name: str = str(uuid.uuid4())
        new_room: GameRoom = GameRoom(new_room_name)
        #print(player.name)
        new_room.add_player(player)
        self.rooms.append(new_room)
        return new_room

    def release_room(self, player) -> None:
        for room in self.rooms:
            if room.player1 == player or room.player2 == player:
                room.remove_memver(player)
                if room.player1 is None and room.player2 is None:
                    self.rooms.remove(room)
                break


    def get_room(self, player) -> GameRoom:
        for room in self.rooms:
            if room.player1 == player or room.player2 == player:
                return room
        return None

        
