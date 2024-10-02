from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..serializers.avatar_serializer import AvatarSerializer

class GetAvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = AvatarSerializer(user)
        return Response(serializer.data)