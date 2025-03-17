from django.db.models import Sum, Count, Avg, F, Q
from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponse
import csv
import datetime
from .models import Book, Category

def home_view(request):
    total_books = Book.objects.count()
    total_categories = Category.objects.count()
    total_expenses = Book.objects.aggregate(total=Sum('distribution_expense'))['total'] or 0
    recent_books = Book.objects.order_by('-id')[:5]
    
    context = {
        'total_books': total_books,
        'total_categories': total_categories,
        'total_expenses': total_expenses,
        'recent_books': recent_books,
    }
    return render(request, 'books/index.html', context)

def book_list_view(request):
    books = Book.objects.all().order_by('title')
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) | 
            Q(author__icontains=search_query)
        )
    
    category_id = request.GET.get('category', '')
    if category_id and category_id != 'all':
        books = books.filter(category__id=category_id)
        
    categories = Category.objects.all()
    
    # Pagination
    paginator = Paginator(books, 10)  # Show 10 books per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'categories': categories,
        'selected_category': category_id,
    }
    return render(request, 'books/book_list.html', context)


def report_view(request):
   
    category_id = request.GET.get('category', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    books = Book.objects.all()

    if category_id and category_id != 'all':
        books = books.filter(category_id=category_id)
    
    if date_from:
        try:
            from_date = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
            books = books.filter(publishing_date__gte=from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
            books = books.filter(publishing_date__lte=to_date)
        except ValueError:
            pass
    

    report_data = books.values('category__name').annotate(
        total_expense=Sum('distribution_expense'),
        book_count=Count('id'),
        avg_expense=Avg('distribution_expense')
    ).order_by('-total_expense')
    
    categories = Category.objects.all()
    
    context = {
        'report_data': report_data,
        'categories': categories,
        'selected_category': category_id,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'books/report.html', context)

def export_report_csv(request):
    category_id = request.GET.get('category', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    books = Book.objects.all()
    
    if category_id and category_id != 'all':
        books = books.filter(category_id=category_id)
    
    if date_from:
        try:
            from_date = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
            books = books.filter(publishing_date__gte=from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
            books = books.filter(publishing_date__lte=to_date)
        except ValueError:
            pass

    response = HttpResponse(content_type='text/csv')
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="expense_report_{timestamp}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Category', 'Number of Books', 'Total Expenses', 'Average Expense per Book'])
    
    report_data = books.values('category__name').annotate(
        total_expense=Sum('distribution_expense'),
        book_count=Count('id'),
        avg_expense=Avg('distribution_expense')
    ).order_by('-total_expense')
    
    for item in report_data:
        writer.writerow([
            item['category__name'],
            item['book_count'],
            f"${item['total_expense']}",
            f"${item['avg_expense']:.2f}"
        ])
    
    return response