import pandas as pd
import joblib
from pathlib import Path

def test_model_properly():
    """Test the ML model with correct feature structure"""
    
    try:
        # Load the model and encoders
        model_path = Path("ml/jobrole_model.pkl")
        target_encoder_path = Path("ml/jobrole_target_encoder.pkl")
        skills_encoder_path = Path("ml/multilabel_skills.pkl")
        cert_encoder_path = Path("ml/multilabel_cert.pkl")
        
        print("📁 Loading models...")
        
        model = joblib.load(model_path)
        target_encoder = joblib.load(target_encoder_path)
        skills_encoder = joblib.load(skills_encoder_path)
        cert_encoder = joblib.load(cert_encoder_path)
        
        print("✅ Models loaded successfully!")
        print(f"Model feature names: {model.feature_names_in_[:10]}...")  # Show first 10 features
        
        # Interactive input
        print("\n🎯 ENTER YOUR DETAILS:")
        
        degree = int(input("Degree (0=B.Tech, 1=BCA, 2=MCA, 3=M.Tech): ") or "2")
        major = int(input("Major (0=CS, 1=IT, 2=SE, 3=AI&ML): ") or "2")
        specialization = int(input("Specialization (0=Frontend, 1=Full Stack): ") or "0")
        cgpa = float(input("CGPA: ") or "7.5")
        experience = float(input("Years of experience: ") or "2")
        industry = int(input("Industry (0=Product, 1=Startups): ") or "1")
        
        # Skills input
        print("\n🛠️ SKILLS (enter comma-separated):")
        print("Example: HTML, CSS, JavaScript, React, Python")
        skills_input = input("Your skills: ") or "HTML, CSS, JavaScript"
        skills_list = [s.strip() for s in skills_input.split(',')]
        
        # Certification input
        print("\n📜 CERTIFICATIONS (enter comma-separated):")
        print("Example: Google Cloud Basics, HackerRank SQL")
        cert_input = input("Your certifications: ") or "Google Cloud Basics"
        cert_list = [c.strip() for c in cert_input.split(',')]
        
        # Create proper feature vector
        input_data = create_feature_vector(
            degree, major, specialization, cgpa, experience, industry,
            skills_list, cert_list, skills_encoder, cert_encoder
        )
        
        print(f"\n📊 Input shape: {input_data.shape}")
        
        # Make prediction
        prediction_encoded = model.predict(input_data)
        prediction = target_encoder.inverse_transform(prediction_encoded)
        
        print(f"🎯 PREDICTED JOB ROLE: {prediction[0]}")
        
    except Exception as e:
        print(f"💥 ERROR: {e}")
        import traceback
        traceback.print_exc()

def create_feature_vector(degree, major, specialization, cgpa, experience, industry, 
                         skills_list, cert_list, skills_encoder, cert_encoder):
    """Create the exact feature vector the model expects"""
    
    # Start with basic features
    basic_features = {
        'Degree': degree,
        'Major': major,
        'Specialization': specialization,
        'CGPA': cgpa,
        'Years of Experience': experience,
        'Preferred Industry': industry
    }
    
    # Convert to DataFrame
    input_df = pd.DataFrame([basic_features])
    
    # Encode skills using multilabel encoder
    skills_encoded = skills_encoder.transform([skills_list])
    skills_df = pd.DataFrame(skills_encoded, columns=skills_encoder.classes_)
    skills_df = skills_df.add_prefix('skill_')
    
    # Encode certifications using multilabel encoder
    cert_encoded = cert_encoder.transform([cert_list])
    cert_df = pd.DataFrame(cert_encoded, columns=cert_encoder.classes_)
    cert_df = cert_df.add_prefix('cert_')
    
    # Combine all features
    final_df = pd.concat([input_df, skills_df, cert_df], axis=1)
    
    # Ensure all expected columns are present (fill missing with 0)
    expected_columns = model.feature_names_in_
    for col in expected_columns:
        if col not in final_df.columns:
            final_df[col] = 0
    
    # Reorder columns to match training
    final_df = final_df[expected_columns]
    
    return final_df

if __name__ == "__main__":
    test_model_properly()