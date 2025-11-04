from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username
    

from django.db import models
from django.contrib.auth.models import User

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
    
from mongoengine import Document, StringField, FloatField, ListField, IntField

class UserProfile(Document):
    username = StringField(required=True, unique=True)
    email = StringField(required=True)
    degree = StringField()
    major = StringField()
    cgpa = FloatField()
    skills = ListField(StringField())
    certifications = StringField()
    industry_preference = StringField()
    experience = IntField()


from django.db import models

class UserProfile(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    degree = models.CharField(max_length=100, blank=True, null=True)
    major = models.CharField(max_length=100, blank=True, null=True)
    cgpa = models.FloatField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    certifications = models.CharField(max_length=200, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    experience = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.name
    
from mongoengine import Document, StringField, FloatField, EmailField

class UserProfile(Document):
    name = StringField(required=True, max_length=100)
    email = EmailField(required=True, unique=True)
    degree = StringField(max_length=100)
    major = StringField(max_length=100)
    cgpa = FloatField()
    skills = StringField()
    certifications = StringField()
    industry = StringField()
    experience = FloatField()

    meta = {'collection': 'user_profiles'}

from mongoengine import Document, StringField, EmailField

class UserProfile(Document):
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)   # ✅ Add this
    name = StringField()





