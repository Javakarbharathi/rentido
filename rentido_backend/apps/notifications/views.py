from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from .models import Notification, NotificationPreference
from .serializers import NotificationSerializer, NotificationPreferenceSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List user notifications",
        parameters=[
            OpenApiParameter(name='is_read', description='Filter by read status (true/false)', required=False, type=bool),
            OpenApiParameter(name='channel', description='Filter by channel (IN_APP, EMAIL, SMS, PUSH)', required=False, type=str),
        ]
    ),
    retrieve=extend_schema(summary="Retrieve notification detail")
)
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Notification.objects.filter(recipient=self.request.user)
        is_read = self.request.query_params.get('is_read')
        channel = self.request.query_params.get('channel')

        if is_read is not None:
            if is_read.lower() in ['true', '1']:
                queryset = queryset.filter(is_read=True)
            elif is_read.lower() in ['false', '0']:
                queryset = queryset.filter(is_read=False)

        if channel:
            queryset = queryset.filter(channel=channel.upper())

        return queryset

    @extend_schema(summary="Mark a specific notification as read")
    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.mark_as_read()
        return Response({"status": "SUCCESS", "message": "Notification marked as read."})

    @extend_schema(summary="Mark all unread notifications as read")
    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        now = timezone.now()
        updated_count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True, read_at=now)
        return Response({
            "status": "SUCCESS",
            "marked_read_count": updated_count
        })

    @extend_schema(summary="Get total unread notifications count")
    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({"unread_count": count})

    @extend_schema(summary="Get or update notification delivery preferences")
    @action(detail=False, methods=['get', 'put', 'patch'], url_path='preferences')
    def preferences(self, request):
        prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)
        if request.method in ['PUT', 'PATCH']:
            serializer = NotificationPreferenceSerializer(
                prefs, data=request.data, partial=(request.method == 'PATCH')
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        serializer = NotificationPreferenceSerializer(prefs)
        return Response(serializer.data)
