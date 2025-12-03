import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from pymongo import MongoClient
from bson import ObjectId
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import pandas as pd
import joblib
from pathlib import Path
from collections import Counter
from django.db.models import Count

from predictor.views import predict_job
from .serializers import RegisterSerializer
from .models import PredictionHistory

# --------------------------------------------------
# ✅ MongoDB Connection
# --------------------------------------------------
client = MongoClient("mongodb+srv://Elavarasan-db2025:Elavarasanatlas06@cluster6.ukhq53j.mongodb.net/")
db = client["infy_database"]
users_collection = db["users"]

BASE_DIR = Path(__file__).resolve().parent.parent
# ✅ CORRECTED PATHS - changed "ml_models" to "ml"
TEXT_ENCODERS_PATH = BASE_DIR / "ml" / "text_label_encoders.pkl"
SKILL_ENCODER_PATH = BASE_DIR / "ml" / "multilabel_skills.pkl"
CERT_ENCODER_PATH = BASE_DIR / "ml" / "multilabel_cert.pkl"

# --------------------------------------------------
# REGISTER
# --------------------------------------------------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


# --------------------------------------------------
# LOGIN
# --------------------------------------------------
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password required"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            return Response({"error": "Invalid email or password"},
                            status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(username=username, password=password)

        if user:
            auth_login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Login successful",
                "access": str(refresh.access_token),
                "username": user.username,
                "email": user.email,
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid credentials"},
                        status=status.HTTP_401_UNAUTHORIZED)


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        return Response({'detail': 'Logged out successfully'},
                        status=status.HTTP_200_OK)


# --------------------------------------------------
# FORGOT PASSWORD
# --------------------------------------------------
class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')

        if not email:
            return Response({'error': 'Email is required'}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'No user found with this email'}, status=404)

        if new_password:
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password changed successfully'})

        return Response({'error': 'Provide new_password'}, status=400)


# --------------------------------------------------
# TEMPLATE PAGES
# --------------------------------------------------
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

def visualizations_page(request):
    """Render the visualizations page"""
    return render(request, 'api/visualizations.html')


# --------------------------------------------------
# PROFILE SAVE
# --------------------------------------------------
class ProfileSaveView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        email = data.get('email')

        if not email:
            return Response({'error': 'Email is required'}, status=400)

        profile_data = {
            "name": data.get('name'),
            "email": email,
            "degree": data.get('degree'),
            "major": data.get('major'),
            "experience": data.get('experience')
        }

        existing = users_collection.find_one({"email": email})

        if existing:
            users_collection.update_one({"email": email}, {"$set": profile_data})
            return Response({'message': 'Profile updated successfully'})
        else:
            users_collection.insert_one(profile_data)
            return Response({'message': 'Profile created successfully'}, status=201)


# --------------------------------------------------
# GET PROFILE
# --------------------------------------------------
class ProfileGetView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, email):
        user = users_collection.find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])
            return Response(user)

        return Response({'error': 'User not found'}, status=404)


# --------------------------------------------------
# REDIRECT
# --------------------------------------------------
def profile_redirect(request):
    return redirect('/profile-page/')


# --------------------------------------------------
# GET CURRENT USER (NEW FUNCTION)
# --------------------------------------------------
@csrf_exempt
def get_current_user(request):
    """Get current logged in user info"""
    try:
        if request.user.is_authenticated:
            return JsonResponse({
                'email': request.user.email,
                'username': request.user.username,
                'is_authenticated': True
            })
        else:
            # For demo purposes, return a demo user
            return JsonResponse({
                'email': 'demo@example.com',
                'username': 'demo_user',
                'is_authenticated': False,
                'is_demo': True
            })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# --------------------------------------------------
