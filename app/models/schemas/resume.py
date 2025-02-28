from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class Education(BaseModel):
    institution: str
    degree: str
    field_of_study: str
    start_date: date
    end_date: Optional[date] = None
    description: Optional[str] = None

class Experience(BaseModel):
    company: str
    position: str
    start_date: date
    end_date: Optional[date] = None
    description: List[str]
    skills_used: List[str]

class Skill(BaseModel):
    name: str
    category: str
    level: Optional[str] = None

class Resume(BaseModel):
    personal_info: dict
    summary: str
    education: List[Education]
    experience: List[Experience]
    skills: List[Skill]
    languages: Optional[List[dict]] = None
    certifications: Optional[List[dict]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "personal_info": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+1234567890",
                    "location": "New York, USA"
                },
                "summary": "Experienced software engineer with 5+ years...",
                "education": [{
                    "institution": "MIT",
                    "degree": "Bachelor's",
                    "field_of_study": "Computer Science",
                    "start_date": "2015-09-01",
                    "end_date": "2019-06-30"
                }],
                "experience": [{
                    "company": "Tech Corp",
                    "position": "Senior Developer",
                    "start_date": "2019-07-01",
                    "description": [
                        "Led team of 5 developers",
                        "Implemented CI/CD pipeline"
                    ],
                    "skills_used": ["Python", "Docker", "AWS"]
                }],
                "skills": [{
                    "name": "Python",
                    "category": "Programming",
                    "level": "Expert"
                }]
            }
        }
