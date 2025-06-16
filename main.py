from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import os
import sys

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.classifier import IntentClassifier
from models.regression import SalaryPredictor
from models.ocr_processor import OCRProcessor
import sqlite3
import json

# Crear aplicación FastAPI
app = FastAPI(
    title="Chatbot IA - Sistema de Consultas de RRHH",
    description="API inteligente para consultas de empleados con clasificación, regresión y OCR",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica la URL de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Modelos Pydantic para las peticiones
class ChatbotRequest(BaseModel):
    pregunta: str

class SalaryPredictionRequest(BaseModel):
    edad: int
    experiencia_anos: int
    departamento: str
    nivel_educacion: str

class OCRRequest(BaseModel):
    imagen: str  # base64 string

# Inicializar modelos
classifier = IntentClassifier()
salary_predictor = SalaryPredictor()
ocr_processor = OCRProcessor()

@app.on_event("startup")
async def startup_event():
    """Inicializar modelos al arrancar la aplicación"""
    print("🚀 Inicializando modelos de IA...")
    
    # Entrenar/cargar clasificador
    try:
        classifier.load_model()
        print("✅ Clasificador de intenciones listo")
    except Exception as e:
        print(f"⚠️ Error cargando clasificador: {e}")
        classifier.train()
    
    # Entrenar/cargar predictor de salarios
    try:
        salary_predictor.load_model()
        print("✅ Predictor de salarios listo")
    except Exception as e:
        print(f"⚠️ Error cargando predictor: {e}")
        salary_predictor.train()
    
    print("🎯 Todos los modelos están listos!")

@app.get("/")
async def root():
    """Endpoint raíz - Servir el frontend"""
    return FileResponse("static/index.html")

@app.get("/api")
async def api_info():
    """Endpoint de información de la API"""
    return {
        "message": "Chatbot IA - Sistema de Consultas de RRHH",
        "version": "1.0.0",
        "endpoints": {
            "chatbot": "/chatbot",
            "predict_salary": "/predict-salario",
            "upload_card": "/upload-tarjeta",
            "docs": "/docs",
            "frontend": "/"
        }
    }

@app.post("/chatbot")
async def chatbot_endpoint(request: ChatbotRequest):
    """Endpoint principal del chatbot"""
    try:
        # Clasificar la pregunta
        classification = classifier.predict(request.pregunta)
        
        # Generar respuesta basada en la categoría
        respuesta = await generate_response(request.pregunta, classification)
        
        return {
            "respuesta": respuesta,
            "categoria": classification["categoria"],
            "confianza": classification["confianza"],
            "probabilidades": classification["probabilidades"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el chatbot: {str(e)}")

async def generate_response(pregunta: str, classification: dict):
    """Generar respuesta basada en la categoría clasificada"""
    categoria = classification["categoria"]
    
    if categoria == "conteo":
        return await get_employee_count()
    
    elif categoria == "busqueda_max":
        return await get_highest_salary_employee()
    
    elif categoria == "estadistica":
        return await get_statistics()
    
    elif categoria == "filtro":
        return await get_filtered_count(pregunta)
    
    elif categoria == "busqueda_min":
        return await get_youngest_employee()
    
    elif categoria == "prediccion":
        return await get_salary_prediction(pregunta)
    
    else:
        return "Lo siento, no entiendo tu pregunta. ¿Podrías reformularla?"

async def get_employee_count():
    """Obtener conteo total de empleados"""
    conn = sqlite3.connect('data/empresa.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM empleados")
    count = cursor.fetchone()[0]
    conn.close()
    
    return f"Actualmente hay {count} empleados en la empresa."

async def get_highest_salary_employee():
    """Obtener empleado con mayor salario"""
    conn = sqlite3.connect('data/empresa.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nombre, departamento, salario 
        FROM empleados 
        ORDER BY salario DESC 
        LIMIT 1
    """)
    employee = cursor.fetchone()
    conn.close()
    
    if employee:
        return f"El empleado mejor pagado es {employee[0]} del departamento de {employee[1]} con un salario de ${employee[2]:,}."
    else:
        return "No se encontraron empleados."

async def get_statistics():
    """Obtener estadísticas generales"""
    conn = sqlite3.connect('data/empresa.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            AVG(edad) as edad_promedio,
            AVG(salario) as salario_promedio,
            AVG(experiencia_anos) as exp_promedio
        FROM empleados
    """)
    stats = cursor.fetchone()
    conn.close()
    
    return f"Estadísticas de la empresa: Edad promedio {stats[0]:.1f} años, salario promedio ${stats[1]:,.0f}, experiencia promedio {stats[2]:.1f} años."

async def get_filtered_count(pregunta: str):
    """Obtener conteo filtrado por departamento"""
    # Extraer departamento de la pregunta
    departamentos = ["ventas", "it", "marketing", "finanzas", "recursos humanos"]
    departamento = None
    
    pregunta_lower = pregunta.lower()
    for dept in departamentos:
        if dept in pregunta_lower:
            departamento = dept
            break
    
    if not departamento:
        return "Por favor, especifica un departamento (Ventas, IT, Marketing, Finanzas, Recursos Humanos)."
    
    conn = sqlite3.connect('data/empresa.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM empleados WHERE LOWER(departamento) = ?", (departamento,))
    count = cursor.fetchone()[0]
    conn.close()
    
    return f"Hay {count} empleados en el departamento de {departamento.title()}."

async def get_youngest_employee():
    """Obtener empleado más joven"""
    conn = sqlite3.connect('data/empresa.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nombre, edad, departamento 
        FROM empleados 
        ORDER BY edad ASC 
        LIMIT 1
    """)
    employee = cursor.fetchone()
    conn.cursor()
    
    if employee:
        return f"El empleado más joven es {employee[0]} con {employee[1]} años del departamento de {employee[2]}."
    else:
        return "No se encontraron empleados."

async def get_salary_prediction(pregunta: str):
    """Obtener predicción de salario"""
    # Extraer información de la pregunta (simplificado)
    # En un caso real, usarías NLP más avanzado
    
    # Valores por defecto
    edad = 30
    experiencia = 5
    departamento = "IT"
    educacion = "Licenciatura"
    
    # Intentar extraer edad
    import re
    edad_match = re.search(r'(\d+)\s*años', pregunta.lower())
    if edad_match:
        edad = int(edad_match.group(1))
    
    # Intentar extraer experiencia
    exp_match = re.search(r'(\d+)\s*años\s*de\s*experiencia', pregunta.lower())
    if exp_match:
        experiencia = int(exp_match.group(1))
    
    # Intentar extraer departamento
    dept_keywords = {
        "ventas": "Ventas",
        "it": "IT", 
        "marketing": "Marketing",
        "finanzas": "Finanzas",
        "recursos humanos": "Recursos Humanos"
    }
    
    for keyword, dept in dept_keywords.items():
        if keyword in pregunta.lower():
            departamento = dept
            break
    
    # Intentar extraer educación
    educ_keywords = {
        "técnico": "Técnico",
        "licenciatura": "Licenciatura", 
        "maestría": "Maestría",
        "doctorado": "Doctorado"
    }
    
    for keyword, educ in educ_keywords.items():
        if keyword in pregunta.lower():
            educacion = educ
            break
    
    # Hacer predicción
    prediction = salary_predictor.predict(edad, experiencia, departamento, educacion)
    
    return f"Para un empleado de {edad} años con {experiencia} años de experiencia en {departamento} con {educacion}, el salario predicho sería aproximadamente ${prediction['salario_predicho']:,.0f}."

@app.post("/predict-salario")
async def predict_salary_endpoint(request: SalaryPredictionRequest):
    """Endpoint para predicción de salario"""
    try:
        # Validar datos de entrada
        if request.edad < 18 or request.edad > 70:
            raise HTTPException(status_code=400, detail="La edad debe estar entre 18 y 70 años")
        
        if request.experiencia_anos < 0 or request.experiencia_anos > 50:
            raise HTTPException(status_code=400, detail="La experiencia debe estar entre 0 y 50 años")
        
        # Hacer predicción
        prediction = salary_predictor.predict(
            request.edad,
            request.experiencia_anos,
            request.departamento,
            request.nivel_educacion
        )
        
        return {
            "salario_predicho": prediction["salario_predicho"],
            "confianza": prediction["confianza"],
            "features_usadas": prediction["features_usadas"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")

@app.post("/upload-tarjeta")
async def upload_card_endpoint(request: OCRRequest):
    """Endpoint para procesar tarjetas de empleado con OCR"""
    try:
        # Procesar imagen
        result = ocr_processor.process_image(request.imagen)
        
        if result["success"]:
            return {
                "datos_extraidos": result["datos_extraidos"],
                "success": True,
                "texto_extraido": result["texto_extraido"],
                "validacion": result["validacion"]
            }
        else:
            return {
                "datos_extraidos": {},
                "success": False,
                "error": result["error"],
                "texto_extraido": result["texto_extraido"],
                "validacion": {}
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en OCR: {str(e)}")

@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud"""
    return {
        "status": "healthy",
        "models_loaded": {
            "classifier": classifier.pipeline is not None,
            "salary_predictor": salary_predictor.model is not None,
            "ocr_processor": True
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 