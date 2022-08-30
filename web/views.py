import json
from decimal import Decimal

import markdown
from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from markdown.extensions import fenced_code, tables

from core.models import Algorithm, Dataset
from core.stock_models import SHORT_DOC, LONG_DOC
from web.forms import AlgorithmForm, ClassicModelForm, DatasetForm

"""
/ - стартовая страница
/models/classic/ - классические модели
/models/author/ - список авторских моделей
/models/author/new/ - новая модель
/models/author/<int:pk>/ - авторская модель
/datasets/ - список датасетов
"""


def test(request):
    return render(request, 'web/test.html', {'docs': LONG_DOC})


def index(request):
    author_docs = markdown.markdown(SHORT_DOC, extensions=[fenced_code.FencedCodeExtension()])
    return render(request, 'web/index.html', {'author_docs': author_docs})


def models_classic(request):
    context = {
        'is_classic': True,
    }
    return render(request, 'web/models/classic.html', context)


def models_author_list(request):
    user = request.user if request.user.is_authenticated else None
    filters = models.Q(is_public=True) | models.Q(author=user)

    q = request.GET.get('q')
    if q:
        filters &= models.Q(description__icontains=q) | models.Q(formula_point_refill__icontains=q) | models.Q(
            formula_order_size__icontains=q) | models.Q(author__email__icontains=q)
    algo = Algorithm.objects.filter(filters).order_by('-id')
    return render(request, 'web/models/author_list.html', {'algo': algo, 'q': q})


@login_required
def models_author_new(request):
    author_docs = markdown.markdown(SHORT_DOC, extensions=[fenced_code.FencedCodeExtension(), tables.TableExtension()])
    form_algo = AlgorithmForm()
    form_dataset = DatasetForm()
    context = {
        'author_docs': author_docs,
        'form_algo': form_algo,
        'form_dataset': form_dataset,
        'can_save_algo': True,
    }
    return render(request, 'web/models/author_view.html', context)


def models_author_view(request, pk):
    author_docs = markdown.markdown(SHORT_DOC, extensions=[fenced_code.FencedCodeExtension()])
    user = request.user if request.user.is_authenticated else None
    algo = get_object_or_404(Algorithm, models.Q(author=user) | models.Q(is_public=True), pk=pk)
    form = AlgorithmForm(instance=algo, request=request)
    context = {
        'author_docs': author_docs,
        'form_algo': form,
        'can_save_algo': user == algo.author,
    }
    return render(request, 'web/models/author_view.html', context)


def datasets_list(request):
    user = request.user if request.user.is_authenticated else None
    filters = models.Q(is_public=True) | models.Q(author=user)
    q = request.GET.get('q')
    if q:
        filters &= models.Q(description__icontains=q) | models.Q(author__email__icontains=q)
    datasets = Dataset.objects.filter(filters).order_by('-dt_edited', '-id')
    return render(request, 'web/datasets/list.html', {'datasets': datasets, 'q': q})


@login_required
def datasets_new(request):
    form = DatasetForm(request.POST or None, skip_required=True)
    if request.method == 'GET':
        return render(request, 'web/datasets/new.html', {'form': form})
    parameters = form.parameters_to_json()
    data = form.cleaned_data
    Dataset.objects.create(
        data=data['consumption'],
        author=request.user,
        description=data['description'],
        parameters=parameters,
        is_public=data['is_public'],
    ).save()
    return redirect('datasets_list')


@login_required
def datasets_edit(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk, author=request.user)
    if request.method == 'POST':
        form = DatasetForm(request.POST, skip_required=True)
        parameters = form.parameters_to_json()
        data = form.cleaned_data
        dataset.data = data['consumption']
        dataset.is_public = data['is_public']
        dataset.parameters = parameters
        dataset.description = data['description']
        dataset.save()
        return redirect('datasets_list')
    data = {
        'consumption': dataset.data,
        'description': dataset.description,
        'is_public': dataset.is_public,
    }
    try:
        parameters = json.loads(dataset.parameters)
        data.update(parameters)
    except json.JSONDecodeError:
        pass
    form = DatasetForm(data, skip_required=True)
    return render(request, 'web/datasets/new.html', {'form': form})


def docs(request):
    context = {
        'docs': markdown.markdown(LONG_DOC, extensions=[fenced_code.FencedCodeExtension(), tables.TableExtension()])
    }
    return render(request, 'web/docs/docs.html', context)
