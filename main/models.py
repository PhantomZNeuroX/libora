from email.policy import default
from django.db import models
from django.contrib.auth.models import User
import shortuuid

# Create your models here.
class teacher(models.Model):
    subjects = [
        ('eng', 'English'),
        ('hin', 'Hindi'),
        ('sci', 'Science'),
        ('maths', 'Maths'),
        ('ai', 'A.i.'),
        ('other', 'Other')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.CharField(max_length=35)
    subject = models.CharField(choices=subjects,max_length=15)
    def __str__(self):
        return self.user.first_name

class profile(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    clas = models.ForeignKey('clas', on_delete=models.PROTECT, null=True)
    genres = models.JSONField(null=True)
    location = models.CharField(max_length=60, null=True)
    completed = models.BooleanField(default=False)
    words = models.IntegerField(default=0)
    time = models.DecimalField(default=0,decimal_places=3, max_digits=19)
    score = models.DecimalField(default=0,decimal_places=2, max_digits=19)
    def __str__(self):
        return self.user.first_name



class clas(models.Model):
    teacher = models.OneToOneField(teacher, on_delete=models.CASCADE)
    name = models.CharField(null=True,max_length=40)
    code = models.CharField(default= shortuuid.ShortUUID().random(length=5).upper(), editable=True, max_length=5)
    students = models.ManyToManyField(User, null=True)
    goal = models.IntegerField(default=10000)
    avg = models.DecimalField(null=True,max_digits=19,decimal_places=2)
    def __str__(self):
        return self.name

class ebook(models.Model):
    clas = models.ForeignKey(clas, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    deadline = models.DateField()
    students = models.ManyToManyField(User, null=True)
    book = models.FileField()
    cover = models.FileField(null=True)
    words = models.IntegerField(null=True)
    avg = models.IntegerField(null=True)
    description = models.TextField(max_length=300, null=True)
    def __str__(self):
        return self.name

class reading_day(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    words = models.IntegerField(default=0)
    time = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.user.first_name

class ReadBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(ebook, on_delete=models.CASCADE)
    words = models.IntegerField(default=0)
    time = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    finished = models.DateField(null=True)
    score = models.DecimalField(default=0,decimal_places=2, max_digits=19)
