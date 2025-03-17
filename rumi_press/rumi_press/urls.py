from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from books.views import report_view, home_view, book_list_view, export_report_csv
from books.api_views import BookViewSet, CategoryViewSet, expense_report_api
from books.auth_views import RegisterView, CustomAuthToken, LogoutView

# Create a router for REST API
router = routers.DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('report/', report_view, name='report'),
    path('books/', book_list_view, name='book_list'),
    path('export/report/', export_report_csv, name='export_report_csv'),
    path('', home_view, name='home'),
    
    # API URLs
    path('api/', include(router.urls)),
    path('api/expense-report/', expense_report_api, name='expense_report_api'),
    path('api-auth/', include('rest_framework.urls')),
    
    # Authentication endpoints
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', CustomAuthToken.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
]