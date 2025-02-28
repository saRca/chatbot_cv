from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from app.models.chat import ChatSession, Message
from app.models.conversation_state import ConversationState, ConversationStage, ConversationType
from app.services.dataset_service import DatasetService
from app.models.schemas.resume import Resume
from loguru import logger
import json
import re
from datetime import datetime
import os
from dotenv import load_dotenv
from typing import List, Tuple

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

            logger.info(f"Processing message in stage: {state.stage}")

            response, state = self._process_message(message, state)

            return response

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "Lo siento, ha ocurrido un error. ¿Podrías intentar nuevamente?"

    def _process_message(self, message: str, state: ConversationState) -> Tuple[str, ConversationState]:
        """Procesa el mensaje del usuario y actualiza el estado de la conversación."""
        message = message.lower().strip()
        
        # Comandos especiales
        if message == "quiero ver mi cv":
            if not state.is_complete():
                return "Aún necesito más información para generar tu CV. Continuemos con el proceso. 😊", state
            cv_content = self._generate_cv_html(state)
            return cv_content, state
            
        if message in ["no", "ninguna", "ninguno", "finalizar"]:
            if state.stage != ConversationStage.COMPLETE:
                state.stage = ConversationStage.COMPLETE
                cv_content = self._generate_cv_html(state)
                return f"¡Listo! Aquí tienes tu CV optimizado:\n\n{cv_content}", state
            else:
                return "¡Gracias por usar nuestro asistente! Que tengas mucho éxito en tu búsqueda laboral. 🚀", state

        # Procesar según la etapa actual
        if state.stage == ConversationStage.START:
            if message == "hola":
                return "¡Hola! 👋 Soy tu asistente para crear un CV optimizado para ATS. Para empezar, ¿podrías compartirme tu nombre completo y correo electrónico? 📧", state
            
            state.personal_info["contact"] = message
            state.stage = ConversationStage.CV_TYPE
            return (f"¡Gracias {message.split()[0].capitalize()}! 😊 Me gustaría saber un poco más sobre tus objetivos profesionales. ¿Estás buscando:\n\n"
                   "💼 Una posición específica (cuéntame el puesto)\n"
                   "🎯 O prefieres un CV general para tu área profesional?"), state

        elif state.stage == ConversationStage.CV_TYPE:
            if "1" in message or "vacante" in message or "especific" in message or "posición" in message:
                state.cv_type = ConversationType.SPECIFIC
                state.stage = ConversationStage.VACANCY
                return "¡Perfecto! 🎯 Cuéntame sobre el puesto al que te gustaría aplicar. ¿Cuál es el título y las principales responsabilidades?", state
            else:
                state.cv_type = ConversationType.GENERAL
                state.stage = ConversationStage.PROFESSION
                return "¡Entiendo! 💼 ¿En qué campo profesional te desempeñas? Cuéntame sobre tu área de especialización.", state

        elif state.stage == ConversationStage.VACANCY:
            state.vacancy_info = message
            resumes = self.dataset_service.search_resumes(message)
            state.initial_recommendations = self._generate_initial_recommendations(resumes, message)
            state.stage = ConversationStage.EDUCATION
            return (f"¡Gracias por compartir eso! Basado en lo que me cuentas, te comparto algunas recomendaciones para crear un CV que destaque:\n\n"
                   f"{state.initial_recommendations}\n\n"
                   f"Ahora, teniendo en cuenta estas recomendaciones, cuéntame sobre tu formación académica más relevante para este puesto. 🎓"), state

        elif state.stage == ConversationStage.PROFESSION:
            state.profession = message
            resumes = self.dataset_service.search_resumes(message)
            state.initial_recommendations = self._generate_initial_recommendations(resumes, message)
            state.stage = ConversationStage.EDUCATION
            return (f"¡Excelente elección profesional! He preparado algunas recomendaciones para potenciar tu CV en esta área:\n\n"
                   f"{state.initial_recommendations}\n\n"
                   f"Considerando estas sugerencias, háblame de tu formación académica más relevante. 🎓"), state

        elif state.stage == ConversationStage.EDUCATION:
            state.education.append(message)
            state.stage = ConversationStage.EXPERIENCE
            return ("¡Gran formación! Ahora cuéntame sobre tu experiencia laboral. Recuerda incluir logros medibles y responsabilidades clave. 💪\n"
                   "Por ejemplo: 'Lideré un equipo de 5 personas y aumenté la productividad en un 25%'"), state

        elif state.stage == ConversationStage.EXPERIENCE:
            state.experience.append(message)
            state.stage = ConversationStage.SKILLS
            return ("¡Impresionante experiencia! Por último, ¿cuáles son tus principales habilidades técnicas y blandas? 🌟\n"
                   "Piensa en las herramientas que dominas y tus fortalezas personales."), state

        elif state.stage == ConversationStage.SKILLS:
            state.skills.append(message)
            state.stage = ConversationStage.COMPLETE
            
            context = self._get_user_context(state)
            resumes = self.dataset_service.search_resumes(state.vacancy_info or state.profession)
            state.final_recommendations = self._generate_final_recommendations(resumes, context)
            
            cv_content = self._generate_cv_html(state)
            return (f"¡Excelente! Con toda esta información, he preparado tu CV optimizado. 🎉\n\n"
                   f"📝 **Recomendaciones para destacar aún más:**\n\n"
                   f"{state.final_recommendations}\n\n"
                   f"Aquí está tu CV:\n\n{cv_content}\n\n"
                   "¿Te gustaría hacer algún ajuste? (responde 'no' si estás conforme)"), state

        return "Disculpa, no logré entender tu mensaje. ¿Podrías reformularlo de otra manera?", state

    def _generate_initial_recommendations(self, resumes: List[Resume], context: str) -> str:
        """Genera recomendaciones iniciales para guiar la recopilación de información."""
        try:
            system_prompt = (
                "Eres un experto en desarrollo profesional y optimización de CV. "
                "Genera recomendaciones amigables y específicas para ayudar a la persona a destacar en su CV. "
                "Las recomendaciones deben ser conversacionales pero mantener este formato:\n\n"
                "💫 **Lo que más valoran los reclutadores:**\n"
                "• [3-4 aspectos clave para el rol]\n\n"
                "📚 **Formación que marca la diferencia:**\n"
                "• [2-3 tipos de estudios o certificaciones relevantes]\n\n"
                "💼 **Experiencia que destaca:**\n"
                "• [2-3 tipos de experiencias o logros importantes]\n\n"
                "🌟 **Habilidades clave:**\n"
                "• [3-4 habilidades técnicas y blandas esenciales]\n\n"
                "Usa emojis y viñetas para mejor legibilidad."
            )

            human_prompt = (
                f"Necesito recomendaciones iniciales para un CV en: {context}\n"
                "Las recomendaciones deben ser específicas y ayudar al usuario a proporcionar mejor información."
            )

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.chat_model.invoke(messages)
            return response.content.strip()

        except Exception as e:
            logger.error(f"Error generando recomendaciones iniciales: {e}")
            return (
                "💫 **Lo que más valoran los reclutadores:**\n"
                "• Experiencia relevante y demostrable\n"
                "• Logros cuantificables\n"
                "• Proyectos destacados\n\n"
                "📚 **Formación que marca la diferencia:**\n"
                "• Títulos relevantes para el área\n"
                "• Certificaciones clave\n\n"
                "💼 **Experiencia que destaca:**\n"
                "• Roles con responsabilidades similares\n"
                "• Proyectos exitosos\n\n"
                "🌟 **Habilidades clave:**\n"
                "• Competencias técnicas específicas\n"
                "• Habilidades de comunicación\n"
                "• Capacidad de resolución de problemas"
            )

    def _generate_final_recommendations(self, resumes: List[Resume], context: str) -> str:
        """Genera recomendaciones finales personalizadas."""
        try:
            system_prompt = (
                "Eres un experto en desarrollo profesional. Basado en el CV del usuario, "
                "genera recomendaciones finales siguiendo este formato:\n\n"
                "🎯 **Para destacar tu perfil:**\n"
                "• [2-3 sugerencias de mejora específicas]\n\n"
                "💡 **Para optimizar el impacto:**\n"
                "• [2-3 consejos de formato y presentación]\n\n"
                "⭐ **Palabras clave sugeridas:**\n"
                "• [3-4 términos relevantes para el sector]\n\n"
                "🔍 **Para superar filtros ATS:**\n"
                "• [2-3 consejos específicos]\n\n"
                "Usa emojis y viñetas para mejor legibilidad."
            )

            human_prompt = (
                f"Genera recomendaciones finales para este CV:\n{context}\n"
                "Las recomendaciones deben ser específicas y accionables."
            )

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.chat_model.invoke(messages)
            return response.content.strip()

        except Exception as e:
            logger.error(f"Error generando recomendaciones finales: {e}")
            return (
                "🎯 **Para destacar tu perfil:**\n"
                "• Añade métricas específicas a tus logros\n"
                "• Personaliza el objetivo profesional\n\n"
                "💡 **Para optimizar el impacto:**\n"
                "• Usa viñetas para mejor legibilidad\n"
                "• Mantén un formato consistente\n\n"
                "⭐ **Palabras clave sugeridas:**\n"
                "• Términos técnicos relevantes\n"
                "• Habilidades específicas del sector\n\n"
                "🔍 **Para superar filtros ATS:**\n"
                "• Incluye palabras clave de la descripción\n"
                "• Evita tablas y gráficos complejos"
            )

    def _generate_cv_html(self, state: ConversationState) -> str:
        """Genera el CV en formato HTML."""
        try:
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
            contact_info = state.personal_info.get('contact', '').strip()
            html += f"""
            <div class="section">
                <h1>Curriculum Vitae</h1>
                <div class="contact-info">{contact_info}</div>
            </div>
            """

            # Objetivo Profesional
            if state.cv_type == ConversationType.SPECIFIC:
                objective = state.vacancy_info
            else:
                objective = f"Profesional en {state.profession}"
            
            html += f"""
            <div class="section">
                <h2>Objetivo Profesional</h2>
                <div class="item">{objective}</div>
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

            html += """
            </body>
            </html>
            """

            return html

        except Exception as e:
            logger.error(f"Error generando HTML del CV: {str(e)}")
            return "Error al generar el CV. Por favor, intenta nuevamente."

    def _get_user_context(self, state: ConversationState) -> str:
        """Obtiene el contexto del usuario para generar recomendaciones."""
        return f"""
        Información de contacto: {state.personal_info.get('contact', '')}
        Tipo de CV: {'Específico' if state.cv_type == ConversationType.SPECIFIC else 'General'}
        Vacante: {state.vacancy_info or ''}
        Profesión: {state.profession or ''}
        Educación: {', '.join(state.education)}
        Experiencia: {', '.join(state.experience)}
        Habilidades: {', '.join(state.skills)}
        """
