from rest_framework import serializers


class RouteAnalysisSerializer(serializers.Serializer):
    origin = serializers.CharField(min_length=2, max_length=255)
    destination = serializers.CharField(min_length=2, max_length=255)
    departure_time = serializers.DateTimeField()
    load_weight = serializers.FloatField(min_value=0)
    checkpoint_interval = serializers.ChoiceField(choices=[10, 25, 50], default=25)
