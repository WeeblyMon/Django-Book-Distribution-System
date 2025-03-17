from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Book, Category
from decimal import Decimal
import json

class CategoryModelTests(TestCase):
    def test_category_creation(self):
        category = Category.objects.create(name='Fiction')
        self.assertEqual(category.name, 'Fiction')
        self.assertEqual(str(category), 'Fiction')

class BookModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Fiction')
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            publishing_date='2023-01-01',
            category=self.category,
            distribution_expense=Decimal('25.50')
        )
    
    def test_book_creation(self):
        self.assertEqual(self.book.title, 'Test Book')
        self.assertEqual(self.book.author, 'Test Author')
        self.assertEqual(self.book.category.name, 'Fiction')
        self.assertEqual(self.book.distribution_expense, Decimal('25.50'))
        self.assertEqual(str(self.book), 'Test Book')

class ReportViewTests(TestCase):
    def setUp(self):
        self.category1 = Category.objects.create(name='Fiction')
        self.category2 = Category.objects.create(name='Non-Fiction')
        
        Book.objects.create(
            title='Book 1',
            author='Author 1',
            category=self.category1,
            distribution_expense=Decimal('100.00')
        )
        Book.objects.create(
            title='Book 2',
            author='Author 2',
            category=self.category1,
            distribution_expense=Decimal('150.00')
        )
        Book.objects.create(
            title='Book 3',
            author='Author 3',
            category=self.category2,
            distribution_expense=Decimal('200.00')
        )
    
    def test_report_view(self):
        response = self.client.get(reverse('report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fiction')
        self.assertContains(response, 'Non-Fiction')

class BookListViewTests(TestCase):
    def setUp(self):
        self.category1 = Category.objects.create(name='Fiction')
        self.category2 = Category.objects.create(name='Non-Fiction')
        
        for i in range(15): 
            Book.objects.create(
                title=f'Book {i}',
                author=f'Author {i}',
                category=self.category1 if i % 2 == 0 else self.category2,
                distribution_expense=Decimal(f'{100 + i}.00')
            )
    
    def test_book_list_view(self):
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Book 0')
    
    def test_pagination(self):
        response = self.client.get(reverse('book_list'))
        self.assertTrue('page_obj' in response.context)
        self.assertEqual(len(response.context['page_obj']), 10) 
        
    def test_search_functionality(self):
        response = self.client.get(f"{reverse('book_list')}?search=Book 5")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Book 5')
        self.assertNotContains(response, 'Book 1')
        
    def test_category_filter(self):
        response = self.client.get(f"{reverse('book_list')}?category={self.category1.id}")
        self.assertEqual(response.status_code, 200)
        
        # We expect only books from category1 to be shown
        books_shown = response.context['page_obj']
        for book in books_shown:
            self.assertEqual(book.category, self.category1)

class APITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
 
        self.category = Category.objects.create(name='Fiction')
        self.book = Book.objects.create(
            title='API Test Book',
            author='API Author',
            category=self.category,
            distribution_expense=Decimal('50.00')
        )
        
        self.client = APIClient()
    
    def test_api_authentication_required(self):
        # Test that authentication is required
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_login_and_access(self):
        # Log in
        login_response = self.client.post('/api/login/', {
            'username': 'testuser',
            'password': 'testpassword123'
        }, format='json')
        
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        token = login_response.data['token']
        
        # AccesAPI with token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'API Test Book')
    
    def test_create_book_via_api(self):
        # Log in first
        login_response = self.client.post('/api/login/', {
            'username': 'testuser',
            'password': 'testpassword123'
        }, format='json')
        token = login_response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        
        # Create new book
        new_book_data = {
            'title': 'New API Book',
            'author': 'New API Author',
            'category': self.category.id,
            'distribution_expense': '75.00'
        }
        response = self.client.post('/api/books/', new_book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify book was created
        book = Book.objects.get(title='New API Book')
        self.assertEqual(book.author, 'New API Author')
        self.assertEqual(book.distribution_expense, Decimal('75.00'))

    def test_expense_report_api(self):
        login_response = self.client.post('/api/login/', {
            'username': 'testuser',
            'password': 'testpassword123'
        }, format='json')
        token = login_response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        
        response = self.client.get('/api/expense-report/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
  
        report_data = response.data
        self.assertEqual(len(report_data), 1)
        self.assertEqual(report_data[0]['category__name'], 'Fiction')
        self.assertEqual(Decimal(report_data[0]['total_expense']), Decimal('50.00'))
        
    def test_logout(self):

        login_response = self.client.post('/api/login/', {
            'username': 'testuser',
            'password': 'testpassword123'
        }, format='json')
        token = login_response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        logout_response = self.client.post('/api/logout/')
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)