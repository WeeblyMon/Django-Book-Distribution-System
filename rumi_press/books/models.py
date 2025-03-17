from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publishing_date = models.DateField(null=True, blank=True)  
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    distribution_expense = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title