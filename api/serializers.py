import json

from rest_framework import serializers

from core.models import Dataset, User
from core.stock_models.config import MODEL_TYPE, MODIFICATION


class _CommonSerializer(serializers.Serializer):
    consumption = serializers.ListField()
    order_costs = serializers.FloatField(min_value=0)
    storage_costs = serializers.FloatField(min_value=0)
    delivery_time = serializers.IntegerField(min_value=0)
    delay_time = serializers.IntegerField(min_value=0)
    initial_stock = serializers.FloatField()
    delay_probability = serializers.FloatField(required=False, min_value=0, max_value=1, default=0)
    delay_days = serializers.ListField(required=False)
    # optional
    deficit_losses = serializers.FloatField(required=False, min_value=0)
    s = serializers.FloatField(required=False, min_value=0, help_text='Среднесуточное потребление (отгрузка)')
    d = serializers.FloatField(required=False, min_value=0, help_text='Среднесуточное потребление (оприходование)')


class ClassicModelSerializer(_CommonSerializer):
    model_type = serializers.ChoiceField(['frz', 'fiv', 'min_max', 'fixed_period'])  # todo
    modification = serializers.ChoiceField(['classic', 'lost_sales', 'gradual_replenishment'])  # todo


class AuthorModelSerializer(_CommonSerializer):
    formula_point_refill = serializers.CharField()
    formula_order_size = serializers.CharField()
    formula_score = serializers.CharField(required=False)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('date_joined', 'email', 'id', 'first_name', 'last_name')


class DatasetListSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    parameters = serializers.JSONField()

    class Meta:
        model = Dataset
        exclude = ('data',)


class DatasetDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    parameters = serializers.JSONField

    class Meta:
        model = Dataset
        fields = '__all__'
