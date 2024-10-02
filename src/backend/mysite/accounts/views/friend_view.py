from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

User = get_user_model()

def query_check(query):
    if query:
        if not query.isalnum() or len(query) < 3 or len(query) > 15:
            return False
        return True
    return False

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    query = request.GET.get('q', '')
    #if query:
    if query_check(query):
        users = User.objects.filter(
            Q(name__icontains=query) | Q(email__icontains=query)
        ).exclude(id=request.user.id).exclude(
            id__in=request.user.friends.all()
        ).exclude(
            id__in=request.user.friend_requests_sent.all()
        )
        results = [{'id': user.id, 'name': user.name, 'email': user.email} for user in users]
    else:
        results = []
    return Response(results)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_friend_request(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user not in request.user.friend_requests_sent.all() and user not in request.user.friends.all():
        request.user.friend_requests_sent.add(user)
        return Response({'status': 'ok'})
    return Response({'status': 'already_sent_or_friend'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_friend_request(request, user_id, action):
    user = get_object_or_404(User, id=user_id)
    if action == 'accept':
        request.user.friends.add(user)
        user.friends.add(request.user)
    request.user.friend_requests_received.remove(user)
    return Response({'status': 'ok'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def friend_list(request):
    friends = request.user.friends.all()
    # results = [{'id': friend.id, 'name': friend.name, 'email': friend.email} for friend in friends]
    results = [{'id': friend.id, 'name': friend.name, 'email': friend.email, 'is_online': friend.is_online} for friend in friends]
    return Response(results)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def friend_requests_list(request):
    requests = request.user.friend_requests_received.all()
    results = [{'id': user.id, 'name': user.name, 'email': user.email} for user in requests]
    return Response(results)
