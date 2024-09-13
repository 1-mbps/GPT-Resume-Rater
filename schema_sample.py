from pydantic import BaseModel, Field

class Ratings(BaseModel):
    name: str = Field(..., description="The applicant's name.")
    frontend_experience: int = Field(..., description="Rate the applicant's experience with modern web development technologies (especially React and TypeScript).")
    python_experience: int = Field(..., description="Rate the applicant's experience with Python.")
