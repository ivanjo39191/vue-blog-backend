from django.db import models
from django.contrib.auth.models import User
from model_utils.models import TimeStampedModel
from ckeditor_uploader.fields import RichTextUploadingField  #導入富文本套件

from core import helpers

__all__ = ('Blog', 'BlogType', 'BlogSubtype', 'BlogTag')


# Create your models here.
class BlogType(TimeStampedModel):
    type_name = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.type_name

    class Meta:
        ordering = ['type_name']


class BlogSubtype(TimeStampedModel):
    type = models.ForeignKey(BlogType, on_delete=models.CASCADE, null=True, related_name='subtype_set')
    subtype_name = models.CharField(max_length=200, null=True)

    def __str__(self):
        return f'{self.type} / {self.subtype_name}'

    class Meta:
        ordering = ['type']


class BlogTag(TimeStampedModel):
    tag_name = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.tag_name

    class Meta:
        ordering = ['tag_name']


class Blog(TimeStampedModel):

    title = models.CharField(max_length=200, null=True)
    content = RichTextUploadingField()  #改為RichTextField
    types = models.ManyToManyField(BlogType, blank=True, related_name='blog_set')
    subtypes = models.ManyToManyField(BlogSubtype, blank=True, related_name='blog_set')
    tags = models.ManyToManyField(BlogTag, blank=True, related_name='blog_set')
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    banner = models.FileField("主圖片", null=True, blank=True, upload_to=helpers.upload_handle)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created']