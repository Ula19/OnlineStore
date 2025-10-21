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
        ordering = self.request.GET.get('ordering', self.ordering)
        queryset = cache.get_or_set('cashed_product_list', Product.objects.select_related('category', 'brand').order_by(ordering))
        slug = self.kwargs.get('slug')
        if slug:
            self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
            queryset = cache.get_or_set('cashed_product_list_by_category',
                                        Product.objects.filter(category=self.category).order_by(ordering), 100)
            # queryset = Product.objects.filter(category=self.category).order_by(ordering)
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
