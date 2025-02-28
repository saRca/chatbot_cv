import json
from pathlib import Path
from typing import List, Optional
from app.models.schemas.resume import Resume
from loguru import logger

class DatasetService:
    def __init__(self):
        self.data_dir = Path("app/data")
        self.resume_file = self.data_dir / "resumes.json"
        self._ensure_data_dir()
        
    def _ensure_data_dir(self):
        """Asegura que el directorio de datos existe"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.resume_file.exists():
            self.resume_file.write_text("[]")
    
    def load_resumes(self) -> List[Resume]:
        """Carga todos los resumes del dataset"""
        try:
            data = json.loads(self.resume_file.read_text())
            return [Resume(**item) for item in data]
        except Exception as e:
            logger.error(f"Error loading resumes: {e}")
            return []
    
    def save_resume(self, resume: Resume) -> bool:
        """Guarda un nuevo resume en el dataset"""
        try:
            resumes = self.load_resumes()
            resumes.append(resume)
            self.resume_file.write_text(
                json.dumps([r.dict() for r in resumes], indent=2, default=str)
            )
            return True
        except Exception as e:
            logger.error(f"Error saving resume: {e}")
            return False
    
    def search_resumes(self, query: str) -> List[Resume]:
        """Busca resumes basado en un query simple"""
        resumes = self.load_resumes()
        query = query.lower()
        
        return [
            resume for resume in resumes
            if query in resume.summary.lower() or
            any(skill.name.lower() == query for skill in resume.skills) or
            any(exp.position.lower() == query for exp in resume.experience)
        ]
    
    def get_common_skills(self) -> List[str]:
        """Obtiene las habilidades más comunes del dataset"""
        resumes = self.load_resumes()
        skills = {}
        
        for resume in resumes:
            for skill in resume.skills:
                skills[skill.name] = skills.get(skill.name, 0) + 1
        
        return sorted(skills.keys(), key=lambda x: skills[x], reverse=True)
