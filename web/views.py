from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import markdown
from markdown.extensions import fenced_code
from core.stock_models.author import DOC
from core.models import Dataset, Algorithm
from web.forms import ClassicModelForm
from django.db import models

"""
/ - стартовая страница
/models/classic/ - классические модели
/models/author/ - список авторских моделей
/models/author/new/ - новая модель
/models/author/<int:pk>/ - авторская модель
/datasets/ - список датасетов
"""
def test(request):
    return render(request, 'web/test.html')


def index(request):
    author_docs = markdown.markdown(DOC, extensions=[fenced_code.FencedCodeExtension()])
    return render(request, 'web/index.html', {'author_docs': author_docs})


def models_classic(request):
    context = {
        'is_classic': True,
    }
    return render(request, 'web/models/classic.html', context)


def models_author_list(request):
    algo = Algorithm.objects.filter(models.Q(is_public=True) | models.Q(author=request.user)).order_by('-dt_edited')
    return render(request, 'web/models/author_list.html', {'algo': algo})


@login_required
def models_author_new(request):
    author_docs = markdown.markdown(DOC, extensions=[fenced_code.FencedCodeExtension()])
    context = {
        'author_docs': author_docs,
    }
    return render(request, 'web/models/author_new.html', context)


def models_author_view(request, pk):
    return render(request, 'web/models/author_view.html')


def datasets_list(request):
    datasets = Dataset.objects.filter(models.Q(is_public=True) | models.Q(author=request.user)).order_by('-dt_edited')
    return render(request, 'web/datasets/list.html', {'datasets': datasets})
