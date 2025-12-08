"""
Shared service for patient management operations
Used by both admin and doctor roles to avoid code duplication
"""
from fastapi import Form, UploadFile, File
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import User
from app.services.flash_messages import set_flash_message
from app.services.password_utils import get_password_hash
import random
import string
import pandas as pd
import io
from typing import Dict, Any
from pathlib import Path


def add_patient_logic(
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    gender: str,
    address: str,
    blood_type: str,
    dob: str,
    db: Session,
    redirect_url: str,
    doctor_id: int = None
) -> RedirectResponse:
    """
    Shared logic for adding a patient
    Used by both admin and doctor routes
    If doctor_id is provided, creates association between doctor and patient
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        response = RedirectResponse(url=redirect_url, status_code=303)
        set_flash_message(response, "error", "A user with this email already exists")
        return response
    
    # Generate username from email
    username = email.split('@')[0]
    # Check if username exists and make it unique if necessary
    base_username = username
    counter = 1
    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}{counter}"
        counter += 1
    
    # Generate random temporary password
    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    
    # Create new patient user
    new_patient = User(
        username=username,
        password=get_password_hash(temp_password),
        fname=first_name,
        lname=last_name,
        email=email,
        phone=phone,
        gender=gender,
        address=address,
        blood_type=blood_type if blood_type else None,
        role="patient",
        is_active=1
    )
    
    try:
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        
        # If doctor_id is provided, create association
        if doctor_id:
            from app.database import doctor_patients
            db.execute(
                doctor_patients.insert().values(
                    doctor_id=doctor_id,
                    patient_id=new_patient.id
                )
            )
            db.commit()
        
        # Return success with patient ID
        return {
            "success": True,
            "patient_id": new_patient.id,
            "temp_password": temp_password,
            "name": f"{first_name} {last_name}"
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }


def upload_cbc_csv_logic(
    file: UploadFile,
    notes: str,
    patient_id: int,
    uploaded_by_id: int,
    db: Session
) -> Dict[str, Any]:
    """
    Shared logic for uploading CBC CSV
    Used by both patient and doctor routes
    """
    try:
        # Validate file was actually uploaded
        if not file or not file.filename:
            return {
                "success": False,
                "message": "No file was selected. Please select a CSV file to upload."
            }
        
        # Validate file extension
        if not file.filename.lower().endswith('.csv'):
            return {
                "success": False,
                "message": "Invalid file type. Please upload a CSV file (.csv extension)."
            }
        
        # Read the uploaded CSV file
        contents = file.file.read()
        
        # Check if file is empty
        if len(contents) == 0:
            return {
                "success": False,
                "message": "The uploaded file is empty. Please upload a valid CSV file with CBC data."
            }
        
        df = pd.read_csv(io.BytesIO(contents))
        
        # Check if CSV has data
        if df.empty:
            return {
                "success": False,
                "message": "The CSV file contains no data. Please ensure your file has CBC test results."
            }
        
        # Import prediction module
        from app.ai.cbc.predict import load_model_and_assets, prepare_dataframe_for_inference
        import numpy as np
        
        # Load model and assets
        model, scaler, used_features = load_model_and_assets()
        
        # Prepare dataframe
        df_prepared = prepare_dataframe_for_inference(df, used_features)
        
        if len(df_prepared) == 0:
            return {
                "success": False,
                "message": "No valid data rows found in CSV. Please check your file format and values."
            }
        
        # Extract features for prediction
        X = df_prepared[used_features].values
        
        # Scale features
        X_scaled = scaler.transform(X)
        
        # Make prediction
        predictions = model.predict(X_scaled)
        
        # Get prediction probabilities
        prediction_probs = model.predict_proba(X_scaled)
        
        # Add predictions to dataframe
        df_prepared['Predicted_Anemia'] = predictions
        df_prepared['Anemia_Probability'] = prediction_probs[:, 1]
        
        # Generate detailed report for the first row (or all rows if multiple)
        from app.ai.cbc.predict import build_report
        
        results = []
        for idx, row in df_prepared.iterrows():
            report = build_report(row)
            result_data = {
                "row_index": int(idx),
                "prediction": "أنيميا" if int(row['Predicted_Anemia']) == 1 else "طبيعي",
                "probability": f"{row['Anemia_Probability']:.2%}",
                "report": report,
                "values": {
                    "RBC": float(row.get('RBC', 0)),
                    "HGB": float(row.get('HGB', 0)),
                    "PCV": float(row.get('PCV', 0)),
                    "MCV": float(row.get('MCV', 0)),
                    "MCH": float(row.get('MCH', 0)),
                    "MCHC": float(row.get('MCHC', 0)),
                    "TLC": float(row.get('TLC', 0)),
                    "PLT": float(row.get('PLT', 0)),
                }
            }
            results.append(result_data)
        
        # TODO: Save to database when ready
        # - Create Test record
        # - Create TestResult record
        # - Save TestFile record
        
        return {
            "success": True,
            "message": f"CBC analysis completed successfully! Analyzed {len(results)} sample(s).",
            "results": results,
            "notes": notes
        }
        
    except ValueError as ve:
        return {
            "success": False,
            "message": f"CSV validation error: {str(ve)}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error processing CSV: {str(e)}"
        }


def upload_cbc_manual_logic(
    rbc: float,
    hgb: float,
    pcv: float,
    mcv: float,
    mch: float,
    mchc: float,
    tlc: float,
    plt: float,
    notes: str,
    patient_id: int,
    uploaded_by_id: int,
    db: Session
) -> Dict[str, Any]:
    """
    Shared logic for manual CBC input
    Used by both patient and doctor routes
    """
    try:
        # Create a dataframe from manual input
        data = {
            'RBC': [rbc],
            'HGB': [hgb],
            'PCV': [pcv],
            'MCV': [mcv],
            'MCH': [mch],
            'MCHC': [mchc],
            'TLC': [tlc],
            'PLT': [plt]
        }
        df = pd.DataFrame(data)
        
        # Import prediction module
        from app.ai.cbc.predict import load_model_and_assets, prepare_dataframe_for_inference, build_report
        import numpy as np
        
        # Load model and assets
        model, scaler, used_features = load_model_and_assets()
        
        # Prepare dataframe
        df_prepared = prepare_dataframe_for_inference(df, used_features)
        
        if len(df_prepared) == 0:
            return {
                "success": False,
                "message": "Invalid CBC values provided. Please check your input."
            }
        
        # Extract features for prediction
        X = df_prepared[used_features].values
        
        # Scale features
        X_scaled = scaler.transform(X)
        
        # Make prediction
        predictions = model.predict(X_scaled)
        
        # Get prediction probabilities
        prediction_probs = model.predict_proba(X_scaled)
        
        # Add predictions to dataframe
        df_prepared['Predicted_Anemia'] = predictions
        df_prepared['Anemia_Probability'] = prediction_probs[:, 1]
        
        # Generate detailed report
        row = df_prepared.iloc[0]
        report = build_report(row)
        
        result_data = {
            "prediction": "أنيميا" if int(row['Predicted_Anemia']) == 1 else "طبيعي",
            "probability": f"{row['Anemia_Probability']:.2%}",
            "confidence": "عالية" if row['Anemia_Probability'] > 0.8 or row['Anemia_Probability'] < 0.2 else "متوسطة",
            "report": report,
            "values": {
                "RBC": float(rbc),
                "HGB": float(hgb),
                "PCV": float(pcv),
                "MCV": float(mcv),
                "MCH": float(mch),
                "MCHC": float(mchc),
                "TLC": float(tlc),
                "PLT": float(plt),
            }
        }
        
        # TODO: Save to database when ready
        # - Create Test record
        # - Create TestResult with parameters
        
        return {
            "success": True,
            "message": "CBC analysis completed successfully!",
            "result": result_data,
            "notes": notes
        }
        
    except ValueError as ve:
        return {
            "success": False,
            "message": f"Validation error: {str(ve)}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error during CBC analysis: {str(e)}"
        }


def upload_blood_image_logic(
    file: UploadFile,
    description: str,
    patient_id: int,
    uploaded_by_id: int,
    db: Session
):
    """
    Shared logic for blood image upload
    Used by both patient and doctor routes
    """
    # TODO: Implement blood image upload logic
    # - Save image file
    # - Create Test record
    # - Create TestFile record
    # - Run AI image analysis
    return {"success": True, "message": "Blood image uploaded successfully!"}
