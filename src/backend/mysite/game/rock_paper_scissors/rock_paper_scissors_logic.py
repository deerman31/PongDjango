from enum import Enum

class Hands(Enum):
    Rock = "rock",
    Paper = "paper",
    Scissors = "scissors",
    Etc = "etc",
    
class Player:
    def __init__(self, player):
        self.user_info = player
        self.score: int = 0
        self.hand: Hands = Hands.Etc

class Game:
    def __init__(self, player1, player2):
        self.player1: Player = Player(player1)
        self.player2: Player = Player(player2)
        self.max_score: int = 3
        self.winner = None
    
    def judgment(self):
        if self.player1.hand != Hands.Etc and self.player2.hand != Hands.Etc:
            outcomes = {
                (Hands.Rock, Hands.Scissors): self.player1,
                (Hands.Scissors, Hands.Paper): self.player1,
                (Hands.Paper, Hands.Rock): self.player1,
                (Hands.Rock, Hands.Paper): self.player2,
                (Hands.Scissors, Hands.Rock): self.player2,
                (Hands.Paper, Hands.Scissors): self.player2,
            }
            # あいこ
            if self.player1.hand == self.player2.hand:
                return
            # 辞書で勝敗を判定し、winnerにplayer1もしくは、player2を代入
            winner = outcomes.get((self.player1.hand, self.player2.hand))
            if winner:
                winner.score += 1
            # ここでscoreが勝利条件に達したら、winnerにplayerの情報を代入
            if self.player1.score == self.max_score:
                self.winner = self.player1.user_info
            elif self.player2.score == self.max_score:
                self.winner = self.player2.user_info
                
    def get_state(self):
        hand1: str = ""
        if self.player1.hand == Hands.Rock:
            hand1 = "rock"
        elif self.player1.hand == Hands.Paper:
            hand1 = "paper"
        elif self.player1.hand == Hands.Scissors:
            hand1 = "scissors"

        hand2: str = ""
        if self.player2.hand == Hands.Rock:
            hand2 = "rock"
        elif self.player2.hand == Hands.Paper:
            hand2 = "paper"
        elif self.player2.hand == Hands.Scissors:
            hand2 = "scissors"

        return {
            'player1': self.player1.user_info.name,
            'player1_score': self.player1.score,
            'player1_hand': hand1,
            'player2': self.player2.user_info.name,
            'player2_score': self.player2.score,
            'player2_hand': hand2,
        }
