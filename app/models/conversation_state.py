from enum import Enum
from typing import List, Dict, Optional

class ConversationStage(Enum):
    START = "start"
    CONTACT = "contact"
    CV_TYPE = "cv_type"  # Nueva etapa para elegir tipo de CV
    VACANCY = "vacancy"  # Para CV específico
    PROFESSION = "profession"  # Para CV general
    EDUCATION = "education"
    EXPERIENCE = "experience"
    SKILLS = "skills"
    COMPLETE = "complete"

class ConversationType(Enum):
    SPECIFIC = "specific"  # Para vacante específica
    GENERAL = "general"    # Para CV general

class ConversationState:
    def __init__(self):
        self.stage: ConversationStage = ConversationStage.START
        self.cv_type: Optional[ConversationType] = None
        self.personal_info: Dict[str, str] = {}
        self.vacancy_info: Optional[str] = None
        self.profession: Optional[str] = None
        self.education: List[str] = []
        self.experience: List[str] = []
        self.skills: List[str] = []
        self.initial_recommendations: Optional[str] = None
        self.final_recommendations: Optional[str] = None

    def is_complete(self) -> bool:
        """Verifica si se ha recopilado toda la información necesaria."""
        required_fields = [
            self.personal_info.get("contact"),
            self.education,
            self.experience,
            self.skills
        ]
        
        if self.cv_type == ConversationType.SPECIFIC:
            required_fields.append(self.vacancy_info)
        else:
            required_fields.append(self.profession)
            
        return all(field for field in required_fields)
