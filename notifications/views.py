from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Notification


@login_required
def notifications_list(request):
    """Page liste des notifications."""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:50]
    # Mark all as read when page is opened
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return render(request, 'notifications/list.html', {'notifications': notifications})


@login_required
def notifications_api(request):
    """
    AJAX endpoint — polled every 10s.
    Returns unread count + last 8 notifications.
    """
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    notifs = list(
        Notification.objects.filter(recipient=request.user)
        .order_by('-created_at')[:8]
        .values('id', 'notif_type', 'title', 'body', 'link', 'is_read', 'created_at')
    )
    # Serialize datetime
    for n in notifs:
        n['created_at'] = n['created_at'].strftime('%d/%m/%Y %H:%M')
    return JsonResponse({'unread_count': unread_count, 'notifications': notifs})


@login_required
@require_POST
def mark_read(request, pk):
    """Mark a single notification as read."""
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save(update_fields=['is_read'])
    return JsonResponse({'ok': True})


@login_required
@require_POST
def mark_all_read(request):
    """Mark all notifications as read."""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'ok': True})
