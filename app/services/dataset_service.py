import json
import pandas as pd
from pathlib import Path
from typing import List, Optional, Dict
from app.models.schemas.resume import Resume
from loguru import logger

class DatasetService:
    def __init__(self):
        self.data_dir = Path("app/data")
        self.datasets_dir = self.data_dir / "datasets"
        self.resume_file = self.data_dir / "resumes.json"
        self.recommendations_file = self.datasets_dir / "recomendaciones_hoja_vida.csv"
        self.action_verbs_file = self.datasets_dir / "verbos_en_accion.xlsx"
        self._ensure_dirs()
        
    def _ensure_dirs(self):
        """Asegura que los directorios necesarios existen"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.datasets_dir.mkdir(parents=True, exist_ok=True)
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
        """Busca resumes y recomendaciones basado en un query simple"""
        results = []
        query = query.lower()
        
        # Buscar en resumes.json
        resumes = self.load_resumes()
        json_results = [
            resume for resume in resumes
            if query in resume.summary.lower() or
            any(skill.name.lower() == query for skill in resume.skills) or
            any(exp.position.lower() == query for exp in resume.experience)
        ]
        results.extend(json_results)
        
        # Buscar en recomendaciones_hoja_vida.csv
        try:
            if self.recommendations_file.exists():
                df = pd.read_csv(self.recommendations_file)
                # Buscar en la columna de profesión y palabras clave
                mask = (
                    df['profesion'].str.lower().str.contains(query, na=False) |
                    df['palabras_clave'].str.lower().str.contains(query, na=False)
                )
                csv_results = df[mask].to_dict('records')
                
                # Convertir resultados CSV a objetos Resume
                for result in csv_results:
                    resume = Resume(
                        name=result['profesion'],
                        summary=result.get('consejos_adicionales', ''),
                        skills=[{"name": skill.strip()} for skill in result.get('habilidades_clave', '').split(',')],
                        experience=[{
                            "position": result['profesion'],
                            "description": result.get('experiencia_laboral', '')
                        }]
                    )
                    results.append(resume)
        except Exception as e:
            logger.error(f"Error searching in recommendations file: {e}")
        
        return results

    def get_cv_recommendations(self, role: str = None) -> List[Dict]:
        """Obtiene recomendaciones del dataset de hojas de vida"""
        try:
            if not self.recommendations_file.exists():
                logger.warning(f"Recommendations file not found: {self.recommendations_file}")
                return []
            
            df = pd.read_csv(self.recommendations_file)
            if role:
                # Si se especifica un rol, filtrar por ese rol
                role_lower = role.lower()
                df = df[df['role'].str.lower().str.contains(role_lower, na=False)]
            
            # Convertir a lista de diccionarios
            recommendations = df.to_dict('records')
            return recommendations[:5]  # Retornar las 5 primeras recomendaciones
            
        except Exception as e:
            logger.error(f"Error loading CV recommendations: {e}")
            return []

    def get_action_verbs(self, category: str = None) -> List[str]:
        """Obtiene verbos de acción del dataset de verbos"""
        try:
            if not self.action_verbs_file.exists():
                logger.warning(f"Action verbs file not found: {self.action_verbs_file}")
                return []
            
            df = pd.read_excel(self.action_verbs_file)
            if category:
                # Si se especifica una categoría, filtrar por esa categoría
                category_lower = category.lower()
                df = df[df['category'].str.lower().str.contains(category_lower, na=False)]
            
            # Obtener lista única de verbos
            verbs = df['verb'].unique().tolist()
            return verbs
            
        except Exception as e:
            logger.error(f"Error loading action verbs: {e}")
            return []

    def get_common_skills(self) -> List[str]:
        """Obtiene las habilidades más comunes del dataset"""
        resumes = self.load_resumes()
        skills = {}
        
        for resume in resumes:
            for skill in resume.skills:
                skills[skill.name] = skills.get(skill.name, 0) + 1
        
        return sorted(skills.keys(), key=lambda x: skills[x], reverse=True)
