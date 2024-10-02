from .single_game_manager import SingleGameManager, GameRoom

from channels.generic.websocket import AsyncWebsocketConsumer

import asyncio
import json
from typing import List, Optional

from ..game_logic import Game
from channels.db import database_sync_to_async

g_single_game_manager = SingleGameManager()

class SingleGameConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return
        
        self.room: GameRoom = g_single_game_manager.assign_room(self.user)
        if not self.room:
            await self.close()
            return
        
        self.room_name: str = self.room.room_name
        self.group_name: str = f"room_{self.room_name}"

        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        if self.room.player1 and self.room.player2:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "game_ready",
                    "room_name": self.room_name,
                    "message": "Tournament is ready to start.",
                }
            )
            self.room.game.start()
            asyncio.create_task(self.move_ball())

    async def receive(self, text_data=None, bytes_data=None) -> None:
        # lobbyの準備ができていないときには何も処理しない。
        if not self.room.player1 or not self.room.player2:
            return

        data = json.loads(text_data)

        action: str = data.get('action')

        room: GameRoom = self.room

        player = room.game.players[2] if room.player2 == self.user else room.game.players[1]
        if action == 'up':
            player.paddle.move_up()
        elif action == 'down':
            player.paddle.move_down(600)

    async def disconnect(self, close_code: Optional[int]) -> None:
        room: GameRoom = self.room

        if close_code != 1000:
            if room.player1 and room.player2:
                winner = None
                if room.player1 == self.user:
                    winner = room.player2
                else:
                    winner = room.player1
                if winner:
                    self.room.winner_name = winner
                    await self.save_game_result()
                    if self.user == room.player1:
                        room.player1 = None
                    else:
                        room.player2 = None
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            'type': 'game_end',
                            'message': json.dumps({'game_over': True, 'winner': winner.name}),
                        }
                    )
                    
            else:
                g_single_game_manager.release_room(self.user)

        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def game_end(self, event) -> None:
        await self.send(text_data=json.dumps({
            'type': 'game_end',
            'message': event["message"],
        }))
        self.room.game.stop()
        g_single_game_manager.release_room(self.user)

    async def game_ready(self, event) -> None:
        await self.send(text_data=json.dumps({
            "type": "start_game",
        }))

    async def move_ball(self):
        room: GameRoom = self.room
        game: Game = room.game

        while game.started:
            game.move_ball()
            await self.send_game_state(room)
            await asyncio.sleep(0.01)

            if game.is_game_over():
                winner = game.get_winner()
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'game_end',
                        'message': json.dumps({'game_over': True, 'winner': winner}),
                    }
                )
                self.room.winner_name = winner
                await self.save_game_result()
                game.reset()
                return

    async def send_game_state(self, room: GameRoom):
        game: Game = room.game
        await self.channel_layer.group_send(self.group_name, {'type': 'game_state', 'message': json.dumps(game.get_state())})

    async def game_state(self, event):
        await self.send(text_data=json.dumps({
            'type': 'drawing',
            'message': event["message"],
        }))

    @database_sync_to_async
    def save_game_result(self):
        from accounts.models import GameResult
        room: GameRoom = self.room
        game: Game = room.game
        if not game.result_saved:  # 勝敗が記録されていない場合のみ記録
            winner, loser, win_score, lose_score = game.get_game_result()
            if loser == self.room.winner_name:
                loser = winner
                winner = self.room.winner_name
            game_result = GameResult()
            game_result.record_result(winner, loser, win_score, lose_score)
            game.result_saved = True  # 勝敗が記録されたことをマーク
