import django_filters
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authentication import TokenAuthentication

from .models import Blog
from . import serializers


class TitleFilter(django_filters.FilterSet):
    def __init__(self, *args, name=None, **kwargs):
        super().__init__(*args, **kwargs)

    name = django_filters.Filter(field_name='title', lookup_expr='icontains')

    class Meta:
        fields = ('title',)


class TypeFilter(django_filters.FilterSet):
    def __init__(self, *args, type=None, **kwargs):
        super().__init__(*args, **kwargs)

    types = django_filters.Filter(field_name='types__type_name', lookup_expr='iexact')
    subtypes = django_filters.Filter(field_name='subtypes__subtype_name', lookup_expr='iexact')
    tags = django_filters.Filter(field_name='tags__tag_name', lookup_expr='iexact')

    class Meta:
        fields = ('types', 'subtypes', 'tags')


class BlogViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.BlogSerializer
    permission_classes = (AllowAny, )
    queryset = Blog.objects.all()

    def filter_queryset(self, queryset):
        if self.action == 'blogtype':
            self.filterset_class = TypeFilter
        return super().filter_queryset(queryset)

    @action(detail=False)
    def title(self, request):
        queryset = self.filter_queryset(self.get_queryset())[0:20]
        serializer = serializers.BlogTitleSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def blogtype(self, request):
        queryset = self.filter_queryset(self.get_queryset())[0:20]
        serializer = serializers.BlogTitleSerializer(queryset, many=True)
        return Response(serializer.data)