from rest_framework import serializers
from .models import UserActivityLog

class UserActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivityLog
        fields = '__all__'
        read_only_fields = ['user', 'timestamp']

    def validate_status(self, value):
        instance = self.instance
        if not instance:
            return value

        current_status = instance.status

        valid_transitions = {
            'PENDING': ['IN_PROGRESS'],
            'IN_PROGRESS': ['DONE'],
            'DONE': []
        }

        if value == current_status:
            return value

        if value not in valid_transitions[current_status]:
            raise serializers.ValidationError(
                f"Invalid status transition from {current_status} to {value}. "
                f"Allowed: {', '.join(valid_transitions[current_status])}"
            )

        return value

