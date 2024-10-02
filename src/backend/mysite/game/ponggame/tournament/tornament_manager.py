from typing import List
import random
import uuid
from ..game_logic import Game

class TournamentGame:
    def __init__(self, room_name: str, player1, player2) -> None:
        self.room_name: str = room_name
        self.player1 = player1
        self.player2 = player2
        self.game: Game = Game(player1, player2)
        self.player1_ready: bool = False
        self.player2_ready: bool = False
        self.group_name: str = f"game_{self.room_name}"
        self.winner = None

    def remove_member(self, player) -> None:
        if self.player1 == player:
            self.player1 = None
        elif self.player2 == player:
            self.player2 = None
    


class TournamentLobby:
    def __init__(self, lobby_name: str) -> None:
        self.lobby_name: str = lobby_name
        self.waiting_players: List = []
        self.max_capacity: int = 4
        self.is_ready: bool = False

        self.rooms: List[TournamentGame] = []

        self.tournament_bracket: List[List[str]] = []
    
    def check_finished(self) -> bool:
        for game in self.rooms:
            #if game.ready_count != 0:
            #if game.player1_ready or game.player2_ready or not game.winner:
            if not game.winner:
                return False
        return True

    def add_player(self, add_player) -> None:
        if self.is_ready:
            return None

        self.waiting_players.append(add_player)
        if len(self.waiting_players) == self.max_capacity:
            random.shuffle(self.waiting_players)
            pair: List = []
            for player in self.waiting_players:
                pair.append(player)
                if len(pair) == 2:
                    room_name: str = str(uuid.uuid4())
                    room: TournamentGame = TournamentGame(room_name, pair[0], pair[1])
                    self.rooms.append(room)
                    pair.clear()
            self.is_ready = True
            # 準備ができたのでself.waiting_playersを空にする
            self.waiting_players.clear()
    
    def remove_member(self, player) -> None:
        if player in self.waiting_players:
            self.waiting_players.remove(player)
            if self.is_ready:
                self.is_ready = False


# TornamentManagerは待合室を管理
class TournamentManager:
    def __init__(self) -> None:
        self.lobbys: List[TournamentLobby] = []
    
    def assign_lobby(self, player) -> TournamentLobby:
        for lobby in self.lobbys:
            if player in lobby.waiting_players:
                return None
            if lobby.is_ready == False:
                lobby.add_player(player)
                return lobby
        lobby_name: str = str(uuid.uuid4())
        new_lobby = TournamentLobby(lobby_name)
        new_lobby.add_player(player)
        self.lobbys.append(new_lobby)
        return new_lobby

    def release_lobby(self, player) -> None:
        for lobby in self.lobbys:
            if player in lobby.waiting_players:
                # lobbyから削除
                lobby.remove_member(player)
                # lobbyにplayerがいなくなれば、lobby自体を削除
                if not lobby.waiting_players:
                    self.lobbys.remove(lobby)
                break
    
    # tournamentで敗者をlobbyから消すためにrelease_lobby()を使ってしまうとis_readyがFalseになってしまうため、is_readyを再度Trueにする
    def losers_leave(self, player) -> None:
        for lobby in self.lobbys:
            if player in lobby.waiting_players:
                # lobbyから削除
                lobby.remove_member(player)
                lobby.is_ready = True
                # lobbyにplayerがいなくなれば、lobby自体を削除
                if not lobby.waiting_players:
                    self.lobbys.remove(lobby)
                break

    def release_lobby2(self, player) -> None:
        for lobby in self.lobbys:
            for game in lobby.rooms:
                if game.player1 == player or game.player2 == player:
                    if game.player1 == player:
                        game.player1 = None
                    else:
                        game.player2 = None
                    if not game.player1 and not game.player2:
                        lobby.rooms.remove(game)
                    if len(lobby.rooms) == 0:
                        self.lobbys.remove(lobby)
                    break

    def losers_leave2(self, player) -> None:
        for lobby in self.lobbys:
            for game in lobby.rooms:
                if game.player1 == player or game.player2 == player:
                    if game.player1 == player:
                        game.player1 = None
                    else:
                        game.player2 = None
                    if game.player1 is None and game.player2 is None:
                        lobby.rooms.remove(game)
                    if len(lobby.rooms) == 0:
                        self.lobbys.remove(lobby)
                    break

    def get_room(self, player) -> TournamentGame:
        for lobby in self.lobbys:
            for room in lobby.rooms:
                if room.player1 == player or room.player2 == player:
                    return room
        return None
