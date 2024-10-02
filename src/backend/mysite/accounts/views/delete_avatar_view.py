from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import os
from django.conf import settings

class DeleteAvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        if user.avatar:
            avatar_path = user.avatar.path  # ファイルパスを取得
            user.avatar.delete()  # avatarフィールドを削除
            if os.path.exists(avatar_path):  # ファイルが存在する場合削除
                os.remove(avatar_path)
            return Response({"message": "アバターが削除されました。"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "アバターが設定されていません。"}, status=status.HTTP_400_BAD_REQUEST)