# 🔥 JOB PREDICTION API (FIXED VERSION)
# --------------------------------------------------
@csrf_exempt
def predict_job_api(request):
    if request.method == "GET":
        return JsonResponse({"message": "Prediction API active. Use POST to send data."})

    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            
            print("📨 Received raw data from frontend:", data)  # Debug log

            # Make sure required fields exist
            required = ["Degree", "Major"]
            for r in required:
                if r not in data or not data[r]:
                    return JsonResponse({"error": f"Missing field: {r}"}, status=400)

            # ✅ PREPROCESS: Convert text data to numeric format
            processed_data = preprocess_frontend_data(data)
            print("🔢 Processed numeric data:", processed_data)  # Debug log

            # Create a new request with processed numeric data
            from django.http import HttpRequest
            mock_request = HttpRequest()
            mock_request.method = 'POST'
            mock_request._body = json.dumps(processed_data).encode('utf-8')
            
            # Pass PROCESSED numeric data to ML prediction function
            response = predict_job(mock_request)
            
            # ✅ ADDED: Auto-save prediction after successful prediction
            if response.status_code == 200:
                try:
                    prediction_data = json.loads(response.content)
                    if 'prediction' in prediction_data:
                        # Get user email (for demo, use a default)
                        user_email = "user@example.com"
                        if request.user.is_authenticated:
                            user_email = request.user.email
                        
                        # Save prediction to history
                        save_data = {
                            'email': user_email,
                            'predicted_job': prediction_data['prediction'],
                            'skills': data.get('Skills', ''),
                            'confidence': prediction_data.get('confidence', 85)
                        }
                        
                        # Call save_prediction internally
                        from django.http import HttpRequest
                        save_request = HttpRequest()
                        save_request.method = 'POST'
                        save_request._body = json.dumps(save_data).encode('utf-8')
                        save_prediction(save_request)
                        
                        print("✅ Prediction auto-saved to history")
                except Exception as save_error:
                    print("⚠️ Could not auto-save prediction:", save_error)
            
            return response

        except Exception as e:
            print("❌ Prediction error:", str(e))  # Debug log
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


# ✅ PREPROCESSING FUNCTION (FIXED VERSION)
def preprocess_frontend_data(data):
    """Convert frontend text data to 201-feature format expected by the model"""
    
    try:
        # Load the encoders
        skills_encoder = joblib.load(SKILL_ENCODER_PATH)
        cert_encoder = joblib.load(CERT_ENCODER_PATH)
        
        # Basic feature mappings
        degree_map = {
            "B.Tech": 0, "BCA": 1, "MCA": 2, "M.Tech": 3,
            "B.E": 4, "B.Sc": 5, "MTech": 3, "BTech": 0
        }
        
        major_map = {
            "Computer Science": 0, "Information Technology": 1,
            "Software Engineering": 2, "AI & ML": 3,
            "Data Science": 4, "AI": 5, "Cyber Security": 6
        }
        
        specialization_map = {
            "Frontend Development": 0, "Full Stack Development": 1,
            "React Development": 2, "Web Technologies": 3, "UI/UX": 4,
            "Backend Development": 5, "Full Stack": 6, "Machine Learning": 7
        }
        
        industry_map = {
            "Product-based": 0, "Startups": 1, "Tech Consulting": 2,
            "IT Services": 3, "Software Development": 4
        }

        # Process basic features
        basic_features = {
            'Degree': degree_map.get(data.get('Degree', ''), -1),
            'Major': major_map.get(data.get('Major', ''), -1),
            'Specialization': specialization_map.get(data.get('Specialization', ''), -1),
            'CGPA': float(data.get('CGPA', 0)),
            'Years of Experience': float(data.get('Years of Experience', 0)),
            'Preferred Industry': industry_map.get(data.get('Preferred Industry', ''), -1)
        }
        
        # Process skills (convert comma-separated to list)
        skills_text = data.get('Skills', '')
        skills_list = [s.strip() for s in skills_text.split(',')] if skills_text else []
        
        # Process certifications (convert comma-separated to list)
        cert_text = data.get('Certification', '')
        cert_list = [c.strip() for c in cert_text.split(',')] if cert_text else []
        
        # Create the full feature vector with 201 features
        processed_data = create_full_feature_vector(
            basic_features, skills_list, cert_list, skills_encoder, cert_encoder
        )
        
        print(f"🔢 Created {len(processed_data)} features for model")
        return processed_data
        
    except Exception as e:
        print(f"❌ Preprocessing error: {e}")
        # Fallback to simple preprocessing (might not work but prevents crash)
        return preprocess_simple_fallback(data)


