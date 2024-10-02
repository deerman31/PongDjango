import uuid
from typing import Dict, List

class RoomManager:
    def __init__(self):
        self.active_rooms: Dict[str, List] = {}
        self.games: Dict[str, Game] = {}

    def assign_room(self, user):
        for room, players in self.active_rooms.items():
            if len(players) < 2:
                players.append(user)
                return room
        new_room = str(uuid.uuid4())
        self.active_rooms[new_room]= [user]
        return new_room

    def release_room(self, room, user):
        if user in self.active_rooms[room]:
            self.active_rooms[room].remove(user)
        if not self.active_rooms[room]:
            del self.active_rooms[room]
            del self.games[room]

    def get_or_create_game(self, room, user):
        if room not in self.games:
            self.games[room] = Game(user, None)
        else:
            self.games[room].update_player2(user)
        return self.games[room]
    
    def get_game(self, room):
        if room in self.games:
            return self.games[room]
        return None


class Paddle:
    def __init__(self, x_position, y_position, height, speed):
        self.x = x_position
        self.y = y_position
        self.height = height
        self.speed = speed

    def move_up(self):
        self.y = max(self.y - self.speed, 0)

    def move_down(self, boundary):
        self.y = min(self.y + self.speed, boundary - self.height)


class Ball:
    def __init__(self, x_position=400, y_position=300, radius=10, speed=4):
        self.x = x_position
        self.y = y_position
        self.dx = speed
        self.dy = speed
        self.radius = radius

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def bounce_vertical(self):
        self.dy = -self.dy

    def bounce_horizontal(self):
        self.dx = -self.dx

    def reset(self):
        self.x = 400
        self.y = 300
        self.dx = -self.dx
        self.dy = -self.dy


class Player:
    def __init__(self, user, x_position, y_position=250, height=100, speed=20):
        self.user = user
        self.score = 0
        self.paddle = Paddle(x_position, y_position, height, speed)
        self.connected = False  # ここでconnected属性を追加

    def add_score(self):
        print(self.user.name, ": add_score")
        self.score += 1


class Game:
    def __init__(self, player1, player2):
        self.players = {
            1: Player(player1, 10),
            2: Player(player2, 760)
        }
        self.ball = Ball()
        self.max_score = 10
        self.started = False
        self.winner = None
        self.result_saved = False  # 勝敗が記録されたことをマーク

    def update_player2(self, player2):
        self.players[2].user = player2
        self.players[2].connected = True

    def check_winner(self):
        if self.players[1].score >= self.max_score:
            self.winner = 1
        elif self.players[2].score >= self.max_score:
            self.winner = 2
    
    def start(self):
        #print("Game start")
        self.started = True

    def stop(self):
        #print("Game stop")
        self.started = False

    def reset(self):
        for player in self.players.values():
            player.score = 0
        self.ball.reset()
        self.started = False
        self.winner = None

    def move_ball(self):
        """ボールの動きと衝突判定"""
        if not self.started:
            return

        self.ball.move()

        # 上下の壁でボールが跳ね返る
        if self.ball.y <= 0 or self.ball.y >= 580:
            self.ball.bounce_vertical()

        # プレイヤーパドルとの衝突判定
        if (self.ball.dx < 0 and self.ball.x <= self.players[1].paddle.x + 10 and
            self.players[1].paddle.y <= self.ball.y <= self.players[1].paddle.y + self.players[1].paddle.height):
            self.ball.bounce_horizontal()
        elif (self.ball.dx > 0 and self.ball.x >= self.players[2].paddle.x - 10 and
            self.players[2].paddle.y <= self.ball.y <= self.players[2].paddle.y + self.players[2].paddle.height):
            self.ball.bounce_horizontal()

        # ボールが左側の壁を通過したら右側のプレイヤーの得点
        elif self.ball.x <= 0:
            self.players[2].add_score()
            self.ball.reset()

        # ボールが右側の壁を通過したら左側のプレイヤーの得点
        elif self.ball.x >= 800:
            self.players[1].add_score()
            self.ball.reset()

    def is_game_over(self):
        """どちらかのプレイヤーが最大スコアに達したらゲームオーバー"""
        return any(player.score >= self.max_score for player in self.players.values())

    def get_winner(self):
        if self.players[1].score >= self.max_score:
            return self.players[1].user.name
        elif self.players[2].score >= self.max_score:
            return self.players[2].user.name
        return None

    def get_game_result(self):
        if self.get_winner() == self.players[1].user.name:
            winner = self.players[1].user.name
            loser = self.players[2].user.name
        else:
            winner = self.players[2].user.name
            loser = self.players[1].user.name
        win_score = max(self.players[1].score, self.players[2].score)
        lose_score = min(self.players[1].score, self.players[2].score)
        return winner, loser, win_score, lose_score

    def get_state(self):
        return {
            'ball_x': self.ball.x,
            'ball_y': self.ball.y,
            'player_1_y': self.players[1].paddle.y,
            'player_2_y': self.players[2].paddle.y,
            'score_1': self.players[1].score,
            'score_2': self.players[2].score,
            'game_over': self.is_game_over()
        }