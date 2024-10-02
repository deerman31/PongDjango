from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..serializers.update_name_serializer import UpdateNameSerializer
from .login_view import get_first_error_message

class UpdateNameView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = UpdateNameSerializer(user, data=request.data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "名前が更新されました。"}, status=status.HTTP_200_OK)
        err_message = get_first_error_message(serializer.errors)
        return Response({"error": err_message}, status=status.HTTP_400_BAD_REQUEST)