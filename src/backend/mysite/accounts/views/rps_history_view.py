from rest_framework.permissions import IsAuthenticated
from ..models import RockPaperScissorsResult
from rest_framework.authentication import TokenAuthentication
from django.views.decorators.http import require_GET
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from django.http import JsonResponse

@require_GET
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_user_rps_results(request):
    user = request.user

    # userのgameの結果を取得
    game_results = RockPaperScissorsResult.get_results_by_username(user.name)

    # 結果を辞書形式に変換
    results_list = [
        {
            "winner": result.winner,
            "loser": result.loser,
            "date_time": result.date_time,
            "winner_score": result.winner_score,
            "loser_score": result.loser_score
        }
        for result in game_results
    ]
    # JSON形式でレスポンスを返す
    return JsonResponse({"results": results_list}, safe=False)
