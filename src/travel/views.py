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

from .models import Travel, Rating, Place
from . import serializers

class NameFilter(django_filters.FilterSet):
    def __init__(self, *args, name=None, **kwargs):
        super().__init__(*args, **kwargs)
    name = django_filters.Filter(field_name='name', lookup_expr='icontains')
    class Meta:
        fields = ['name']


class RegionFilter(django_filters.FilterSet):
    def __init__(self, *args, region=None, **kwargs):
        super().__init__(*args, **kwargs)
    region = django_filters.Filter(field_name='region', lookup_expr='icontains')
    class Meta:
        fields = ['region']


class PlaceFilter(NameFilter, RegionFilter):
    class Meta:
        models = Place
        fields = ['name', 'region']


class TravelViewSet(viewsets.ModelViewSet):
    queryset= Travel.objects.all()
    serializer_class = serializers.TravelSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    @action(methods=['POST'], detail=True)
    def rate_travel(self,request,pk=None):
      if 'stars' in request.data:
        travel=Travel.objects.get(id=pk)
        stars = request.data['stars']
        comments = request.data['comments']
        user = request.user
        try:
          rating = Rating.objects.get(user=user.id,travel=travel.id)
          rating.stars = stars
          rating.comments = comments 
          rating.save()

          serializer = RatingSerializer(rating, many=False)
          response = {'message':'rating has been updated', 'result':serializer.data}
          return Response(response, status=status.HTTP_200_OK)

        except:
          rating =Rating.objects.create(user=user,travel=travel,stars=stars,comments=comments)
          serializer = RatingSerializer(rating,many=false)
          response = {'message':'rating created','result': serializer.data}
          return Response(response, status=status.HTTP_200_OK)
      
      else:
        response = {'message':'Please enter stars for the rating'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = serializers.RatingSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    def delete(self,request,*args,**kwargs):
      response = {'message':'Rating cannot be updated like this'}
      return Response(response, status = status.HTTP_400_BAD_REQUEST)

    def create(self,request,*args,**kwargs):
      response = {'message':'Rating cannot be created like this'}
      return Response(response, status = status.HTTP_400_BAD_REQUEST)

class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filterset_class  = PlaceFilter
    lookup_field='json_d'

    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action == 'list':
            return serializers.PlaceSerializer
        if hasattr(self, 'action') and self.action == 'retrieve':
            return serializers.PlacePositionSerializer

    def filter_queryset(self, queryset):
        if self.action == 'list':
            self.filterset_class = PlaceFilter
        elif self.action == 'position':
            self.filterset_class = RegionFilter
        return super().filter_queryset(queryset)

    @action(detail=False)
    def position(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = serializers.PlacePositionSerializer(queryset, many=True)
        return Response(serializer.data)

