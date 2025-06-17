# 🤖 Chatbot IA - Sistema de Consultas de RRHH

## 📋 Descripción del Proyecto

Sistema inteligente de consultas automatizadas para el departamento de Recursos Humanos que combina múltiples técnicas de Inteligencia Artificial:

- **Clasificación automática** de tipos de preguntas
- **Predicciones de salario** usando regresión lineal
- **Procesamiento de imágenes** para extraer información de tarjetas de empleado (OCR)
- **Consultas inteligentes** a base de datos SQLite
- **Frontend web moderno** con interfaz interactiva

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   Base de       │
│   Web (HTML)    │◄──►│   Backend       │◄──►│   Datos SQLite  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Modelos IA    │
                       │                 │
                       │ • Clasificador  │
                       │ • Regresión     │
                       │ • OCR           │
                       └─────────────────┘
```

## 🧠 Modelos de IA Implementados

### 1. Clasificador de Intenciones
- **Algoritmo**: Naive Bayes con TF-IDF
- **Features**: N-gramas (1-2) con stop words en español
- **Categorías**: conteo, búsqueda_max, estadística, filtro, búsqueda_min, predicción
- **Métricas**: Accuracy, Precisión por categoría

### 2. Modelo de Regresión Lineal
- **Algoritmo**: Linear Regression (scikit-learn)
- **Features**: edad, experiencia_años, departamento (codificado), nivel_educación (codificado)
- **Variable objetivo**: salario
- **Métricas**: MAE, RMSE, R²

### 3. Procesador OCR
- **Herramienta**: Tesseract (pytesseract)
- **Preprocesamiento**: Escala de grises, umbral adaptativo, morfología
- **Extracción**: Nombre, ID, Departamento, Cargo, Email, Teléfono
- **Validación**: Verificación contra base de datos

## 📊 Base de Datos

### Estructura
```sql
CREATE TABLE empleados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    departamento TEXT NOT NULL,
    salario INTEGER NOT NULL,
    edad INTEGER NOT NULL,
    ciudad TEXT NOT NULL,
    experiencia_anos INTEGER NOT NULL,
    nivel_educacion TEXT NOT NULL,
    fecha_ingreso DATE NOT NULL
);
```

### Datos de Prueba
- **20 empleados** con datos realistas
- **5 departamentos**: Ventas, IT, Marketing, Finanzas, Recursos Humanos
- **Rango de salarios**: $25,000 - $90,000
- **Rango de edades**: 22 - 55 años
- **4 niveles educativos**: Técnico, Licenciatura, Maestría, Doctorado

## 🚀 Instalación y Configuración Completa

### Prerrequisitos
- Python 3.8+
- Tesseract OCR (para procesamiento de imágenes)
- Git (opcional)

### 1. Instalación de Tesseract OCR

**Windows:**
```bash
# Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
# Instalar en: C:\Program Files\Tesseract-OCR
# Agregar al PATH: C:\Program Files\Tesseract-OCR
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-spa
```

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang
```

### 2. Configurar Idioma Español en Tesseract

1. **Descargar archivo de idioma español:**
   - Ve a: https://github.com/tesseract-ocr/tessdata/blob/main/spa.traineddata
   - Descarga el archivo `spa.traineddata`

2. **Copiar archivo a la carpeta tessdata:**
   ```bash
   # Windows
   C:\Program Files\Tesseract-OCR\tessdata\spa.traineddata
   
   # Linux/macOS
   /usr/share/tessdata/spa.traineddata
   ```

3. **Verificar instalación:**
   ```bash
   tesseract --version
   ```

### 3. Configuración del Proyecto

1. **Clonar repositorio:**
```bash
git clone <url-del-repositorio>
cd proyecto
```

2. **Crear entorno virtual:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Instalar dependencias adicionales (si no están en requirements.txt):**
```bash
pip install opencv-python
```

5. **Crear base de datos:**
```bash
python create_database.py
```

6. **Entrenar modelos:**
```bash
python models/classifier.py
python models/regression.py
```

7. **Crear tarjetas de ejemplo para OCR:**
```bash
python models/ocr_processor.py
```

### 4. Verificar Instalación

**Probar Tesseract:**
```bash
python test_ocr.py
```

**Deberías ver:**
```
Texto extraído:
----------------------------------------
TARJETA DE EMPLEADO
Nombre: Ana García
ID: 1
Departamento: Recursos Humanos
...
----------------------------------------
```

## 🌐 Levantar el Sistema

### Opción 1: Servidor Completo (Recomendado)

