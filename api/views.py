from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from pymongo import MongoClient
from .serializers import RegisterSerializer, UserSerializer
from .models import UserProfile


# ✅ MongoDB Connection
client = MongoClient("mongodb+srv://Elavarasan-db2025:Elavarasanatlas06@cluster6.ukhq53j.mongodb.net/")
db = client["infy_database"]
users_collection = db["users"]


# ---------------------------- REGISTER ----------------------------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


def register(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    users_collection.insert_one({
        "username": username,
        "email": email,
        "password": password
    })
    return Response({"message": "User registered successfully!"})


# ---------------------------- PROFILE ----------------------------
class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# ---------------------------- LOGIN ----------------------------
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(username=username, password=password)

        if user:
            auth_login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Login successful",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "username": user.username,
                "email": user.email,
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)


# ---------------------------- LOGOUT ----------------------------
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        return Response({'detail': 'Logged out successfully'}, status=status.HTTP_200_OK)


# ---------------------------- FORGOT PASSWORD ----------------------------
class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')

        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'No user found with this email.'}, status=status.HTTP_404_NOT_FOUND)

        if new_password:
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password changed successfully.'})

        return Response({'message': 'Password reset instructions have been sent to your email.'})


# ---------------------------- PAGES ----------------------------
def index(request):
    return render(request, 'api/index.html')


def home(request):
    username = request.user.username if request.user.is_authenticated else "Guest"
    return render(request, 'api/home.html', {"username": username})


def profile_page(request):
    return render(request, 'api/profile.html')


def predict_page(request):
    return render(request, 'api/predict.html')


def history_page(request):
    return render(request, 'api/history.html')


def forgot_password_page(request):
    return render(request, 'api/forgot_password.html')


# ---------------------------- PROFILE SAVE / GET ----------------------------
class ProfileSaveView(APIView):
    def post(self, request):
        data = request.data
        profile = UserProfile(
            username=data.get('username'),
            email=data.get('email'),
            degree=data.get('degree'),
            major=data.get('major'),
            cgpa=data.get('cgpa'),
            skills=data.get('skills', []),
            certifications=data.get('certifications'),
            industry_preference=data.get('industry_preference'),
            experience=data.get('experience')
        )
        profile.save()
        return Response({'message': 'Profile saved successfully!'}, status=status.HTTP_201_CREATED)


class ProfileGetView(APIView):
    def get(self, request, username):
        try:
            profile = UserProfile.objects.get(username=username)
            return Response(profile.to_mongo())
        except UserProfile.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# ---------------------------- PROFILE MANAGEMENT (MongoDB) ----------------------------
from bson import ObjectId

class ProfileSaveView(APIView):
    """
    Save or update profile info to MongoDB Atlas.
    """
    def post(self, request):
        data = request.data
        email = data.get('email')

        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        existing_user = users_collection.find_one({"email": email})

        profile_data = {
            "name": data.get('name'),
            "email": email,
            "degree": data.get('degree'),
            "major": data.get('major'),
            "experience": data.get('experience')
        }

        if existing_user:
            users_collection.update_one({"email": email}, {"$set": profile_data})
            return Response({'message': 'Profile updated successfully!'}, status=status.HTTP_200_OK)
        else:
            users_collection.insert_one(profile_data)
            return Response({'message': 'Profile created successfully!'}, status=status.HTTP_201_CREATED)


class ProfileGetView(APIView):
    """
    Get profile info from MongoDB Atlas using email.
    """
    def get(self, request, email):
        user = users_collection.find_one({"email": email})
        if user:
            user['_id'] = str(user['_id'])  # convert ObjectId for JSON
            return Response(user, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
from django.shortcuts import redirect

# Redirect /profile/ → /profile-page/
def profile_redirect(request):
    """Redirect API profile URL to the actual profile page."""
    return redirect('/profile-page/')












