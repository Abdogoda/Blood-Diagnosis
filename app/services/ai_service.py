"""
AI Prediction Service
Handles CBC anemia predictions and blood cell image analysis
"""
import pandas as pd
import io
from typing import Dict, List, Optional, Any
import numpy as np
import cv2
from fastapi import UploadFile
from sqlalchemy.orm import Session
import os
import uuid
from datetime import datetime
from pathlib import Path

# Try to import AI modules, gracefully handle if not available
try:
    from app.ai.cbc import (
        load_model_and_assets,
        prepare_dataframe_for_inference,
        build_report
    )
    CBC_AI_AVAILABLE = True
except ImportError as e:
    CBC_AI_AVAILABLE = False
    print(f"⚠️ CBC AI modules not available: {e}")


# ==================== CBC Anemia Prediction ====================

class CBCPredictionService:
    """Service for CBC Anemia predictions"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.used_features = None
        self._loaded = False
        self._available = CBC_AI_AVAILABLE
    
    def is_available(self) -> bool:
        """Check if AI prediction is available"""
        return self._available
    
    def load_model(self):
        """Load the model, scaler, and features"""
        if not self._available:
            raise RuntimeError("AI prediction modules are not available")
        
        if not self._loaded:
            self.model, self.scaler, self.used_features = load_model_and_assets()
            self._loaded = True
            print("✅ CBC Anemia model loaded successfully")
    
    def predict_single(self, cbc_data: Dict, with_report: bool = False) -> Dict:
        if not self._loaded:
            self.load_model()
        
        df = pd.DataFrame([cbc_data])
        df = prepare_dataframe_for_inference(df, self.used_features, self.scaler)
        
        prediction = self.model.predict(df)[0]
        probabilities = self.model.predict_proba(df)[0]
        confidence = float(max(probabilities))
        confidence_percentage = confidence * 100  # Convert to percentage
        
        result = {
            "prediction": int(prediction),
            "prediction_label": "Anemia" if prediction == 1 else "Normal",
            "confidence": f"{confidence_percentage:.2f}%",
            "confidence_raw": confidence,
            "probabilities": {
                "normal": float(probabilities[0]),
                "anemia": float(probabilities[1])
            }
        }
        
        if with_report:
            result["report"] = build_report(cbc_data, prediction, confidence)
        
        return result
    
    def predict_batch(self, cbc_data_list: List[Dict], with_report: bool = False) -> List[Dict]:
        """Predict anemia for multiple CBC samples"""
        if not self._loaded:
            self.load_model()
        
        df = pd.DataFrame(cbc_data_list)
        df_prepared = prepare_dataframe_for_inference(df, self.used_features)
        
        # Extract features and scale
        X = df_prepared[self.used_features].values
        X_scaled = self.scaler.transform(X)
        
        # Make predictions
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        
        results = []
        for i, (pred, probs) in enumerate(zip(predictions, probabilities)):
            row_data = df_prepared.iloc[i]
            confidence_percentage = float(probs[1]) * 100  # Convert to percentage
            result = {
                "row_index": i,
                "prediction": "Anemia" if int(pred) == 1 else "Normal",
                "prediction_code": int(pred),
                "probability": f"{confidence_percentage:.2f}%",
                "probability_text": f"{probs[1]:.2%}",
                "confidence": "High" if max(probs) > 0.8 else "Medium",
                "probabilities": {
                    "normal": float(probs[0]),
                    "anemia": float(probs[1])
                },
                "values": {
                    "RBC": float(row_data.get('RBC', 0)),
                    "HGB": float(row_data.get('HGB', 0)),
                    "PCV": float(row_data.get('PCV', 0)),
                    "MCV": float(row_data.get('MCV', 0)),
                    "MCH": float(row_data.get('MCH', 0)),
                    "MCHC": float(row_data.get('MCHC', 0)),
                    "TLC": float(row_data.get('TLC', 0)),
                    "PLT": float(row_data.get('PLT', 0)),
                }
            }
            
            if with_report:
                # Create a copy to avoid SettingWithCopyWarning
                row_data_copy = row_data.copy()
                row_data_copy['Predicted_Anemia'] = pred
                row_data_copy['Anemia_Probability'] = probs[1]
                result["report"] = build_report(row_data_copy)
            
            results.append(result)
        
        return results
    
    def process_csv_upload(
        self,
        file: UploadFile,
        patient_id: int,
        uploaded_by_id: int,
        notes: str = "",
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Process CBC test data from uploaded CSV file.
        
        Args:
            file: Uploaded CSV file
            patient_id: Patient ID
            uploaded_by_id: ID of user uploading
            notes: Additional notes
            db: Database session (for future persistence)
            
        Returns:
            Dict with success status, message, and results
        """
        try:
            # Validate file
            if not file or not file.filename:
                return {
                    "success": False,
                    "message": "No file was selected. Please select a CSV file to upload."
                }
            
            if not file.filename.lower().endswith('.csv'):
                return {
                    "success": False,
                    "message": "Invalid file type. Please upload a CSV file (.csv extension)."
                }
            
            # Read and validate content
            contents = file.file.read()
            if len(contents) == 0:
                return {
                    "success": False,
                    "message": "The uploaded file is empty. Please upload a valid CSV file with CBC data."
                }
            
            # Parse CSV
            df = pd.read_csv(io.BytesIO(contents))
            if df.empty:
                return {
                    "success": False,
                    "message": "The CSV file contains no data. Please ensure your file has CBC test results."
                }
            
            # Load model if needed
            if not self._loaded:
                self.load_model()
            
            # Prepare dataframe
            df_prepared = prepare_dataframe_for_inference(df, self.used_features)
            if len(df_prepared) == 0:
                return {
                    "success": False,
                    "message": "No valid data rows found in CSV. Please check your file format and values."
                }
            
            # Convert to list of dicts for batch prediction
            cbc_data_list = df_prepared[self.used_features].to_dict('records')
            
            # Get predictions with reports
            results = self.predict_batch(cbc_data_list, with_report=True)
            
            # TODO: Save to database when ready
            # if db:
            #     - Create Test record
            #     - Create TestResult records
            #     - Save TestFile record
            
            return {
                "success": True,
                "message": f"CBC analysis completed successfully! Analyzed {len(results)} sample(s).",
                "results": results,
                "notes": notes,
                "patient_id": patient_id,
                "uploaded_by_id": uploaded_by_id
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
    
    def process_manual_input(
        self,
        rbc: float,
        hgb: float,
        pcv: float,
        mcv: float,
        mch: float,
        mchc: float,
        tlc: float,
        plt: float,
        patient_id: int,
        uploaded_by_id: int,
        notes: str = "",
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Process manually entered CBC test data.
        
        Args:
            rbc, hgb, pcv, mcv, mch, mchc, tlc, plt: CBC parameters
            patient_id: Patient ID
            uploaded_by_id: ID of user uploading
            notes: Additional notes
            db: Database session (for future persistence)
            
        Returns:
            Dict with success status, message, and result
        """
        try:
            # Create single-row dataframe
            cbc_data = {
                'RBC': rbc,
                'HGB': hgb,
                'PCV': pcv,
                'MCV': mcv,
                'MCH': mch,
                'MCHC': mchc,
                'TLC': tlc,
                'PLT': plt
            }
            
            # Load model if needed
            if not self._loaded:
                self.load_model()
            
            # Prepare and validate
            df = pd.DataFrame([cbc_data])
            df_prepared = prepare_dataframe_for_inference(df, self.used_features)
            
            if len(df_prepared) == 0:
                return {
                    "success": False,
                    "message": "Invalid CBC values provided. Please check your input."
                }
            
            # Get prediction with report
            results = self.predict_batch([cbc_data], with_report=True)
            result_data = results[0]
            
            # TODO: Save to database when ready
            # if db:
            #     - Create Test record
            #     - Create TestResult with parameters
            
            return {
                "success": True,
                "message": "CBC analysis completed successfully!",
                "result": result_data,
                "notes": notes,
                "patient_id": patient_id,
                "uploaded_by_id": uploaded_by_id
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


# ==================== Image Analysis ====================

class BloodImageAnalysisService:
    """Service for blood microscope image analysis"""
    
    def __init__(self):
        self.model = None
        self._loaded = False
    
    def process_image_upload(
        self,
        file: UploadFile,
        patient_id: int,
        uploaded_by_id: int,
        description: str = "",
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Process uploaded blood microscope image.
        
        Args:
            file: Uploaded image file
            patient_id: Patient ID
            uploaded_by_id: ID of user uploading
            description: Description of the image
            db: Database session (for future persistence)
            
        Returns:
            Dict with success status and message
        """
        try:
            # Validate file
            if not file or not file.filename:
                return {
                    "success": False,
                    "message": "No file was selected. Please select an image file to upload."
                }
            
            # Validate image extension
            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            file_extension = Path(file.filename).suffix.lower()
            if file_extension not in valid_extensions:
                return {
                    "success": False,
                    "message": f"Invalid file type. Please upload an image file ({', '.join(valid_extensions)})."
                }
            
            # Create uploads directory structure if it doesn't exist
            upload_dir = Path("uploads/tests/blood_cell")
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename with datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            random_id = uuid.uuid4().hex[:8]
            filename = f"{timestamp}_{random_id}{file_extension}"
            file_path = upload_dir / filename
            
            # Save the uploaded file
            contents = file.file.read()
            with open(file_path, "wb") as f:
                f.write(contents)
            
            # Create Test record in database
            if db:
                from app.database import Test, TestFile
                
                # Create new test
                new_test = Test(
                    patient_id=patient_id,
                    model_id=None,  # No AI model used
                    notes=description if description else "Blood cell image uploaded",
                    review_status='pending'
                )
                db.add(new_test)
                db.flush()  # Get the test ID
                
                # Create test_files record
                test_file = TestFile(
                    test_id=new_test.id,
                    name=filename,
                    extension=file_extension,
                    path=str(file_path),
                    type='input'
                )
                db.add(test_file)
                db.commit()
                
                return {
                    "success": True,
                    "message": "Blood cell image uploaded successfully!",
                    "test_id": new_test.id,
                    "file_path": str(file_path)
                }
            else:
                return {
                    "success": False,
                    "message": "Database session not provided"
                }
            
        except Exception as e:
            if db:
                db.rollback()
            return {
                "success": False,
                "message": f"Error uploading image: {str(e)}"
            }

# ==================== Service Instances ====================

# Global singleton instances
cbc_prediction_service = CBCPredictionService()
blood_image_service = BloodImageAnalysisService()