def create_full_feature_vector(basic_features, skills_list, cert_list, skills_encoder, cert_encoder):
    """Create the 201-feature vector expected by the model"""
    
    # Convert basic features to DataFrame
    input_df = pd.DataFrame([basic_features])
    
    # Encode skills using multilabel encoder
    skills_encoded = skills_encoder.transform([skills_list])
    skills_df = pd.DataFrame(skills_encoded, columns=skills_encoder.classes_)
    skills_df = skills_df.add_prefix('skill_')
    
    # Encode certifications using multilabel encoder
    # Handle case sensitivity in certification names
    valid_certs = []
    for cert in cert_list:
        cert_lower = cert.lower()
        found = False
        for train_cert in cert_encoder.classes_:
            if cert_lower in train_cert.lower() or train_cert.lower() in cert_lower:
                valid_certs.append(train_cert)
                found = True
                break
        if not found and cert:
            print(f"⚠️  Certification '{cert}' not found, using default")
            valid_certs.append("Google Cloud Basics")  # Default fallback
    
    if not valid_certs:
        valid_certs = ["Google Cloud Basics"]  # Default fallback
    
    cert_encoded = cert_encoder.transform([valid_certs])
    cert_df = pd.DataFrame(cert_encoded, columns=cert_encoder.classes_)
    cert_df = cert_df.add_prefix('cert_')
    
    # Combine all features
    final_df = pd.concat([input_df, skills_df, cert_df], axis=1)
    
    # Load model to get expected columns
    try:
        model_path = BASE_DIR / "ml" / "jobrole_model.pkl"
        model = joblib.load(model_path)
        expected_columns = model.feature_names_in_
        
        # Ensure all expected columns are present (fill missing with 0)
        for col in expected_columns:
            if col not in final_df.columns:
                final_df[col] = 0
        
        # Reorder columns to match training
        final_df = final_df[expected_columns]
        
    except Exception as e:
        print(f"⚠️  Could not load model for column validation: {e}")
    
    # Convert to dictionary format for JSON serialization
    processed_dict = final_df.iloc[0].to_dict()
    
    return processed_dict


def preprocess_simple_fallback(data):
    """Fallback preprocessing if encoders fail"""
    degree_map = {"B.Tech": 0, "BCA": 1, "MCA": 2, "M.Tech": 3, "B.E": 4, "B.Sc": 5}
    major_map = {"Computer Science": 0, "Information Technology": 1, "Software Engineering": 2}
    specialization_map = {"Frontend Development": 0, "Full Stack Development": 1}
    industry_map = {"Product-based": 0, "Startups": 1, "IT Services": 2}
    
    processed = {}
    processed['Degree'] = degree_map.get(data.get('Degree', ''), -1)
    processed['Major'] = major_map.get(data.get('Major', ''), -1)
    processed['Specialization'] = specialization_map.get(data.get('Specialization', ''), -1)
    processed['CGPA'] = float(data.get('CGPA', 0))
    processed['Years of Experience'] = float(data.get('Years of Experience', 0))
    processed['Preferred Industry'] = industry_map.get(data.get('Preferred Industry', ''), -1)
    
    # Add some common skill and cert columns as fallback
    skills_text = data.get('Skills', '').lower()
    cert_text = data.get('Certification', '').lower()
    
    processed['skill_HTML'] = 1 if 'html' in skills_text else 0
    processed['skill_CSS'] = 1 if 'css' in skills_text else 0
    processed['skill_JavaScript'] = 1 if 'javascript' in skills_text else 0
    processed['skill_Python'] = 1 if 'python' in skills_text else 0
    
    processed['cert_Google Cloud Basics'] = 1 if 'google cloud' in cert_text else 0
    processed['cert_HackerRank SQL'] = 1 if 'hackerrank' in cert_text else 0
    
    print("⚠️  Using fallback preprocessing with limited features")
    return processed


# --------------------------------------------------
# VISUALIZATION DATA
# --------------------------------------------------
@csrf_exempt
def visualization_data(request, email):
    if request.method == 'GET':
        try:
            # Get user's prediction history
            user_history = PredictionHistory.objects.filter(email=email)
            
            if not user_history.exists():
                # Return sample data structure for empty state
                return JsonResponse({
                    'confidence_scores': [],
                    'job_distribution': [],
                    'skills_frequency': [],
                    'career_paths': []
                })
            
            # Confidence scores data
            confidence_scores = []
            for prediction in user_history:
                confidence_scores.append({
                    'job': prediction.predicted_job,
                    'confidence': float(prediction.confidence) if prediction.confidence else 0.0,
                    'date': prediction.date.strftime('%Y-%m-%d') if prediction.date else 'Unknown'
                })
            
            # Job distribution (count of each job type)
            job_distribution = user_history.values('predicted_job').annotate(count=Count('id'))
            job_distribution_list = [{'job': item['predicted_job'], 'count': item['count']} for item in job_distribution]
            
            # Skills frequency analysis
            skills_list = []
            for prediction in user_history:
                if prediction.skills:
                    skills = [skill.strip() for skill in prediction.skills.split(',')]
                    skills_list.extend(skills)
            
            skills_counter = Counter(skills_list)
            skills_frequency = [{'skill': skill, 'count': count} for skill, count in skills_counter.most_common(15)]
            
            # Career paths analysis (based on job transitions)
            career_paths = analyze_career_paths(user_history)
            
            data = {
                'confidence_scores': confidence_scores,
                'job_distribution': job_distribution_list,
                'skills_frequency': skills_frequency,
                'career_paths': career_paths
            }
            
            return JsonResponse(data)
            
        except Exception as e:
            print(f"❌ Error generating visualization data: {e}")
            return JsonResponse({'error': str(e)}, status=500)

