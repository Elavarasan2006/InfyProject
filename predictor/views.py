import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# ✅ CORRECTED PATHS - changed "ml_models" to "ml"
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "ml" / "jobrole_model.pkl"
TARGET_ENCODER_PATH = BASE_DIR / "ml" / "jobrole_target_encoder.pkl"
TEXT_ENCODERS_PATH = BASE_DIR / "ml" / "text_label_encoders.pkl"
SKILL_ENCODER_PATH = BASE_DIR / "ml" / "multilabel_skills.pkl"
CERT_ENCODER_PATH = BASE_DIR / "ml" / "multilabel_cert.pkl"


def _load_model() -> Tuple[Any, List[str]]:
    artifact = joblib.load(MODEL_PATH)
    if isinstance(artifact, dict) and "model" in artifact:
        return artifact["model"], artifact.get("feature_columns", [])
    return artifact, []


def _load_encoders() -> Tuple[Any, Dict[str, Any]]:
    # ✅ FIXED: Use TARGET_ENCODER_PATH instead of ENCODER_PATH
    artifact = joblib.load(TARGET_ENCODER_PATH)
    if isinstance(artifact, dict):
        target_encoder = artifact.get("target_encoder")
        feature_encoders = artifact.get("feature_encoders", {})
        return target_encoder, feature_encoders
    return artifact, {}


def _prepare_features(
    payload: Dict[str, Any],
    feature_columns: List[str],
    feature_encoders: Dict[str, Any],
) -> np.ndarray:
    if not feature_columns:
        feature_columns = list(payload.keys())

    missing = [col for col in feature_columns if col not in payload]
    if missing:
        raise ValueError(f"Missing required feature(s): {', '.join(missing)}")

    ordered_values: List[float] = []

    for column in feature_columns:
        value = payload[column]

        # If we have an encoder for this column, use it
        if column in feature_encoders:
            encoder = feature_encoders[column]
            try:
                encoded = encoder.transform([value])
            except Exception as exc:
                # Try with string conversion (some encoders expect str inputs)
                try:
                    encoded = encoder.transform([str(value)])
                except Exception as exc2:
                    raise ValueError(f"Encoding failed for feature '{column}': {exc2}") from exc2

            # encoded might be:
            # - a 1D array / list with a single scalar (e.g. LabelEncoder -> array([2]))
            # - a 2D array (e.g. MultiLabelBinarizer -> array([[0,1,0,1,...]]))
            # Normalize to a 1D list of numbers to append
            if hasattr(encoded, "shape") and len(encoded.shape) == 2 and encoded.shape[1] > 1:
                # e.g. array([[0,1,0,...]]) -> take first row and extend
                row = encoded[0].tolist()
                ordered_values.extend([float(x) for x in row])
            else:
                # either scalar array like array([2]) or single value
                try:
                    val = encoded[0]
                    # if val is array-like, convert to float (handles array([2]) -> 2)
                    if hasattr(val, "__len__") and not isinstance(val, (str, bytes)):
                        # e.g. val might be numpy scalar or 0-d array
                        # flatten and take first element
                        v = np.asarray(val).ravel()[0]
                        ordered_values.append(float(v))
                    else:
                        ordered_values.append(float(val))
                except Exception:
                    # last resort: try converting the encoded itself to float
                    ordered_values.append(float(encoded))
        else:
            # No encoder: expect numeric input from payload
            try:
                ordered_values.append(float(value))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Feature '{column}' must be numeric") from exc

    return np.array([ordered_values])


def _get_top_predictions_with_confidence(model, feature_array, label_encoder, top_n=3):
    """Get top N predictions with confidence scores"""
    try:
        # Get probability scores for all classes
        probabilities = model.predict_proba(feature_array)[0]
        
        # Get all class labels
        if hasattr(label_encoder, "classes_"):
            all_classes = label_encoder.classes_
        else:
            # If no classes attribute, use numeric predictions
            all_classes = range(len(probabilities))
        
        # Get indices of top N predictions
        top_indices = np.argsort(probabilities)[-top_n:][::-1]
        
        # Get top predictions and their confidence scores
        top_predictions = []
        for idx in top_indices:
            if hasattr(label_encoder, "inverse_transform"):
                prediction_label = label_encoder.inverse_transform([idx])[0]
            else:
                prediction_label = str(idx)
            
            # Convert float32 to float for JSON serialization
            confidence = float(probabilities[idx] * 100)  # Convert to percentage and to native float
            
            top_predictions.append({
                'role': prediction_label,
                'confidence': round(confidence, 2)
            })
        
        return top_predictions
        
    except AttributeError:
        # If model doesn't support predict_proba, fall back to basic prediction
        numeric_prediction = model.predict(feature_array)[0]
        if hasattr(label_encoder, "inverse_transform"):
            prediction = label_encoder.inverse_transform([int(numeric_prediction)])[0]
        else:
            prediction = str(numeric_prediction)
        
        # Return default confidence if predict_proba not available
        return [{'role': prediction, 'confidence': 85.0}]


@csrf_exempt
def predict_job(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
        print(f"📨 Received raw data from frontend: {payload}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON payload"}, status=400)

    if not isinstance(payload, dict):
        return JsonResponse({"detail": "Payload must be a JSON object"}, status=400)

    # ✅ FIXED: Use TARGET_ENCODER_PATH instead of ENCODER_PATH
    if not MODEL_PATH.exists() or not TARGET_ENCODER_PATH.exists():
        return JsonResponse({"detail": "Model artifacts missing. Please train the model first."}, status=500)

    try:
        model, feature_columns = _load_model()
        label_encoder, feature_encoders = _load_encoders()
        feature_array = _prepare_features(payload, feature_columns, feature_encoders)
        print(f"🔢 Created {len(feature_array[0])} features for model")
        
        # Get top 3 predictions with confidence scores
        top_predictions = _get_top_predictions_with_confidence(model, feature_array, label_encoder, top_n=3)
        
        # Primary prediction (highest confidence)
        primary_prediction = top_predictions[0]['role']
        confidence_score = top_predictions[0]['confidence']
        
        # Alternative suggestions (next 2 predictions)
        suggestions = []
        if len(top_predictions) > 1:
            suggestions = [pred['role'] for pred in top_predictions[1:3]]
        
        # Ensure we always have 2 suggestions (duplicate if needed)
        while len(suggestions) < 2:
            if len(suggestions) == 0:
                suggestions.append(f"{primary_prediction} Specialist")
            else:
                suggestions.append(suggestions[0] + " Expert")
        
        print(f"🎯 Prediction: {primary_prediction}, Confidence: {confidence_score}%")
        print(f"💡 Suggestions: {suggestions}")
        
        # Convert all values to JSON-serializable types
        response_data = {
            "prediction": str(primary_prediction),
            "confidence": float(confidence_score),  # Ensure it's native float
            "suggestions": [str(suggestion) for suggestion in suggestions]
        }
        
        return JsonResponse(response_data)
        
    except ValueError as exc:
        print(f"❌ ValueError: {exc}")
        return JsonResponse({"detail": str(exc)}, status=400)
    except Exception as exc:  # catch-all for model/IO errors
        print(f"❌ Prediction failed: {exc}")
        return JsonResponse({"detail": f"Prediction failed: {exc}"}, status=500)