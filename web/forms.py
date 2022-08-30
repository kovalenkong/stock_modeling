import json
from decimal import Decimal

from django import forms

from core.models import Algorithm


class ClassicModelForm(forms.Form):
    model_type = forms.ChoiceField(choices=[
        ('frz', 'ФРЗ'),
        ('fiv', 'ФИВ'),
        ('min_max', 'Минимум-Максимум'),
    ], label='Тип модели')


class DatasetForm(forms.Form):
    order_costs = forms.DecimalField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control bg-dark text-light',
            'id': 'orderCosts',
            'placeholder': 'параметр A'
        }),
        label='Затраты на пополнение'
    )
    storage_costs = forms.DecimalField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control bg-dark text-light',
            'id': 'storageCosts',
            'placeholder': 'параметр I'
        }),
        label='Затраты на хранение'
    )
    delivery_time = forms.DecimalField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'id': 'deliveryTime',
            'class': 'form-control bg-dark text-light',
            'placeholder': 'в днях'
        }),
        label='Время доставки'
    )
    delay_time = forms.DecimalField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'id': 'delayTime',
            'class': 'form-control bg-dark text-light',
            'placeholder': 'в днях'
        }),
        label='Время возможной задержки'
    )
    delay_probability = forms.DecimalField(
        min_value=0,
        max_value=1,
        widget=forms.NumberInput(attrs={
            'id': 'delayProbability',
            'type': 'range',
            'class': 'form-range bg-dark text-light',
            'value': 0,
            'step': 0.01
        }),
        label='Вероятность задержки',
        required=False
    )
    delay_days = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'delayDays',
            'class': 'form-control bg-dark text-light',
            'pattern': '[0-9,]*',
            'autocomplete': 'off',
            'placeholder': 'через запятую',
        }),
        label='Задержка поставок',
        required=False
    )
    initial_stock = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'id': 'initialStock',
            'class': 'form-control bg-dark text-light',
            'placeholder': 'любое значение'
        }),
        label='Начальный запас',
        required=False
    )
    deficit_losses = forms.DecimalField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'id': 'deficitLosses',
            'class': 'form-control bg-dark text-light',
            'placeholder': '>=0'
        }),
        label='Потери от дефицита',
        required=False
    )
    avg_daily_consumption = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'id': 'avgDailyConsumption',
            'class': 'form-control bg-dark text-light',
            'placeholder': 'отгрузка'
        }),
        label='Среднесуточное потребление',
        required=False
    )
    avg_daily_consumption_d = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'id': 'avgDailyConsumptionD',
            'class': 'form-control bg-dark text-light',
            'placeholder': 'оприходование'
        }),
        label='Среднесуточное поступление',
        required=False
    )
    consumption = forms.CharField(
        widget=forms.Textarea(attrs={
            'id': 'consumptionDataset',
            'class': 'form-control bg-dark text-light',
            'placeholder': '123.45\n67\n234.67'
        }),
        label='Потребление',
        required=True
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'id': 'description',
            'class': 'form-control bg-dark text-light',
            'rows': 2,
        }),
        label='Описание',
        required=False
    )
    is_public = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'id': 'isPublic',
            'class': 'form-checkbox bg-dark text-light'
        }),
        label='Публичный',
        required=False
    )

    def __init__(self, *args, **kwargs):
        skip_required = kwargs.pop('skip_required', False)
        super().__init__(*args, **kwargs)
        if skip_required:
            for field in self.fields:
                if field == 'consumption':
                    continue
                self.fields[field].required = False

    def parameters_to_json(self):
        self.is_valid()
        data = self.cleaned_data
        res = {}
        for field in self.fields:
            if field not in ('consumption', 'description', 'is_public'):
                value = data[field]
                if isinstance(value, Decimal):
                    value = float(value)
                res[field] = value
        return json.dumps(res)


class AlgorithmForm(forms.ModelForm):
    class Meta:
        _common_attrs = {
            'class': 'form-control bg-dark text-light',
            'spellcheck': 'false',
            'rows': 2,
        }
        model = Algorithm
        fields = [
            'formula_point_refill',
            'formula_order_size',
            'formula_score',
        ]
        widgets = {
            'formula_point_refill': forms.Textarea(attrs={'id': 'formulaPointRefill', **_common_attrs}),
            'formula_order_size': forms.Textarea(attrs={'id': 'formulaOrderSize', **_common_attrs}),
            'formula_score': forms.Textarea(attrs={'id': 'formulaScore', **_common_attrs}),
        }
        labels = {
            'formula_point_refill': 'Формула нахождения точки пополнения заказа',
            'formula_order_size': 'Формула размера заказа',
            'formula_score': 'Оценивающая функция',
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if request is not None:
            if (
                    self.instance is not None and not request.user.is_authenticated
            ) or (
                    request.user.is_authenticated and request.user != self.instance.author
            ):
                for field in self.fields:
                    self.fields[field].disabled = True
