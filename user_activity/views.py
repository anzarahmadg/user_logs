from rest_framework import viewsets, permissions
from .models import UserActivityLog
from .serializers import UserActivityLogSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response


class ActivityLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user activity logs with custom state transition endpoint
    """
    serializer_class = UserActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['action', 'timestamp']
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        """Filter to current user's logs"""
        return UserActivityLog.objects.filter(user=self.request.user)


    def perform_create(self, serializer):
        """Auto-assign current user on create"""
        serializer.save(user=self.request.user)


    @action(detail=True, methods=['patch'], url_path='transition')
    def state_transition(self, request, pk=None):
        """Handle custom state transitions with validation"""
        log = self.get_object()
        new_status = request.data.get('status')
        status_choices = dict(UserActivityLog.STATUS_CHOICES)

        if new_status not in status_choices:
            return Response({"error": f"Invalid status. Valid choices: {list(status_choices.keys())}"},
                            status=400)

        # Check for rules
        transition_rules = {
            'PENDING': ['IN_PROGRESS'],
            'IN_PROGRESS': ['DONE'],
            'DONE': []
        }

        if new_status not in transition_rules[log.status]:
            return Response({
                "error": f"Invalid transition from {log.status} to {new_status}",
                "allowed": transition_rules[log.status]
            }, status=400)

        log.status = new_status
        log.save()

        return Response(self.get_serializer(log).data)
