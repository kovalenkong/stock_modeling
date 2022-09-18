import collections

import numpy as np
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from core.models import Algorithm, Dataset
from core.stock_models import author
from core.stock_models.builders import (build_fiv, build_fixed_period,
                                        build_frz, build_minimum_maximum)
from core.stock_models.config import MODEL_TYPE, Config
from core.stock_models.errors import ConfigError
from .business_logic import prepare_response

from .permissions import IsAuthorOrReadOnly
from .serializers import (AlgorithmSerializer, AuthorModelSerializer,
                          ClassicModelSerializer, DatasetDetailSerializer,
                          DatasetListSerializer)

_model_factory = {
    MODEL_TYPE.FRZ.value: build_frz,
    MODEL_TYPE.FIV.value: build_fiv,
    MODEL_TYPE.MIN_MAX.value: build_minimum_maximum,
    MODEL_TYPE.FIXED_PERIOD.value: build_fixed_period,
}


@csrf_exempt
@api_view(['POST'])
@parser_classes([JSONParser])
def build_classic_model(request):
    data = request.data
    serializer = ClassicModelSerializer(data=data)
    if not serializer.is_valid():
        return Response(data=serializer.errors, status=400)

    data: collections.OrderedDict = serializer.validated_data

    delay_probability = data.get('delay_probability', 0)
    delay_days = data.get('delay_days')
    delay = delay_days or delay_probability

    model_type = data['model_type']
    try:
        config = Config(
            consumption=np.array(data['consumption']),
            order_costs=data['order_costs'],
            storage_costs=data['storage_costs'],
            delivery_time=data['delivery_time'],
            delay_time=data['delay_time'],
            initial_stock=data['initial_stock'],
            modification=data['modification'],
            delay=delay,

            deficit_losses=data.get('deficit_losses'),
            s=data.get('s'),
            d=data.get('d'),
        )
        model = _model_factory[model_type](config)
    except ConfigError as e:
        return Response(data={'error': str(e)}, status=400)
    except Exception as e:
        return Response(data={'error': str(e)}, status=500)

    return Response(prepare_response(model))


@csrf_exempt
@api_view(['POST'])
@parser_classes([JSONParser])
def build_author_model(request):
    data = request.data
    serializer = AuthorModelSerializer(data=data)
    if not serializer.is_valid():
        return Response(data=serializer.errors, status=400)

    data: collections.OrderedDict = serializer.validated_data

    delay_probability = data.get('delay_probability', 0)
    delay_days = data.get('delay_days')
    delay = delay_days or delay_probability

    try:
        config = author.Config(
            consumption=np.array(data['consumption']),
            order_costs=data['order_costs'],
            storage_costs=data['storage_costs'],
            delivery_time=data['delivery_time'],
            delay_time=data['delay_time'],
            initial_stock=data['initial_stock'],
            delay=delay,
            formula_point_refill=data['formula_point_refill'],
            formula_order_size=data['formula_order_size'],
            formula_score=data.get('formula_score'),
        )
        model = author.build_author_model(config)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    return Response(prepare_response(model))


class DatasetView(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            f = models.Q(is_public=True) | models.Q(author=self.request.user)
        else:
            f = models.Q(is_public=True)
        return Dataset.objects.filter(f).order_by('dt_edited')

    def get_serializer_class(self):
        if self.action == 'list':
            return DatasetListSerializer
        return DatasetDetailSerializer


class AlgorithmView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    serializer_class = AlgorithmSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        user = self.request.user if self.request.user.is_authenticated else None
        return Algorithm.objects.filter(models.Q(is_public=True) | models.Q(author=user))
