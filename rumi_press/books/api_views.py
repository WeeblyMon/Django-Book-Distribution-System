from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg
from .models import Book, Category
from .serializers import BookSerializer, CategorySerializer

class BookViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and editing books
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filterset_fields = ['category', 'author']
    search_fields = ['title', 'author']
    
    def get_permissions(self):
        """
        Allow read-only access to all users, but only authenticated users
        can create, update or delete
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and editing categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def expense_report_api(request):
    """
    API endpoint for getting expense reports with filtering options
    """
    books = Book.objects.all()
    
    # Apply filters if provided
    category_id = request.query_params.get('category')
    if category_id and category_id != 'all':
        books = books.filter(category_id=category_id)
    
    date_from = request.query_params.get('date_from')
    if date_from:
        books = books.filter(publishing_date__gte=date_from)
    
    date_to = request.query_params.get('date_to')
    if date_to:
        books = books.filter(publishing_date__lte=date_to)
        
    # Aggregate data
    report_data = books.values('category__name').annotate(
        total_expense=Sum('distribution_expense'),
        book_count=Count('id'),
        avg_expense=Avg('distribution_expense')
    ).order_by('-total_expense')
    
    return Response(list(report_data))