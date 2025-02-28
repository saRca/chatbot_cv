from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from app.models.chat import ChatSession, Message
from app.models.conversation_state import ConversationState, ConversationStage
from app.services.dataset_service import DatasetService
from loguru import logger
import json
import re
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class ChatService:
    def __init__(self):
        """Inicializa el servicio de chat."""
        self.chat_model = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-3.5-turbo",
            temperature=0.7
        )
        self.conversation_states = {}
        self.dataset_service = DatasetService()

    def process_message(self, session: ChatSession, message: str) -> str:
        """Procesa un mensaje en una sesión existente."""
        try:
            # Obtener o crear estado
            state = self.conversation_states.get(session.session_id)
            if not state:
                state = ConversationState()
                self.conversation_states[session.session_id] = state

            # Procesar mensaje según el estado actual
            if state.stage == ConversationStage.START:
                state.personal_info["name"] = message
                state.stage = ConversationStage.CONTACT
                return "Gracias. Ahora, ¿podrías proporcionarme tu información de contacto? (email y teléfono)"

            elif state.stage == ConversationStage.CONTACT:
                state.personal_info["contact"] = message
                state.stage = ConversationStage.EDUCATION
                return "Excelente. Ahora hablemos de tu educación. ¿Podrías compartir tu formación académica? (título, institución, año)"

            elif state.stage == ConversationStage.EDUCATION:
                state.education.append(message)
                state.stage = ConversationStage.EXPERIENCE
                return "Gracias. Ahora cuéntame sobre tu experiencia laboral. ¿Cuál ha sido tu experiencia más relevante?"

            elif state.stage == ConversationStage.EXPERIENCE:
                state.experience.append(message)
                state.stage = ConversationStage.SKILLS
                return "Perfecto. ¿Cuáles son tus principales habilidades técnicas y blandas?"

            elif state.stage == ConversationStage.SKILLS:
                state.skills.append(message)
                state.stage = ConversationStage.LANGUAGES
                return "Excelente. ¿Qué idiomas dominas y a qué nivel?"

            elif state.stage == ConversationStage.LANGUAGES:
                state.languages.append(message)
                state.stage = ConversationStage.CERTIFICATIONS
                return "Gracias. Por último, ¿tienes alguna certificación relevante? Si no tienes, escribe 'no hay más'"

            elif state.stage == ConversationStage.CERTIFICATIONS:
                if message.lower() == "no hay más":
                    cv_html = self._generate_cv_html(state)
                    state.stage = ConversationStage.COMPLETE
                    return f"¡Perfecto! He generado tu CV optimizado para ATS. Aquí está:\n\n{cv_html}"
                else:
                    state.certifications.append(message)
                    return "¿Tienes más certificaciones? Si no tienes más, escribe 'no hay más'"

            elif state.stage == ConversationStage.COMPLETE:
                if message.lower() == "no":
                    return "Gracias por usar nuestro servicio. ¡Que tengas éxito en tu búsqueda laboral!"
                else:
                    return "Tu CV ya está completo. ¿Deseas hacer algún cambio específico?"

            return "Lo siento, no entendí tu mensaje. ¿Podrías intentar de nuevo?"

        except Exception as e:
            logger.error(f"Error procesando mensaje: {str(e)}")
            return "Lo siento, hubo un error procesando tu mensaje. Por favor, intenta de nuevo."

    def _generate_cv_html(self, state: ConversationState) -> str:
        """Genera el HTML del CV basado en el estado actual."""
        try:
            # Crear el HTML base con estilos mejorados
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {
                        font-family: 'Arial', sans-serif;
                        line-height: 1.6;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                        color: #333;
                    }
                    h1 {
                        color: #2c3e50;
                        font-size: 28px;
                        margin-bottom: 5px;
                        border-bottom: 2px solid #3498db;
                        padding-bottom: 10px;
                    }
                    h2 {
                        color: #2c3e50;
                        font-size: 22px;
                        margin-top: 25px;
                        margin-bottom: 15px;
                        border-bottom: 1px solid #bdc3c7;
                        padding-bottom: 5px;
                    }
                    .section {
                        margin-bottom: 30px;
                    }
                    .contact-info {
                        font-size: 16px;
                        color: #555;
                        margin-bottom: 20px;
                    }
                    .item {
                        margin-bottom: 15px;
                        padding-left: 20px;
                        position: relative;
                    }
                    .item::before {
                        content: "•";
                        position: absolute;
                        left: 0;
                        color: #3498db;
                    }
                    .highlight {
                        color: #3498db;
                        font-weight: bold;
                    }
                </style>
            </head>
            <body>
            """

            # Información Personal
            name = state.personal_info.get('name', '').strip()
            contact = state.personal_info.get('contact', '').strip()
            
            html += f"""
            <div class="section">
                <h1>{name}</h1>
                <div class="contact-info">{contact}</div>
            </div>
            """

            # Educación
            if state.education:
                html += """
                <div class="section">
                    <h2>Educación</h2>
                """
                for edu in state.education:
                    html += f'<div class="item">{edu}</div>'
                html += "</div>"

            # Experiencia
            if state.experience:
                html += """
                <div class="section">
                    <h2>Experiencia Profesional</h2>
                """
                for exp in state.experience:
                    html += f'<div class="item">{exp}</div>'
                html += "</div>"

            # Habilidades
            if state.skills:
                html += """
                <div class="section">
                    <h2>Habilidades</h2>
                """
                for skill in state.skills:
                    html += f'<div class="item">{skill}</div>'
                html += "</div>"

            # Idiomas
            if state.languages:
                html += """
                <div class="section">
                    <h2>Idiomas</h2>
                """
                for lang in state.languages:
                    html += f'<div class="item">{lang}</div>'
                html += "</div>"

            # Certificaciones
            if state.certifications:
                html += """
                <div class="section">
                    <h2>Certificaciones</h2>
                """
                for cert in state.certifications:
                    html += f'<div class="item">{cert}</div>'
                html += "</div>"

            html += """
            </body>
            </html>
            """

            return html

        except Exception as e:
            logger.error(f"Error generando HTML del CV: {str(e)}")
            raise ValueError(f"Error al generar el CV: {str(e)}")

    def _get_next_stage(self, stage: ConversationStage) -> ConversationStage:
        """Obtiene la siguiente etapa basada en la etapa actual."""
        next_stages = {
            ConversationStage.START: ConversationStage.CONTACT,
            ConversationStage.CONTACT: ConversationStage.EDUCATION,
            ConversationStage.EDUCATION: ConversationStage.EXPERIENCE,
            ConversationStage.EXPERIENCE: ConversationStage.SKILLS,
            ConversationStage.SKILLS: ConversationStage.LANGUAGES,
            ConversationStage.LANGUAGES: ConversationStage.CERTIFICATIONS,
            ConversationStage.CERTIFICATIONS: ConversationStage.COMPLETE
        }
        return next_stages.get(stage, ConversationStage.COMPLETE)

    def _get_next_question(self, stage: ConversationStage) -> str:
        """Obtiene la siguiente pregunta basada en el estado."""
        questions = {
            ConversationStage.START: "Por favor, comparte tu nombre completo.",
            ConversationStage.CONTACT: "¿Podrías proporcionarme tu información de contacto? (email y teléfono)",
            ConversationStage.EDUCATION: "Cuéntame sobre tu formación académica (título, institución, año).",
            ConversationStage.EXPERIENCE: "Comparte tu experiencia laboral (cargo, empresa, período).",
            ConversationStage.SKILLS: "¿Cuáles son tus principales habilidades técnicas y blandas?",
            ConversationStage.LANGUAGES: "¿Qué idiomas dominas y a qué nivel?",
            ConversationStage.CERTIFICATIONS: "Comparte tus certificaciones (nombre, institución, fecha). Si no tienes, escribe 'no hay más'.",
            ConversationStage.COMPLETE: "¡Listo! Tu CV está completo. ¿Deseas hacer algún cambio?"
        }
        return questions.get(stage, "Lo siento, no puedo determinar la siguiente pregunta.")
