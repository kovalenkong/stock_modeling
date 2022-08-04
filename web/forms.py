from django import forms


class ClassicModelForm(forms.Form):
    model_type = forms.ChoiceField(choices=[
        ('frz', 'ФРЗ'),
        ('fiv', 'ФИВ'),
        ('min_max', 'Минимум-Максимум'),
    ], label='Тип модели')
