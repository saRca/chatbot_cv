"""
Este es un sistema de recomendaciones para hojas de vida:
La función load_resumes() carga la base de datos de recomendaciones para hojas de vida.
La función get_resumes() muestra todas las recomendaciones disponibles.
La función get_resume(id) obtiene una recomendación específica por su identificador.
La función chatbot(query) es un asistente que busca recomendaciones según palabras clave y sinónimos.
La función get_resumes_by_profession(profession) ayuda a encontrar recomendaciones según la profesión.
"""

# Importamos las herramientas necesarias para construir nuestra API
from fastapi import FastAPI, HTTPException # FastAPI nos ayuda a crear la API, HTTPException maneja errores.
from fastapi.responses import HTMLResponse, JSONResponse # HTMLResponse para páginas web, JSONResponse para respuestas en formato JSON. 
import pandas as pd # Pandas nos ayuda a manejar datos en tablas, como si fuera un Excel.
import nltk # NLTK es una librería para procesar texto y analizar palabras. 
from nltk.tokenize import word_tokenize # Se usa para dividir un texto en palabras individuales.
from nltk.corpus import wordnet # Nos ayuda a encontrar sinónimos de palabras. 

# Indicamos la ruta donde NLTK buscará los datos descargados en nuestro computador. 
nltk.data.path.append('dataset')

# Descargamos las herramientas necesarias de NLTK para el análisis de palabras.
nltk.download('punkt') # Paquete para dividir frases en palabras.
nltk.download('wordnet') # Paquete para encontrar sinónimos de palabras en inglés.

# Función para cargar las recomendaciones desde un archivo CSV
def load_resumes():
    # Leemos el archivo que contiene información de hojas de vida y seleccionamos las columnas
    df = pd.read_csv("dataset/recomendaciones_hoja_vida.csv")[['profesion', 'experiencia_laboral', 'habilidades_clave', 'formacion_académica', 'formato_recomendado', 'palabras_clave', 'consejos_adicionales']]
    # Llenamos los espacios vacíos con texto vacío y convertimos los datos en una lista de diccionarios 
    return df.fillna('').to_dict(orient='records')

# Cargamos las recomendaciones al iniciar la API
resumes_list = load_resumes()

# Función para encontrar sinónimos de una palabra
def get_synonyms(word): 
    # Usamos WordNet para obtener distintas palabras que significan lo mismo.
    return {lemma.name().lower() for syn in wordnet.synsets(word) for lemma in syn.lemmas()}

# Creamos la aplicación FastAPI
app = FastAPI(title="API de Recomendaciones para Hojas de Vida", version="1.0.0")

# Ruta de inicio
@app.get('/', tags=['Home'])
def home():
    return HTMLResponse('<h1>Bienvenido al Sistema de Recomendaciones para Hojas de Vida</h1>')

# Ruta para obtener todas las recomendaciones
@app.get('/resumes', tags=['Resumes'])
def get_resumes():
    return resumes_list or HTTPException(status_code=500, detail="No hay recomendaciones disponibles")

# Ruta para obtener una recomendación específica según su identificador
@app.get('/resumes/{id}', tags=['Resumes'])
def get_resume(id: str):
    return next((r for r in resumes_list if r['id'] == id), {"detalle": "recomendación no encontrada"})

# Ruta del chatbot que responde con recomendaciones según palabras clave
@app.get('/chatbot', tags=['Chatbot'])
def chatbot(query: str):
    # Dividimos la consulta en palabras clave
    query_words = word_tokenize(query.lower())
    
    # Buscamos sinónimos de las palabras clave para ampliar la búsqueda
    synonyms = {word for q in query_words for word in get_synonyms(q)} | set(query_words)
    
    # Filtramos la lista de recomendaciones buscando coincidencias en palabras clave
    results = [r for r in resumes_list 
              if any(s in r['palabras_clave'].lower() for s in synonyms) or 
                 any(s in r['profesion'].lower() for s in synonyms)]
    
    return JSONResponse(content={
        "respuesta": "Aquí tienes algunas recomendaciones relacionadas." if results else "No encontré recomendaciones para esa búsqueda.",
        "recomendaciones": results
    })
    
# Ruta para buscar recomendaciones por profesión
@app.get('/resumes/by_profession/', tags=['Resumes'])
def get_resumes_by_profession(profession: str):
    # Filtramos la lista de recomendaciones según la profesión
    return [r for r in resumes_list if profession.lower() in r['profesion'].lower()]