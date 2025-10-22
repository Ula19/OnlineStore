from django.views.generic import TemplateView, ListView, DetailView
from django.shortcuts import get_object_or_404
from django.contrib.postgres.search import TrigramSimilarity
from django.core.cache import cache

from .models import Category, Brand, Product
from .forms import SearchForm


class IndexView(ListView):
    template_name = 'index.html'
    context_object_name = 'products'
    extra_context = {'index': True, 'title': 'Главная страница'}

    def get_queryset(self):
        queryset = cache.get_or_set('cashed_products_last_list',
                                    Product.objects.select_related('category').order_by('-create')[:9])

        return queryset


class ProductListView(ListView):
    template_name = 'shop.html'
    context_object_name = 'products'
    paginate_by = 4
    ordering = 'price'

    category = None

    def get_queryset(self):
        """
        ordering - Динамически определяет сортировку
        ...
        """
        # Получаем параметры
        ordering = self.request.GET.get('ordering', self.ordering)
        slug = self.kwargs.get('slug')
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')

        # Создаем уникальный ключ для кэша
        cache_key = f"products_{slug}_{price_min}_{price_max}_{ordering}"

        # Пробуем получить из кэша
        cached_queryset = cache.get(cache_key)
        if cached_queryset is not None:
            return cached_queryset

        # Начинаем с базового queryset
        if slug:
            self.category = get_object_or_404(Category, slug=slug)
            queryset = Product.objects.filter(category=self.category)
        else:
            queryset = Product.objects.all()

        print(f"DEBUG: slug={slug}, price_min={price_min}, price_max={price_max}, ordering={ordering} ||| cashed={cache_key}")

        # Добавляем select_related для оптимизации
        queryset = queryset.select_related('category', 'brand')

        # Применяем фильтрацию по цене
        if price_min and price_max:
            try:
                price_min = float(price_min)
                price_max = float(price_max)
                queryset = queryset.filter(price__gte=price_min, price__lte=price_max)
            except (ValueError, TypeError):
                pass

        # Применяем сортировку
        queryset = queryset.order_by(ordering)

        # Сохраняем в кэш на 5 минут
        cache.set(cache_key, queryset, 300)

        return queryset
    
    def get_paginate_by(self, queryset):
        """Динамически изменяет количество элементов на странице"""
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_context_data(self, *args, **kwargs):
        """
        ...
        """
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Товары'

        context['categories'] = Category.objects.all()
        context['select_category'] = self.kwargs.get('slug')
        context['brands'] = Brand.objects.all()

        context['ordering'] = self.request.GET.get('ordering', self.ordering)

        context['paginate_by'] = self.request.GET.get('paginate_by', self.paginate_by)
        page = context['page_obj']
        context['paginator_range'] = page.paginator.get_elided_page_range(page.number)

        context['shop'] = True

        return context


class ProductDetailView(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'product-details.html'
    extra_context = {'product_detail': True, 'title': 'Детальная информация'}


# class SearchResultView(ListView):
#     """
#     ...
#     """
#     model = Product
#     template_name = 'search_result.html'
#     context_object_name = 'products'
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         form = SearchForm(self.request.GET)
#
#         if 'query' in self.request.GET and form.is_valid():
#             query = form.cleaned_data['query']
#             queryset = Product.objects.filter(name__search=query)
#             # queryset = Product.objects.annotate(
#             #     similarity=TrigramSimilarity('name', query),
#             # ).filter(similarity__gt=0.1).order_by('-similarity')
#         return queryset
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['form'] = SearchForm(self.request.GET)
#
#         if 'query' in self.request.GET:
#             context['query'] = self.request.GET.get('query')
#
#         return context

class SearchResultView(ListView):
    """
    Представление для показа товаров которых пользователь запросил в поле поиска
    Поиск происходит по триграммному сходству
    """
    template_name = 'search_result.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.objects.all()
        form = SearchForm(self.request.GET)

        if 'query' in self.request.GET and form.is_valid():
            query = form.cleaned_data['query']
            # queryset = Product.objects.filter(name__search=query)
            queryset = Product.objects.annotate(
                similarity=TrigramSimilarity('name', query),
            ).filter(similarity__gt=0.1).order_by('-similarity')
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Поиск'

        context['form'] = SearchForm(self.request.GET)

        if 'query' in self.request.GET:
            context['query'] = self.request.GET.get('query')

        # page = context['page_obj']
        # context['paginator_range'] = page.paginator.get_elided_page_range(page.number)

        return context


class CheckoutView(TemplateView):
    template_name = 'checkout.html'
    extra_context = {'checkout': True}


class CartView(TemplateView):
    template_name = 'cart.html'
    extra_context = {'cart': True}
