from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..serializers.delete_user_serializer import DeleteUserSerializer
from .login_view import get_first_error_message

class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        # 認証されたユーザーを取得
        user = request.user
        serializer = DeleteUserSerializer(instance=user,data=request.data)
        #serializer.is_valid(raise_exception=True)
        if not serializer.is_valid():
            err_message = get_first_error_message(serializer.errors)
            # バリデーションエラーの詳細を含むレスポンスを返す
            return Response({"error": err_message}, status=status.HTTP_400_BAD_REQUEST)

        # ユーザーを削除
        user.delete()
        return Response({"message": "ユーザーが正常に削除されました"}, status=status.HTTP_204_NO_CONTENT)