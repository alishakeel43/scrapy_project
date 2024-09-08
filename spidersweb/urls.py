from django.urls import path
from .views import scrape_view,view_records,check_website,scrapy_submit

urlpatterns = [
    path('', scrape_view, name='scrape_view'),
    path('scrapy/', scrapy_submit, name='scrapy_submit'),
    path('view_records/', view_records, name='view_records'),
    path('check_website/', check_website, name='check_website'),
]