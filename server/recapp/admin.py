from django.contrib import admin
from . import models

admin.site.register(models.Dashboard)
admin.site.register(models.Article)
admin.site.register(models.DashboardArticle)
admin.site.register(models.Url)
admin.site.register(models.CrawlingTarget)
admin.site.register(models.Response)
