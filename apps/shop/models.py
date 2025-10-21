from django.db import models
from django.urls import reverse
from django.core.validators import FileExtensionValidator

from uuslug import uuslug


class Brand(models.Model):
    """Модель названия бренда товара

    Задачи по оптимизации:
    1) Добавить Hash Index
    """

    name = models.CharField(verbose_name='Названии бренда', max_length=150, unique=True)
    slug = models.SlugField(verbose_name='URL бренда', max_length=150, editable=False, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Название бренда'
        verbose_name_plural = 'Название брендов'
        indexes = [
            models.Index(fields=['name'])
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = uuslug(self.name, instance=self)
        super().save(*args, **kwargs)

    # def get_absolute_url(self):


class Category(models.Model):
    """Модель категории товара

    Задачи по оптимизации:
    1) Добавить Hash Index
    """

    name = models.CharField(verbose_name='Названии категории', max_length=150, unique=True)
    slug = models.SlugField(verbose_name='URL категории', max_length=150, editable=False, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        indexes = [
            models.Index(fields=['name'])
        ]


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = uuslug(self.name, instance=self)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_list_by_category', kwargs={'slug': self.slug})


class Product(models.Model):
    """Модель товаров"""

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name='Бренд')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')

    name = models.CharField(verbose_name='Название', max_length=255, unique=True)
    slug = models.SlugField(verbose_name='URL товара', max_length=255, editable=False, unique=True)
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(verbose_name='Цена', max_digits=10, decimal_places=2)
    count = models.IntegerField(verbose_name='Количество в наличии', default=1)
    available = models.BooleanField(verbose_name='Активный товар', default=True)
    create = models.DateTimeField(verbose_name='Время создания', auto_now_add=True)
    update = models.DateTimeField(verbose_name='Время обновления', auto_now=True)
    image = models.ImageField(verbose_name='Изображение товара',
                              default='images/default.jpg',
                              upload_to='products/',
                              validators=[FileExtensionValidator(allowed_extensions=('jpg', 'jpeg', 'webp',))],
                              blank=True)

    class Meta:
        ordering = ['available', '-count', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['-create']),
            # models.Index(fields=['brand__name', 'category__name']),
            models.Index(fields=['price', 'count']),
        ]
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = uuslug(self.name, instance=self)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})
