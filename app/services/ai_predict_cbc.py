"""
AI CBC Anemia Prediction Service
"""
import pandas as pd
from typing import Dict, List, Optional

# Try to import AI modules, gracefully handle if not available
try:
    from app.ai.cbc import (
        load_model_and_assets,
        prepare_dataframe_for_inference,
        build_report
    )
    AI_AVAILABLE = True
except ImportError as e:
    AI_AVAILABLE = False
    print(f"⚠️ AI modules not available: {e}")


class CBCPredictionService:
    """Service for CBC Anemia predictions"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.used_features = None
        self._loaded = False
        self._available = AI_AVAILABLE
    
    def is_available(self) -> bool:
        """Check if AI prediction is available"""
        return self._available
    
    def load_model(self):
        """Load the model, scaler, and features"""
        if not self._available:
            raise RuntimeError("AI prediction modules are not available. Please install required dependencies.")
        
        if not self._loaded:
            self.model, self.scaler, self.used_features = load_model_and_assets()
            self._loaded = True
            print("✅ CBC Anemia model loaded successfully")
    
    def predict_single(self, cbc_data: Dict, with_report: bool = False) -> Dict:
        """
        Predict anemia for a single patient
        
        Args:
            cbc_data: Dict with keys: RBC, HGB, PCV, MCV, MCH, MCHC, TLC, PLT
            with_report: Include detailed medical report
            
        Returns:
            Dict with prediction results
        """
        if not self._available:
            raise RuntimeError("AI prediction is not available. Missing required dependencies.")
        
        if not self._loaded:
            self.load_model()
        
        # Create DataFrame
        df = pd.DataFrame([cbc_data])
        
        # Prepare data
        df_prepared = prepare_dataframe_for_inference(df, self.used_features)
        
        # Scale and predict
        X = df_prepared[self.used_features].values
        X_scaled = self.scaler.transform(X)
        
        y_pred = self.model.predict(X_scaled)
        y_proba = self.model.predict_proba(X_scaled)
        
        # Build result
        result = {
            "id": cbc_data.get("ID") or cbc_data.get("id"),
            "predicted_anemia": int(y_pred[0]),
            "diagnosis": "Healthy" if int(y_pred[0]) == 0 else "Anemia",
            "confidence": float(y_proba[0][int(y_pred[0])])
        }
        
        if with_report:
            df_prepared['Predicted_Anemia'] = y_pred
            result["report"] = build_report(df_prepared.iloc[0])
        
        return result
    
    def predict_batch(self, patients: List[Dict], with_report: bool = False) -> List[Dict]:
        """
        Predict anemia for multiple patients
        
        Args:
            patients: List of dicts with CBC data
            with_report: Include detailed medical reports
            
        Returns:
            List of prediction results
        """
        if not self._available:
            raise RuntimeError("AI prediction is not available. Missing required dependencies.")
        
        if not self._loaded:
            self.load_model()
        
        results = []
        for patient in patients:
            result = self.predict_single(patient, with_report)
            results.append(result)
        
        return results
    
    def get_required_features(self) -> List[str]:
        """Get list of required features"""
        if not self._available:
            raise RuntimeError("AI prediction is not available. Missing required dependencies.")
        
        if not self._loaded:
            self.load_model()
        return self.used_features


# Singleton instance
cbc_predictor = CBCPredictionService()