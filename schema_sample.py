from pydantic import BaseModel, Field

class Ratings(BaseModel):
    name: str = Field(..., description="The applicant's name.")
    frontend_experience: int = Field(..., description="Rate the applicant's experience with modern web development technologies (especially React and TypeScript).")
    python_experience: int = Field(..., description="Rate the applicant's experience with Python.")
    cloud_platforms_experience: int = Field(..., description="Rate the applicant's experience with cloud platforms such as AWS, Google Cloud, or Azure. Be more generous in giving points if they've used AWS specifically.")
    ai_experience: int = Field(..., description="Rate the applicant's experience developing and deploying AI-driven applications.")
    graphql_experience: int = Field(..., description="Rate the applicant's experience with GraphQL.")
    mobile_experience: int = Field(..., description="Rate the user's experience developing mobile application frontends.")
    llm_experience: int = Field(..., description="Rate the user's experience with large language models (LLMs).")