```bash
# Desde la carpeta proyecto/
uvicorn main:app --reload
```

**Acceder a:**
- **Frontend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **API Info:** http://localhost:8000/api

### Opción 2: Solo Backend (para desarrollo)

```bash
# Desde la carpeta proyecto/
python main.py
```

## 🎯 Funcionalidades del Frontend

### 1. Chatbot Inteligente
- **Ubicación:** Sección superior
- **Funcionalidad:** Preguntas en lenguaje natural
- **Ejemplos:**
  - "¿Cuántos empleados hay?"
  - "¿Quién gana más?"
  - "¿Cuántos empleados hay en ventas?"

### 2. Predicción de Salarios
- **Ubicación:** Sección izquierda
- **Funcionalidad:** Formulario para predecir salarios
- **Campos requeridos:**
  - Edad (18-70 años)
  - Años de experiencia (0-50)
  - Departamento
  - Nivel educativo

### 3. Procesamiento OCR
- **Ubicación:** Sección derecha
- **Funcionalidad:** Subir y procesar tarjetas de empleado
- **Formatos soportados:** JPG, PNG, GIF
- **Drag & Drop:** Arrastra imágenes directamente

## 📡 Endpoints de la API

### 1. POST /chatbot
**Descripción**: Endpoint principal del chatbot con clasificación automática

**Request:**
```json
{
    "pregunta": "¿Cuántos empleados hay en ventas?"
}
```

**Response:**
```json
{
    "respuesta": "Hay 6 empleados en el departamento de Ventas.",
    "categoria": "filtro",
    "confianza": 0.95,
    "probabilidades": {
        "conteo": 0.02,
        "busqueda_max": 0.01,
        "estadistica": 0.01,
        "filtro": 0.95,
        "busqueda_min": 0.01,
        "prediccion": 0.00
    }
}
```

### 2. POST /predict-salario
**Descripción**: Predicción de salario usando regresión lineal

**Request:**
```json
{
    "edad": 30,
    "experiencia_anos": 5,
    "departamento": "IT",
    "nivel_educacion": "Licenciatura"
}
```

**Response:**
```json
{
    "salario_predicho": 65000.0,
    "confianza": 0.8,
    "features_usadas": {
        "edad": 30,
        "experiencia_anos": 5,
        "departamento": "IT",
        "nivel_educacion": "Licenciatura"
    }
}
```

### 3. POST /upload-tarjeta
**Descripción**: Procesamiento OCR de tarjetas de empleado

**Request:**
```json
{
    "imagen": "base64_string_de_la_imagen"
}
```

**Response:**
```json
{
    "datos_extraidos": {
        "nombre": "Juan Pérez",
        "id": "123",
        "departamento": "Ventas"
    },
    "success": true,
    "texto_extraido": "Juan Pérez\nID: 123\nDepartamento: Ventas",
    "validacion": {
        "empleado_encontrado": {
            "id": 123,
            "nombre": "Juan Pérez",
            "departamento": "Ventas"
        },
        "coincidencia_id": true
    }
}
```

## 🧪 Ejemplos de Uso

### Clasificación de Preguntas
```python
import requests

# Preguntas de ejemplo
preguntas = [
    "¿Cuántos empleados hay?",
    "¿Quién gana más?",
    "¿Cuál es el promedio de edad?",
    "¿Cuántos empleados hay en ventas?",
    "¿Quién es el más joven?",
    "¿Cuánto ganaría un empleado de 30 años en IT?"
]

for pregunta in preguntas:
    response = requests.post("http://localhost:8000/chatbot", 
                           json={"pregunta": pregunta})
    result = response.json()
    print(f"Pregunta: {pregunta}")
    print(f"Respuesta: {result['respuesta']}")
    print(f"Categoría: {result['categoria']}")
    print(f"Confianza: {result['confianza']:.3f}\n")
```

### Predicción de Salarios
```python
# Predicción de salario
prediction_data = {
    "edad": 35,
    "experiencia_anos": 8,
    "departamento": "Marketing",
    "nivel_educacion": "Maestría"
}

response = requests.post("http://localhost:8000/predict-salario", 
                        json=prediction_data)
result = response.json()
print(f"Salario predicho: ${result['salario_predicho']:,.0f}")
```

## 📈 Métricas de Rendimiento

### Clasificador de Intenciones
- **Accuracy en entrenamiento**: ~0.98
- **Accuracy en prueba**: ~0.95
- **Precisión por categoría**: >0.90 para todas las categorías

