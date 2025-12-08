"""
Tests for AI service
"""
import pytest
import pandas as pd
from io import BytesIO
from app.services import cbc_prediction_service, blood_image_service


class TestCBCPredictionService:
    """Test CBC prediction service"""
    
    def test_service_initialization(self):
        """Test service is initialized"""
        assert cbc_prediction_service is not None
        assert hasattr(cbc_prediction_service, 'is_available')
        assert hasattr(cbc_prediction_service, 'load_model')
    
    def test_is_available(self):
        """Test checking if service is available"""
        available = cbc_prediction_service.is_available()
        assert isinstance(available, bool)
    
    @pytest.mark.skipif(
        not cbc_prediction_service.is_available(),
        reason="AI model not available"
    )
    def test_load_model(self):
        """Test loading the model"""
        cbc_prediction_service.load_model()
        assert cbc_prediction_service._loaded is True
        assert cbc_prediction_service.model is not None
        assert cbc_prediction_service.scaler is not None
    
    @pytest.mark.skipif(
        not cbc_prediction_service.is_available(),
        reason="AI model not available"
    )
    def test_predict_batch(self):
        """Test batch prediction"""
        cbc_data = [
            {
                'RBC': 4.5,
                'HGB': 13.5,
                'PCV': 40.0,
                'MCV': 85.0,
                'MCH': 28.0,
                'MCHC': 33.0,
                'TLC': 7.0,
                'PLT': 250.0
            }
        ]
        
        results = cbc_prediction_service.predict_batch(cbc_data, with_report=False)
        
        assert len(results) == 1
        assert 'prediction' in results[0]
        assert 'probability' in results[0]
        assert 'confidence' in results[0]
    
    def test_process_manual_input(self, db_session):
        """Test processing manual CBC input"""
        result = cbc_prediction_service.process_manual_input(
            rbc=4.5,
            hgb=13.5,
            pcv=40.0,
            mcv=85.0,
            mch=28.0,
            mchc=33.0,
            tlc=7.0,
            plt=250.0,
            patient_id=1,
            uploaded_by_id=1,
            notes="Test notes",
            db=db_session
        )
        
        assert result is not None
        assert 'success' in result
        assert 'message' in result


class TestBloodImageService:
    """Test blood image analysis service"""
    
    def test_service_initialization(self):
        """Test service is initialized"""
        assert blood_image_service is not None
        assert hasattr(blood_image_service, 'process_image_upload')
    
    def test_process_image_upload_no_file(self, db_session):
        """Test image upload with no file"""
        from fastapi import UploadFile
        
        # Mock empty upload file
        class MockFile:
            filename = None
        
        mock_upload = UploadFile(MockFile())
        
        result = blood_image_service.process_image_upload(
            file=mock_upload,
            patient_id=1,
            uploaded_by_id=1,
            description="Test",
            db=db_session
        )
        
        assert result is not None
        assert result['success'] is False
        assert 'message' in result
