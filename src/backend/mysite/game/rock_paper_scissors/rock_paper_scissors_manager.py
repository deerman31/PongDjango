from .rock_paper_scissors_logic import Game

from typing import List
import uuid

class GameRoom:
    def __init__(self, room_name: str) -> None:
        self.room_name = room_name
        self.player1 = None
        self.player2 = None
        self.game: Game = None
    
    def add_player(self, add_player):
        if self.player1 and self.player2:
            return
        if not self.player1:
            self.player1 = add_player
        else:
            self.player2 = add_player
        if self.player1 and self.player2:
            self.game = Game(self.player1, self.player2)
    
    def remove_memver(self, player):
        if self.player1 == player or self.player2 == player:
            if self.player1 == player:
                self.player1 = None
            else:
                self.player2 = None
    
    def add_score(self, player):
        # 準備ができていない
        if not self.player1 or not self.player2:
            return
        if self.player1 == player:
            self.player1_score += 1
        else:
            self.player2_score += 1


class RockPaperScissorsManager:
    def __init__(self) -> None:
        self.rooms: List[GameRoom] = []
    
    def assign_room(self, player) -> GameRoom:
        for room in self.rooms:
            if room.player1 == player or room.player2:
                return None
            if not room.player1 or not room.player2:
                room.add_player(player)
                return room
        
        new_room_name: str = str(uuid.uuid4())
        new_room: GameRoom = GameRoom(new_room_name)
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
