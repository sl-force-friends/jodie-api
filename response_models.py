"""
response_models.py
"""
from pydantic import BaseModel, Field

# Response Models for Instructor
class AlternativeTitles(BaseModel):
    """
    Class for the alternative titles
    """
    alternative_titles: list[str] = Field(min_items=1,
                                          max_items=3,
                                          description="List of alternative job titles")

class NegativeContentCheck(BaseModel):
    """
    Class for the negative content check
    """
    required_years_of_experience: bool = Field(
        description="Binary value indicating if the requirements of years of experience is present")
    required_formal_education: bool = Field(
        description="Binary value indicating if the requirements of specific formal education"\
            "is present")

class PositiveContentCheck(BaseModel):
    """
    Class for the positive content check
    """
    employee_value_proposition: bool = Field(
        description="Binary value indicating if the Employee Value Proposition is present")
    job_summary_and_responsibilities: bool = Field(
        description="Binary value indicating if the Job Summary and Responsibilities are present")
    required_technical_competencies: bool = Field(
        description="Binary value indicating if the Required Technical Competencies are present")
    required_behavioural_competencies: bool = Field(
        description="Binary value indicating if the Required Behavioural Competencies are present")
    preferred_technical_competencies: bool = Field(
        description="Binary value indicating if the Preferred Technical Competencies are present")
    preferred_behavioural_competencies: bool = Field(
        description="Binary value indicating if the Preferred Behavioural Competencies are present")
    example_activities: bool = Field(
        description="Binary value indicating if the Example Activities are present")
    required_certification: bool = Field(
        description="Binary value indicating if the Required Certification is present")
