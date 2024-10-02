from .rock_paper_scissors_manager import RockPaperScissorsManager, GameRoom
from .rock_paper_scissors_logic import Hands, Player, Game
from channels.generic.websocket import AsyncWebsocketConsumer

import asyncio
import json
from channels.db import database_sync_to_async
from typing import List, Tuple, Optional

g_manager = RockPaperScissorsManager()

class RockPaperScissorsConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return
        
        self.room: GameRoom = g_manager.assign_room(self.user)
        if not self.room:
            await self.close()
            return
        
        self.room_name: str = self.room.room_name
        self.group_name: str = f"rpsroom_{self.room_name}"

        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        if self.room.player1 and self.room.player2:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "game_ready",
                    "room_name": self.room_name,
                    "message": "janken is ready to start.",
                }
            )

    async def receive(self, text_data=None, bytes_data=None) -> None:
        # roomの準備ができていないときには何も処理しない。
        if not self.room.player1 or not self.room.player2:
            return
        
        data = json.loads(text_data)
        action: str = data.get('action')

        room: GameRoom = g_manager.get_room(self.user)

        if action == "Hands":
            dhand: str = data.get('hand')
            hand: Hands = Hands.Etc
            if dhand == "rock":
                hand = Hands.Rock
            elif dhand == "paper":
                hand = Hands.Paper
            elif dhand == "scissors":
                hand = Hands.Scissors
            if room.game.player1.user_info == self.user:
                room.game.player1.hand = hand
            else:
                room.game.player2.hand = hand
            room.game.judgment()
            if room.game.winner:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'game_end',
                    }
                )
                await self.save_game_result()
            elif room.game.player1.hand != Hands.Etc and room.game.player2.hand != Hands.Etc:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'game_state',
                        "message": json.dumps(self.room.game.get_state())
                    }
                )
                room.game.player1.hand = Hands.Etc
                room.game.player2.hand = Hands.Etc

    async def disconnect(self, close_code: Optional[int]) -> None:
        #room: GameRoom = g_manager.get_room(self.user)
        if close_code != 1000:
            if not self.room:
                return
            if self.room.player1 and self.room.player2:
                winner = None
                if self.room.player1 == self.user:
                    winner = self.room.player2
                else:
                    winner = self.room.player1
                if winner:
                    self.room.game.winner = winner
                    await self.save_game_result()
                    if self.room.player1 == self.user:
                        self.room.player1 = None
                    else:
                        self.room.player2 = None
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            'type': 'game_end',
                        }
                    )
            else:
                g_manager.release_room(self.user)

        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def game_state(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_state',
            'message': event["message"],
        }))



    async def game_ready(self, event) -> None:
        room: GameRoom = g_manager.get_room(self.user)
        await self.send(text_data=json.dumps({
            "type": "start_game",
        }))

    async def game_end(self, event) -> None:
        print("game_end:", self.user.name)
        await self.send(text_data=json.dumps({
            'type': 'game_end',
            #'message': event["message"],
        }))
        g_manager.release_room(self.user)


    @database_sync_to_async
    def save_game_result(self):
        from accounts.models import RockPaperScissorsResult
        room: GameRoom = self.room
        game: Game = room.game
        winner: str = game.winner.name
        # winner: str = game.winner.user_info.name
        loser: str = ""
        winner_score: int
        loser_score: int
        if winner == game.player1.user_info.name:
            winner_score = game.player1.score
            loser = game.player2.user_info.name
            loser_score = game.player2.score
        else:
            winner_score = game.player2.score
            loser = game.player1.user_info.name
            loser_score = game.player1.score
        result = RockPaperScissorsResult()
        # print("winner:", winner)
        # print("loser:", loser)
        # print("winner_score:", winner_score)
        # print("loser_score:", loser_score)
        result.record_result(winner, loser, winner_score, loser_score)
        