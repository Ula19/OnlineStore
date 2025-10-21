from django.db import models
from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget

from .models import Category, Brand, Product



class CustomAdminClass(ModelAdmin):
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        },
    }

@admin.register(Category)
class CategoryAdmin(CustomAdminClass):
    pass


@admin.register(Brand)
class BrandAdmin(CustomAdminClass):
    pass


@admin.register(Product)
class ProductAdmin(CustomAdminClass):
    pass
