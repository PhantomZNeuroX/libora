from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.teacher)
admin.site.register(models.clas)
admin.site.register(models.profile)
admin.site.register(models.ebook)
admin.site.register(models.reading_day)
admin.site.register(models.ReadBook)