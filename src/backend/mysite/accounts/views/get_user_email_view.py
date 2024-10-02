from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..serializers.get_user_email_serializer import UserEmailSerializer

class GetUserEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserEmailSerializer(user)
        return Response(serializer.data)