### Modelo de Regresión
- **MAE (Mean Absolute Error)**: ~$3,500
- **RMSE (Root Mean Square Error)**: ~$4,800
- **R² (Coeficiente de determinación)**: ~0.85

### Procesador OCR
- **Tasa de éxito**: ~85% en imágenes claras
- **Validación automática**: Verificación contra base de datos
- **Manejo de errores**: Respuestas robustas ante fallos

## 🔧 Configuración para Deployment

### Variables de Entorno
```bash
PORT=8000  # Puerto para Render
```

### Render.com Deployment
1. Conectar repositorio GitHub
2. Configurar como Web Service
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## 🎯 Funcionalidades Implementadas

### ✅ Obligatorias (100% completadas)
- [x] Base de datos SQLite con 20 empleados
- [x] API REST con FastAPI
- [x] Clasificador de intenciones funcional
- [x] Modelo de regresión lineal con métricas
- [x] OCR básico con Tesseract
- [x] Endpoints documentados en /docs
- [x] Manejo de errores robusto

### ✅ Frontend Web (Bonus +15 puntos)
- [x] Interfaz web moderna y responsiva
- [x] Chatbot interactivo
- [x] Formulario de predicción de salarios
- [x] Procesamiento OCR con drag & drop
- [x] Diseño responsive para móviles
- [x] Integración completa con backend

## 🛠️ Estructura del Proyecto

```
proyecto/
├── main.py                    # API principal con frontend
├── create_database.py         # Script para crear BD
├── requirements.txt           # Dependencias
├── README.md                 # Documentación
├── test_ocr.py               # Script de prueba OCR
├── static/
│   └── index.html            # Frontend web
├── models/
│   ├── classifier.py          # Clasificador de intenciones
│   ├── regression.py          # Modelo de regresión
│   └── ocr_processor.py       # Procesamiento OCR
├── data/
│   ├── empresa.db            # Base de datos SQLite
│   └── sample_cards/         # Imágenes de prueba
└── models/                   # Modelos entrenados
    ├── intent_classifier.pkl
    ├── salary_predictor.pkl
    ├── label_encoders.pkl
    └── scaler.pkl
```

## 🚀 Deployment

### URL del Deployment
```
https://chatbot-ia-backend-3461.onrender.com
```

### Documentación Automática
```
https://chatbot-ia-backend-3461.onrender.com/docs
```

## 📝 Reflexión Técnica

### Desafíos Enfrentados
1. **Integración de múltiples modelos IA**: Coordinación entre clasificación, regresión y OCR
2. **Preprocesamiento de texto**: Manejo de stop words y n-gramas en español
3. **Validación de datos OCR**: Verificación automática contra base de datos
4. **Deployment con dependencias**: Configuración de Tesseract en Render
5. **Frontend responsive**: Diseño moderno con JavaScript vanilla

### Decisiones Técnicas
- **Naive Bayes**: Elegido por simplicidad y buen rendimiento para clasificación de texto
- **Linear Regression**: Suficiente para predicciones de salario con features limitadas
- **TF-IDF**: Mejor representación de texto que bag-of-words
- **SQLite**: Base de datos ligera perfecta para prototipos
- **HTML/CSS/JS vanilla**: Sin frameworks para simplicidad y velocidad

### Mejoras Futuras
- Implementar modelos más avanzados (BERT, XGBoost)
- Añadir validación cruzada para regresión
- Mejorar preprocesamiento de imágenes OCR
- Implementar cache para modelos entrenados
- Añadir autenticación de usuarios
- Implementar historial de conversaciones

## 🔧 Solución de Problemas

### Error: "No module named 'cv2'"
```bash
pip install opencv-python
```

### Error: "Tesseract couldn't load any languages"
1. Verificar que `spa.traineddata` esté en la carpeta correcta
2. Configurar variable de entorno `TESSDATA_PREFIX`
3. Reiniciar terminal después de cambios

### Error: "Could not import module 'main'"
```bash
# Asegúrate de estar en la carpeta proyecto/
cd proyecto
uvicorn main:app --reload
```

### Frontend no carga
1. Verificar que el servidor esté en `http://localhost:8000`
2. Revisar consola del navegador (F12) para errores
3. Verificar que `static/index.html` exista

## 📞 Contacto

Para dudas técnicas durante la prueba:
- Email: hector.ruiz@mailtechxmx.com
- Respuesta garantizada en máximo 15 minutos

---

**Desarrollado con ❤️ usando FastAPI, scikit-learn, Tesseract OCR y HTML/CSS/JS** 
