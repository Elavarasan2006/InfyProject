from django.db import models
from django.contrib.auth.models import User
from mongoengine import Document, StringField, FloatField, ListField, IntField, EmailField

# Django ORM Models (for SQLite)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username

class PredictionHistory(models.Model):
    email = models.EmailField()
    predicted_job = models.CharField(max_length=255)
    skills = models.TextField()  # Store as comma-separated string
    confidence = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.email} - {self.predicted_job}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    degree = models.CharField(max_length=100, blank=True)
    major = models.CharField(max_length=100, blank=True)
    cgpa = models.FloatField(blank=True, null=True)
    skills = models.TextField(blank=True)
    certifications = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    experience = models.FloatField(blank=True, null=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# MongoDB Models (for MongoEngine)
class MongoUserProfile(Document):
    username = StringField(required=True, unique=True)
    email = StringField(required=True)
    degree = StringField()
    major = StringField()
    cgpa = FloatField()
    skills = ListField(StringField())
    certifications = StringField()
    industry_preference = StringField()
    experience = IntField()

class MongoUserAuth(Document):
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    name = StringField()





