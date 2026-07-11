from .models import ChatRoomParticipant, ChatMessage

def unread_chat_count(request):
    if not request.user.is_authenticated:
        return {}

    participants = ChatRoomParticipant.objects.filter(
        user_id=request.user.id
    )

    chatroom_ids = [p.chatroom_id for p in participants]

    unread_count = 0
    for msg in ChatMessage.objects.all():
        if (
            msg.chatroom_id in chatroom_ids and
            not msg.is_read and
            msg.sender_id != request.user.id
        ):
            unread_count += 1

    return {
        "unread_count": unread_count
    }
