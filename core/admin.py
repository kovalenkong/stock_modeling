from django.contrib import admin

from .models import Algorithm, Dataset, User

admin.site.register(Dataset)
admin.site.register(Algorithm)
