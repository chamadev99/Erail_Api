from rest_framework import serializers

class TraiSerializers(serializers.Serializer):
    train_number_or_name = serializers.CharField()
    train_up_or_down = serializers.CharField()
    station_name_code = serializers.CharField()
    place_id = serializers.CharField()
    arrival_time = serializers.TimeField()
    departure_time = serializers.TimeField()
    stop_time = serializers.TimeField()
    frequency = serializers.CharField()
