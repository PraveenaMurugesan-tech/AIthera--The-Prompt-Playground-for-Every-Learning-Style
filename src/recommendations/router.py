from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.auth.router import get_current_user
from src.models.user import User
from src.prompts.crud import get_user_prompt_requests
from src.services.recommendation_generator import recommendation_generator
from src.recommendations import schemas

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
)

@router.get("/dashboard", response_model=schemas.RecommendationDashboard)
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> schemas.RecommendationDashboard:
    """
    Generate and return a personalized learning dashboard based on the user's prompt history.
    """
    try:
        # Fetch user's past prompts
        prompt_history = get_user_prompt_requests(db=db, user_id=current_user.id)
        
        # Call the generator service
        dashboard = await recommendation_generator.generate_dashboard(prompt_history)
        return dashboard
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="You have hit the Gemini API rate limit. On the free tier, this is often a strict 20 requests per day limit for the Gemini 2.5 Flash model. Please try again tomorrow or upgrade your AI Studio tier."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate dashboard: {error_msg}"
        )
