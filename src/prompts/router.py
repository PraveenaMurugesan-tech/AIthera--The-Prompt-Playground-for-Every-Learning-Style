import logging
import asyncio
from typing import Optional, Annotated, List

from src.services.ai_service import AIService, AIServiceError

from fastapi import APIRouter, Depends, HTTPException, Response, status, File, UploadFile
from google import genai
from google.genai import types
import os
from PIL import Image
import io
from sqlalchemy.orm import Session

from src.auth.router import get_current_user
from src.database.session import get_db
from src.models.user import User
from src.prompts import crud, schemas
from typing import Optional, Dict


router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.post("/", response_model=schemas.PromptRequestResponse, status_code=status.HTTP_201_CREATED)
def create_prompt(
    payload: schemas.PromptRequestCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> schemas.PromptRequestResponse:
    """
    Create a new PromptRequest for the authenticated user.

    Returns the created PromptRequest with a 201 status code.
    """

    request = crud.create_prompt_request(
        db,
        user_id=int(current_user.id),
        topic=payload.topic,
        learning_style=payload.learning_style,
        difficulty=payload.difficulty,
    )

    return request


@router.get("/", response_model=List[schemas.PromptRequestResponse])
def list_prompts(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> List[schemas.PromptRequestResponse]:
    """
    Return all PromptRequests for the authenticated user, newest first.
    """

    results = crud.get_user_prompt_requests(db, user_id=int(current_user.id))
    return results


@router.get("/{request_id}", response_model=schemas.PromptRequestResponse)
def get_prompt(
    request_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> schemas.PromptRequestResponse:
    """
    Return a single PromptRequest by id for the authenticated user.

    Returns 404 if the PromptRequest does not exist or does not belong to the user.
    """

    request = crud.get_prompt_request(db, request_id=request_id)

    if request is None or int(request.user_id) != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PromptRequest not found")

    return request


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prompt(
    request_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    """
    Delete a PromptRequest owned by the authenticated user.

    Returns 204 No Content on success, or 404 if not found / not owned.
    """

    # Perform a lightweight ownership check by selecting only the owner id.
    owner_id = crud.get_prompt_request_owner(db, request_id=request_id)

    if owner_id is None or int(owner_id) != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PromptRequest not found")

    # Perform a bulk delete to avoid SQLAlchemy loading related collections
    # which may reference missing tables in the database schema.
    deleted = crud.delete_prompt_request(db, request_id=request_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete prompt request")

    return Response(status_code=status.HTTP_204_NO_CONTENT)



logger = logging.getLogger("aithera.api")

_ai_service_instance: Optional[AIService] = None

def get_ai_service() -> AIService:
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance

@router.post("/generate", response_model=schemas.GeneratePromptResponse, status_code=status.HTTP_200_OK)
async def generate_prompt(
    payload: schemas.GeneratePromptRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    ai_service: Annotated[AIService, Depends(get_ai_service)],
) -> schemas.GeneratePromptResponse:
    """
    Generate an optimized prompt and educational metrics via the AI Council.
    """
    logger.info(f"Received learning_style: {payload.learning_style}")
    logger.info(f"Received payload: {payload.dict()}")
    # 1. Create DB record
    try:
        request_record = crud.create_prompt_request(
            db,
            user_id=int(current_user.id),
            topic=payload.topic,
            learning_style=payload.learning_style,
            difficulty=payload.difficulty,
            bloom_level=payload.bloom_level,
        )
    except Exception as e:
        logger.error(f"Failed to create prompt request in DB: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

    # Options mapping
    skip_variants = payload.options.get("skip_variants", False) if payload.options else False
    skip_learning_path = payload.options.get("skip_learning_path", False) if payload.options else False
    timeout = payload.options.get("timeout", 120.0) if payload.options else 120.0

    # 2. Execute Live Council
    try:
        council_result = await ai_service.generate_prompt(request_record, timeout=timeout)
    except TimeoutError:
        logger.warning(f"Timeout during Live Council generation for request {request_record.id}")
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Generation timed out")
    except AIServiceError as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"AIServiceError for request {request_record.id}: {e}\n{tb}")
        error_payload = getattr(e, "error_details", None)
        
        failed_providers = []
        if error_payload and isinstance(error_payload, dict):
            for provider, err in error_payload.items():
                failed_providers.append({
                    "provider": provider,
                    "status": err.get("status_code", "N/A"),
                    "message": err.get("message", "Unknown error")
                })
        
        if failed_providers:
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "All providers failed",
                    "providers": failed_providers,
                    "traceback": tb
                }
            )
        else:
            raise HTTPException(
                status_code=502,
                detail={
                    "provider": "Unknown",
                    "exception": str(e),
                    "traceback": tb,
                    "status": 502
                }
            )
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Unexpected error during generation for request {request_record.id}: {e}\n{tb}")
        raise HTTPException(
            status_code=502,
            detail={
                "provider": "System",
                "exception": str(e),
                "traceback": tb,
                "status": 502
            }
        )

    consensus = council_result.get("consensus")
    if not consensus:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No consensus reached")

    # 3. Generate secondary assets (learning path, variants, recommendations)
    learning_path = None
    if not skip_learning_path:
        try:
            learning_path = await ai_service.generate_learning_path(payload.topic, payload.difficulty, timeout=timeout)
        except Exception as e:
            logger.warning(f"Failed to generate learning path: {e}")

    variants = None
    if not skip_variants:
        try:
            variants = ai_service.generate_prompt_variants(payload.topic)
        except Exception as e:
            logger.warning(f"Failed to generate variants: {e}")

    recommendations = None
    try:
        # Validate prompt and generate recommendations
        # Ensure we have a generated prompt string
        generated_prompt_text = consensus.final_prompt or ""
        validation_score = ai_service.validate_prompt(generated_prompt_text)
        recommendations = ai_service.generate_recommendations(
            generated_prompt_text, 
            payload.learning_style, 
            payload.difficulty,
            validation_score
        )
    except Exception as e:
        logger.warning(f"Failed to generate recommendations: {e}")

    # Build Response
    return schemas.GeneratePromptResponse(
        optimized_prompt=consensus.final_prompt,
        consensus_reasoning=consensus.consensus_reasoning,
        confidence_score=consensus.confidence_score,
        agreement_score=consensus.agreement_score,
        provider_contributions=consensus.provider_contributions,
        educational_metrics={
            "structure_score": consensus.educational_structure_score,
            "diversity_score": consensus.diversity_score,
            "coverage_score": consensus.coverage_score,
        },
        explainability_metrics={
            "explanation": consensus.explanation,
            "evaluation_summary": consensus.evaluation_summary,
        },
        recommendations=recommendations,
        learning_path=learning_path,
        prompt_variants=variants
    )


@router.post("/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Analyzes an uploaded image to extract an educational topic or subject.
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Gemini API Key not configured")
        
        genai.configure(api_key=api_key)
        
        # Read the file bytes
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Use Gemini Vision model
        # Use the correct google-genai SDK client
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        prompt = (
            "Analyze this educational image, diagram, or handwritten note. "
            "Extract the core educational topic or concept it represents. "
            "Also provide any specific instructions or context visible in the image. "
            "Return the result strictly as a JSON object with two keys: 'topic' (a concise string) "
            "and 'instructions' (a string describing the context or additional details, or empty string if none)."
        )
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, image]
        )
        
        # Try to parse the JSON output from the model
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:-3]
        elif text.startswith('```'):
            text = text[3:-3]
            
        import json
        try:
            result = json.loads(text)
        except:
            # Fallback if the model didn't return perfect JSON
            result = {
                "topic": text[:100] + "..." if len(text) > 100 else text,
                "instructions": "Generated from Image Analysis"
            }
            
        return result
        
    except Exception as e:
        logger.error(f"Failed to analyze image: {e}")
        raise HTTPException(status_code=500, detail="Image analysis failed")
