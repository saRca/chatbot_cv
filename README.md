# Especificación Técnica: Chatbot Generador de Hojas de Vida ATS-Friendly

## 1. Descripción General
Este proyecto consiste en el desarrollo de un chatbot interactivo que guíe a los usuarios en la creación de una hoja de vida optimizada para sistemas ATS (Applicant Tracking System). Los usuarios responderán preguntas para generar automáticamente un documento en HTML con la opción de descarga en PDF.

## 2. Tecnologías y Herramientas
### **Backend**
- **Framework**: FastAPI (Python)
- **Procesamiento de Lenguaje Natural (NLP)**: NLTK
- **Generación de Texto**: OpenAI API
- **Manejo de Conversación**: LangChain
- **Conversión de HTML a PDF**: WeasyPrint o ReportLab
- **Despliegue**: Render.com

### **Frontend**
- **Interfaz**: HTML, CSS
- **Templates**: Jinja2 para generación dinámica de contenido

## 3. Arquitectura del Sistema
### **Flujo de Interacción**
1. El usuario inicia la conversación con el chatbot.
2. LangChain gestiona el flujo de preguntas y respuestas.
3. FastAPI recibe las respuestas y genera una estructura de CV.
4. Se rellena una plantilla HTML con la información del usuario.
5. Opcion de visualización y descarga en PDF.

### **Componentes del Sistema**
1. **API de FastAPI**
   - Endpoint para recibir respuestas del usuario.
   - Endpoint para generar y devolver la hoja de vida en HTML/PDF.

2. **Módulo de Chatbot (LangChain + OpenAI API)**
   - Modelo de prompts para guiar la creación del CV.
   - Evaluación de calidad del CV según buenas prácticas ATS.

3. **Generador de Hojas de Vida (Jinja2 + WeasyPrint)**
   - Tres plantillas de CV predefinidas.
   - Conversión HTML a PDF.

## 4. Endpoints de la API
### **1. Inicio de Conversación**
```
POST /chat/start
```
**Request:**
```json
{
    "user_id": "12345"
}
```
**Response:**
```json
{
    "message": "Hola, vamos a crear tu hoja de vida. ¿Cuál es tu nombre?",
    "session_id": "abc123"
}
```

### **2. Responder Preguntas del Chatbot**
```
POST /chat/respond
```
**Request:**
```json
{
    "session_id": "abc123",
    "answer": "Juan Pérez"
}
```
**Response:**
```json
{
    "message": "¿Cuál es tu experiencia laboral?"
}
```

### **3. Generar y Descargar CV**
```
GET /cv/download/{session_id}
```
**Response:**
- Devuelve el archivo en formato PDF o HTML.

## 5. Despliegue y Monitoreo
- Implementación en **Render.com**.
- Logs y monitoreo con **Loguru**.
- Test con **pytest**.

## 6. Roadmap del Desarrollo
### **Semana 1-2:**
- Configuración del entorno y FastAPI.
- Integración de LangChain con OpenAI API.

### **Semana 3-4:**
- Desarrollo del flujo de conversación.
- Implementación de plantillas HTML.

### **Semana 5-6:**
- Conversión de HTML a PDF.
- Pruebas y ajustes.

### **Semana 7-8:**
- Despliegue y optimización.

## 7. Consideraciones
- No se almacenan hojas de vida.
- No hay integración con LinkedIn.
- Se utilizan ejemplos predefinidos para visualización del CV.

# Ruta de Desarrollo Propuesta

## Fase Inicial
- Configuración del proyecto FastAPI
- Integración básica con LangChain y OpenAI
- Estructura base del proyecto
## Fase de Conversación (Semanas 3-4)
- Implementación del flujo conversacional
- Desarrollo de plantillas HTML
- Sistema de prompts para guiar la creación del CV
- Integración con dataset de ejemplos
  - Recopilación y estructuración de datos de ejemplo
  - Implementación de búsqueda y recomendaciones
  - Sistema de análisis de habilidades comunes

## Fase de Generación (Semanas 5-6)
- Implementación de la conversión HTML a PDF
- Sistema de validación y optimización ATS
- Pruebas unitarias y de integración
## Fase Final (Semanas 7-8)
- Despliegue en Render.com
- Optimización y ajustes finales
- Documentación completa