def analyze_career_paths(user_history):
    """Analyze career paths based on prediction history"""
    try:
        # Get user profile to determine major/background
        # This is a simplified version - you might want to connect to user profiles
        user_email = user_history.first().email if user_history else "demo@example.com"
        
        # For now, we'll create sample career path data
        # In a real implementation, you would analyze:
        # - User's educational background
        # - Skill progression
        # - Job role transitions
        # - Industry trends
        
        career_paths = [
            {'major': 'Computer Science', 'job': 'Software Engineer', 'count': 8},
            {'major': 'Computer Science', 'job': 'Data Scientist', 'count': 4},
            {'major': 'Data Science', 'job': 'Data Scientist', 'count': 6},
            {'major': 'Data Science', 'job': 'ML Engineer', 'count': 5},
            {'major': 'IT', 'job': 'Web Developer', 'count': 7},
            {'major': 'Computer Science', 'job': 'Full Stack Developer', 'count': 3},
            {'major': 'IT', 'job': 'DevOps Engineer', 'count': 2}
        ]
        
        return career_paths
        
    except Exception as e:
        print(f"⚠️ Error in career path analysis: {e}")
        return get_sample_career_paths()


def get_sample_career_paths():
    # Return sample data for demonstration
    return [
        {'major': 'Computer Science', 'job': 'Software Engineer', 'count': 8},
        {'major': 'Computer Science', 'job': 'Data Scientist', 'count': 4},
        {'major': 'Data Science', 'job': 'Data Scientist', 'count': 6},
        {'major': 'Data Science', 'job': 'ML Engineer', 'count': 5},
        {'major': 'IT', 'job': 'Web Developer', 'count': 7}
    ]


