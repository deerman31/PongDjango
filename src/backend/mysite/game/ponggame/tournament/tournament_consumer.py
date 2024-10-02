from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import json
from typing import List, Optional
import uuid
from .tornament_manager import TournamentManager, TournamentLobby, TournamentGame
from ..game_logic import Game
from channels.db import database_sync_to_async

# tournamentを管理するmanagerをここでgroubalに定義
g_tournament_manager = TournamentManager()

class TournamentConsumer(AsyncWebsocketConsumer):
    def generate_tournament_bracket(self) -> List[str]:
        tmp_list: List[str] = []
        for game in self.lobby.rooms:
            tmp_list.append(game.player1.name)
            tmp_list.append(game.player2.name)
        return tmp_list

    async def connect(self) -> None:
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return

        self.lobby: TournamentLobby = g_tournament_manager.assign_lobby(self.user)
        if self.lobby == None:
            await self.close()
            return

        self.lobby_name = self.lobby.lobby_name
        self.group_name = f"lobby_{self.lobby_name}"

        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        if self.lobby.is_ready:

            self.lobby.tournament_bracket.append(self.generate_tournament_bracket())
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "tournament_ready",
                    "lobby_name": self.lobby_name,
                    "tournament_bracket": json.dumps(self.lobby.tournament_bracket),
                    "message": "Tournament is ready to start.",
                }
            )

    async def tournament_ready(self, event):
        # print("tournament_ready:", self.user.name)
        room: TournamentGame = g_tournament_manager.get_room(self.user)
        # ここでgameのgroupを設定
        await self.channel_layer.group_add(room.group_name, self.channel_name)
        # ここで受け取ったイベントをフロントエンドに送信する
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "lobby_name": event["lobby_name"],
            "tournament_bracket": event["tournament_bracket"]
        }))


    async def disconnect(self, close_code: Optional[int]) -> None:
        # print("disconnect:", self.user.name)
        room: TournamentGame = g_tournament_manager.get_room(self.user)
        if close_code != 1000:
            # gameが始まっている
            if self.lobby.is_ready:
                winner = None
                if room.player1 == self.user:
                    winner = room.player2
                else:
                    winner = room.player1

                if winner:
                    room.winner = winner
                    await self.save_game_result()
                    if self.user == room.player1:
                        room.player1 = None
                    else:
                        room.player2 = None

                    await self.channel_layer.group_send(
                        room.group_name,
                        {
                            'type': 'game_end',
                            'message': json.dumps({'game_over': True, 'winner': winner.name}),
                        }
                    )
                # winnerがいないということは勝利し、決勝でもう片方のwinnerを待っている間にdisconnectされたから
                else:
                    g_tournament_manager.release_lobby2(self.user)

            else:
                g_tournament_manager.release_lobby(self.user)
        else:
            g_tournament_manager.release_lobby2(self.user)

        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None) -> None:
        # print("receive:", self.user.name)
        # lobbyの準備ができていないときには何も処理しない。
        if not self.lobby.is_ready:
            return

        data = json.loads(text_data)
        action: str = data.get('action')

        if action == 'game_room_is_ready':
            await self.game_room_is_ready()
            return

        room: TournamentGame = g_tournament_manager.get_room(self.user)

        player = room.game.players[2] if room.player2 == self.user else room.game.players[1]
        if action == 'up':
            player.paddle.move_up()
        elif action == 'down':
            player.paddle.move_down(600)

    # あるユーザーがゲームの準備ができたばあいクリックを押しにgame_okとメッセージが飛んでくる。
    async def game_room_is_ready(self) -> None:
        # print("game_room_is_ready:", self.user.name)
        room: TournamentGame = g_tournament_manager.get_room(self.user)
        # await self.channel_layer.group_add(room.group_name, self.channel_name)
        if self.user == room.player1:
            room.player1_ready = True
        elif self.user == room.player2:
            room.player2_ready = True

        if room.player1_ready and room.player2_ready:
            #room.is_game_start = True
            await self.channel_layer.group_send(
                room.group_name,
                {
                    "type": "start_individual_game",
                }
            )
            game: Game = room.game
            game.start()
            asyncio.create_task(self.move_ball())

    async def start_individual_game(self, event) -> None:
        # print("start_individual_game:", self.user.name)

        #message = json.loads(event['message'])
        await self.send(text_data=json.dumps({
            'type': 'start_game',
        }))

    async def game_end(self, event) -> None:
        room: TournamentGame = g_tournament_manager.get_room(self.user)
        await self.channel_layer.group_discard(room.group_name, self.channel_name)
        if room.player1 == self.user:
            room.player1_ready = False
        elif room.player2 == self.user:
            room.player2_ready = False
        # 敗者のuserをgameから外す
        data = json.loads(event["message"])
        if data["winner"] != self.user.name:
            #g_tournament_manager.losers_leave(self.user)
            g_tournament_manager.losers_leave2(self.user)
            await self.send(text_data=json.dumps({
                'type': 'loser_gets_out',
            }))
            return
        else:
            room.winner = self.user
        if len(self.lobby.rooms) == 1:
            await self.send(text_data=json.dumps({
                'type': 'victory',
            }))
            g_tournament_manager.release_lobby2(self.user)
            return

        # 全てのゲームが終了
        tmp: TournamentGame = None
        if self.lobby.check_finished():
            new_rooms = []
            for i, game in enumerate(self.lobby.rooms,start=1):
                if i % 2 == 1:
                    tmp = game
                else:
                    player1 = tmp.winner
                    player2 = game.winner
                    room_name: str = str(uuid.uuid4())
                    new_room: TournamentGame = TournamentGame(room_name, player1, player2)
                    new_rooms.append(new_room)
            self.lobby.rooms = new_rooms

            tmp_list: List[str] = []
            for game in self.lobby.rooms:
                tmp_list.append(game.player1.name)
                tmp_list.append(game.player2.name)
            self.lobby.tournament_bracket.append(tmp_list)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "tournament_ready",
                    "lobby_name": self.lobby_name,
                    "tournament_bracket": json.dumps(self.lobby.tournament_bracket),
                    "message": "Tournament is ready to start."
                }
            )
        else:
            await self.send(text_data=json.dumps({
                'type': 'game_end',
                'message': event["message"],
            }))


    async def move_ball(self):
        room: TournamentGame = g_tournament_manager.get_room(self.user)
        game: Game = room.game

        while game.started:
            game.move_ball()
            await self.send_game_state(room)
            await asyncio.sleep(0.01)

            if game.is_game_over():
                # print("終了:", )
                winner = game.get_winner()
                await self.channel_layer.group_send(
                    room.group_name,
                    {
                        'type': 'game_end',
                        'message': json.dumps({'game_over': True, 'winner': winner}),
                    }
                )
                await self.save_game_result()
                game.reset()
                return

    async def send_game_state(self, room: TournamentGame):
        game: Game = room.game
        await self.channel_layer.group_send(room.group_name, {'type': 'game_state', 'message': json.dumps(game.get_state())})

    async def game_state(self, event):
        await self.send(text_data=json.dumps({
            'type': 'drawing',
            'message': event["message"],
        }))

    async def game_over(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_over',
            'message': event["message"],
        }))

    @database_sync_to_async
    def save_game_result(self):
        from accounts.models import GameResult
        room: TournamentGame = g_tournament_manager.get_room(self.user)
        game: Game = room.game
        if not game.result_saved:  # 勝敗が記録されていない場合のみ記録
            winner, loser, win_score, lose_score = game.get_game_result()
            game_result = GameResult()
            game_result.record_result(winner, loser, win_score, lose_score)
            game.result_saved = True  # 勝敗が記録されたことをマーク