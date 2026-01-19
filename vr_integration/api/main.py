"""
FastAPI Backend
REST API for question prediction and VR configuration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import sys
import os

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)

from vr_integration.model_inference.predictor import get_predictor
from vr_integration.vr_engine.vr_decision import get_vr_engine
from vr_integration.api.question_generator import get_question_generator

app = FastAPI(
    title="LGS VR Math Learning API",
    description="ML Model + VR Integration API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (lazy loading)
_predictor = None
_vr_engine = None

def get_services():
    """Lazy load services"""
    global _predictor, _vr_engine
    if _predictor is None:
        try:
            _predictor = get_predictor()
        except Exception as e:
            print(f"Warning: Could not load model predictor: {e}")
            _predictor = None
    
    if _vr_engine is None:
        _vr_engine = get_vr_engine()
    
    return _predictor, _vr_engine


# Request/Response Models
class QuestionRequest(BaseModel):
    """Question input request"""
    soru_metin: str
    secenekler: Optional[Dict[str, str]] = None  # {"A": "...", "B": "..."}
    gorsel_bagimli: Optional[str] = None


class PredictionResponse(BaseModel):
    """Model prediction response"""
    alt_konu: str
    soru_tipi: str
    confidence: Dict[str, float]
    vr_config: Dict


class VRConfigResponse(BaseModel):
    """VR configuration response"""
    activated: bool
    scene_type: str
    mode: str
    config: Dict


class QuestionResponse(BaseModel):
    """Question with prediction and VR config"""
    question: Dict  # Question data from dataset
    prediction: Optional[Dict] = None  # Model prediction
    vr_config: Optional[Dict] = None  # VR configuration


# API Endpoints
@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok",
        "service": "LGS VR Math Learning API",
        "version": "1.0.0"
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict_question(request: QuestionRequest):
    """
    Predict alt_konu and soru_tipi, and get VR configuration
    
    This is the main endpoint that combines:
    1. ML Model prediction
    2. VR decision engine
    3. VR scene configuration
    """
    predictor, vr_engine = get_services()
    
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Model predictor not available. Please train the model first."
        )
    
    try:
        # Format input
        text_input = predictor.format_question_input(
            soru_metin=request.soru_metin,
            secenekler=request.secenekler,
            gorsel_bagimli=request.gorsel_bagimli
        )
        
        # Get prediction
        prediction = predictor.predict(text_input, return_probs=False)
        
        # Get VR configuration
        vr_config = vr_engine.get_vr_config(
            alt_konu=prediction["alt_konu"],
            soru_tipi=prediction["soru_tipi"],
            gorsel_bagimli=request.gorsel_bagimli
        )
        
        return PredictionResponse(
            alt_konu=prediction["alt_konu"],
            soru_tipi=prediction["soru_tipi"],
            confidence=prediction["confidence"],
            vr_config=vr_config
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )


@app.post("/vr-config", response_model=VRConfigResponse)
async def get_vr_config(
    alt_konu: str,
    soru_tipi: str,
    gorsel_bagimli: Optional[str] = None
):
    """
    Get VR configuration for given predictions
    
    Useful if you already have predictions and just need VR config
    """
    _, vr_engine = get_services()
    
    try:
        config = vr_engine.get_vr_config(
            alt_konu=alt_konu,
            soru_tipi=soru_tipi,
            gorsel_bagimli=gorsel_bagimli
        )
        
        return VRConfigResponse(**config)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"VR config error: {str(e)}"
        )


@app.get("/generate-question", response_model=QuestionResponse)
async def generate_question(gorsel_filter: Optional[str] = None):
    """
    Generate a random question from dataset with prediction and VR config
    
    Args:
        gorsel_filter: Filter by visual dependency
            - "bagimli": Only visual dependent questions
            - "bagimsiz": Only visual independent questions
            - "destekleyici": Only supporting visual questions
            - None: All questions
    
    This endpoint:
    1. Gets a random question from dataset
    2. Predicts alt_konu and soru_tipi
    3. Gets VR configuration
    """
    predictor, vr_engine = get_services()
    question_gen = get_question_generator()
    
    # Get random question with filter
    question = question_gen.get_random_question(gorsel_filter=gorsel_filter)
    if question is None:
        raise HTTPException(
            status_code=503,
            detail="Question generator not available. Dataset not loaded."
        )
    
    prediction = None
    vr_config = None
    
    # If predictor is available, get prediction and VR config
    if predictor is not None:
        try:
            # Format input
            text_input = predictor.format_question_input(
                soru_metin=question['soru_metin'],
                secenekler=question['secenekler'],
                gorsel_bagimli=question.get('gorsel_bagimli')
            )
            
            # Get prediction
            prediction = predictor.predict(text_input, return_probs=False)
            
            # Get VR configuration
            vr_config = vr_engine.get_vr_config(
                alt_konu=prediction["alt_konu"],
                soru_tipi=prediction["soru_tipi"],
                gorsel_bagimli=question.get('gorsel_bagimli')
            )
        except Exception as e:
            print(f"Warning: Could not get prediction: {e}")
            # Continue without prediction
    
    return QuestionResponse(
        question=question,
        prediction=prediction,
        vr_config=vr_config
    )


@app.post("/check-answer")
async def check_answer(question_id: int, selected_answer: str):
    """
    Check if selected answer is correct
    
    Note: This is a simplified version. In production, you'd want to
    store questions in a database or cache.
    
    Args:
        question_id: Question ID
        selected_answer: Selected answer (A, B, C, D, E)
    """
    question_gen = get_question_generator()
    
    # For now, we'll search the dataset for the question
    # In production, use a database or cache
    if question_gen.df is None:
        raise HTTPException(
            status_code=503,
            detail="Question generator not available"
        )
    
    # Find question by ID
    question_row = question_gen.df[question_gen.df['id'] == question_id]
    
    if len(question_row) == 0:
        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )
    
    correct_answer = str(question_row.iloc[0]['dogru_cevap']).strip().upper()
    is_correct = selected_answer.upper() == correct_answer
    
    return {
        "correct": is_correct,
        "correct_answer": correct_answer,
        "selected_answer": selected_answer.upper()
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    predictor, vr_engine = get_services()
    question_gen = get_question_generator()
    
    return {
        "api": "ok",
        "model": "loaded" if predictor is not None else "not_loaded",
        "vr_engine": "ok",
        "question_generator": "loaded" if question_gen.df is not None else "not_loaded"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

