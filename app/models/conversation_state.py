from enum import Enum

class ConversationStage(Enum):
    START = "START"
    CONTACT = "CONTACT"
    EDUCATION = "EDUCATION"
    EXPERIENCE = "EXPERIENCE"
    SKILLS = "SKILLS"
    LANGUAGES = "LANGUAGES"
    CERTIFICATIONS = "CERTIFICATIONS"
    COMPLETE = "COMPLETE"

class ConversationState:
    def __init__(self):
        self.stage = ConversationStage.START
        self.personal_info = {}
        self.education = []
        self.experience = []
        self.skills = []
        self.languages = []
        self.certifications = []
    
    def clear(self):
        """Reinicia el estado a sus valores iniciales"""
        self.__init__()