# --------------------------------------------------
# PREDICTION HISTORY MANAGEMENT (SINGLE DEFINITIONS)
# --------------------------------------------------
@csrf_exempt
def save_prediction(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("💾 Saving prediction:", data)
            
            prediction = PredictionHistory(
                email=data['email'],
                predicted_job=data['predicted_job'],
                skills=data['skills'],
                confidence=data['confidence']
            )
            prediction.save()
            print("✅ Prediction saved successfully")
            return JsonResponse({'message': 'Prediction saved successfully', 'id': prediction.id})
        except Exception as e:
            print(f"❌ Error saving prediction: {e}")
            return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def history_get(request, email):
    if request.method == 'GET':
        try:
            print(f"📖 Loading history for: {email}")
            # Get history for this user, ordered by most recent first
            history = PredictionHistory.objects.filter(email=email).order_by('-date')
            data = []
            for item in history:
                data.append({
                    'predicted_job': item.predicted_job,
                    'date': item.date.strftime('%Y-%m-%d %H:%M'),
                    'skills': item.skills.split(',') if item.skills else [],
                    'confidence': item.confidence
                })
            print(f"📊 Found {len(data)} predictions for {email}")
            return JsonResponse(data, safe=False)
        except Exception as e:
            print(f"❌ Error loading history: {e}")
            return JsonResponse([], safe=False)  # Return empty array on error


@csrf_exempt
def history_clear(request, email):
    if request.method == 'DELETE':
        try:
            count = PredictionHistory.objects.filter(email=email).count()
            PredictionHistory.objects.filter(email=email).delete()
            print(f"🗑️ Cleared {count} predictions for {email}")
            return JsonResponse({'message': f'History cleared successfully ({count} predictions deleted)'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# --------------------------------------------------
# DEMO DATA SETUP (NEW FUNCTION)
# --------------------------------------------------
@csrf_exempt
def setup_demo_data(request):
    """Create demo predictions for testing"""
    try:
        demo_email = "demo@example.com"
        
        # Clear existing demo data
        PredictionHistory.objects.filter(email=demo_email).delete()
        
        # Create sample predictions
        sample_predictions = [
            {
                'email': demo_email,
                'predicted_job': 'Frontend Developer',
                'skills': 'HTML, CSS, JavaScript, React',
                'confidence': 85
            },
            {
                'email': demo_email,
                'predicted_job': 'Full Stack Developer', 
                'skills': 'Python, Django, React, Node.js',
                'confidence': 78
            },
            {
                'email': demo_email,
                'predicted_job': 'Data Scientist',
                'skills': 'Python, Machine Learning, SQL, Statistics',
                'confidence': 92
            }
        ]
        
        for pred_data in sample_predictions:
            prediction = PredictionHistory(**pred_data)
            prediction.save()
        
        return JsonResponse({'message': 'Demo data created successfully', 'count': len(sample_predictions)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



# In your views.py
from django.http import JsonResponse
from .models import PredictionHistory

def prediction_history(request):
    if request.method == 'GET':
        # Get predictions for current user
        predictions = PredictionHistory.objects.filter(user=request.user).order_by('-created_at')
        
        data = {
            'predictions': [
                {
                    'job': p.predicted_job,
                    'skills': p.skills,
                    'confidence': p.confidence,
                    'date': p.created_at.strftime('%b %d, %Y'),
                    'suggestions': p.suggestions.split(',') if p.suggestions else []
                }
                for p in predictions
            ]
        }
        return JsonResponse(data)
    

# Add these imports at the top if not already present
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

# --------------------------------------------------
# PREDICTION HISTORY API ENDPOINTS (NEW)
# --------------------------------------------------

@csrf_exempt
@require_http_methods(["GET"])
def prediction_history_api(request):
    """Get prediction history for current user"""
    try:
        # Get user email from request or use demo
        user_email = "demo@example.com"
        if request.user.is_authenticated:
            user_email = request.user.email
        
        print(f"📖 Loading prediction history for: {user_email}")
        
        # Get history for this user, ordered by most recent first
        history = PredictionHistory.objects.filter(email=user_email).order_by('-date')
        
        predictions_data = []
        for item in history:
            predictions_data.append({
                'id': item.id,
                'job': item.predicted_job,
                'skills': item.skills,
                'confidence': item.confidence,
                'date': item.date.strftime('%b %d, %Y') if item.date else 'Unknown date',
                'suggestions': get_job_suggestions(item.predicted_job)  # Helper function for suggestions
            })
        
        print(f"📊 Found {len(predictions_data)} predictions for {user_email}")
        
        return JsonResponse({
            'status': 'success',
            'predictions': predictions_data
        })
        
    except Exception as e:
        print(f"❌ Error loading prediction history: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'predictions': []
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def clear_all_predictions(request):
    """Clear all predictions for current user"""
    try:
        # Get user email from request or use demo
        user_email = "demo@example.com"
        if request.user.is_authenticated:
            user_email = request.user.email
        
        count = PredictionHistory.objects.filter(email=user_email).count()
        PredictionHistory.objects.filter(email=user_email).delete()
        
        print(f"🗑️ Cleared {count} predictions for {user_email}")
        
        return JsonResponse({
            'status': 'success',
            'message': f'Successfully cleared {count} predictions',
            'count': count
        })
        
    except Exception as e:
        print(f"❌ Error clearing predictions: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def get_job_suggestions(job_title):
    """Get alternative job suggestions based on predicted job"""
    suggestion_map = {
        'Web Developer': ['Frontend Developer', 'Full Stack Developer', 'UI Developer'],
        'Frontend Developer': ['Web Developer', 'UI/UX Developer', 'React Developer'],
        'Backend Developer': ['Full Stack Developer', 'API Developer', 'Software Engineer'],
        'Full Stack Developer': ['Web Developer', 'Software Engineer', 'DevOps Engineer'],
        'Data Scientist': ['Data Analyst', 'Machine Learning Engineer', 'Business Analyst'],
        'Data Analyst': ['Data Scientist', 'Business Analyst', 'Data Engineer'],
        'Product Manager': ['Project Manager', 'Business Analyst', 'Product Owner'],
        'Software Engineer': ['Full Stack Developer', 'Backend Developer', 'DevOps Engineer'],
        'ML Engineer': ['Data Scientist', 'AI Engineer', 'Research Engineer']
    }
    
    return suggestion_map.get(job_title, ['Data Analyst', 'Software Engineer', 'Product Manager'])