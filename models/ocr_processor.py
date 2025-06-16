import cv2
import numpy as np
import pytesseract
from PIL import Image
import re
import sqlite3
import base64
import io
import os

# Configurar la ruta de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Microsoft\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

class OCRProcessor:
    """Procesador OCR para extraer información de tarjetas de empleado"""
    
    def __init__(self):
        self.db_path = "data/empresa.db"
        
    def preprocess_image(self, image):
        """Preprocesar imagen para mejorar OCR"""
        # Convertir a escala de grises
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Aplicar umbral adaptativo
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Reducir ruido
        kernel = np.ones((1, 1), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        # Dilatación para conectar componentes
        kernel = np.ones((1, 1), np.uint8)
        img_dilation = cv2.dilate(opening, kernel, iterations=1)
        
        return img_dilation
    
    def extract_text_from_image(self, image):
        """Extraer texto de la imagen usando OCR"""
        # Configurar pytesseract
        custom_config = r'--oem 3 --psm 6'
        
        # Extraer texto
        text = pytesseract.image_to_string(image, config=custom_config, lang='spa')
        
        return text
    
    def parse_employee_card(self, text):
        """Parsear texto extraído para obtener información del empleado"""
        # Limpiar texto
        text = text.strip()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Patrones para extraer información
        patterns = {
            'nombre': r'nombre[:\s]*([a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+)',
            'id': r'id[:\s]*(\d+)',
            'departamento': r'departamento[:\s]*([a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+)',
            'cargo': r'cargo[:\s]*([a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+)',
            'email': r'email[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            'telefono': r'tel[éf]fono[:\s]*(\d{10})',
        }
        
        extracted_data = {}
        
        # Buscar patrones en el texto
        for field, pattern in patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                extracted_data[field] = match.group(1).strip()
        
        # Si no encontramos patrones específicos, intentar extraer de líneas simples
        if not extracted_data:
            # Buscar nombre (primera línea que no sea ID)
            for line in lines:
                if not re.match(r'^\d+$', line) and len(line) > 3:
                    extracted_data['nombre'] = line
                    break
            
            # Buscar ID (número)
            id_match = re.search(r'\b(\d{3,})\b', text)
            if id_match:
                extracted_data['id'] = id_match.group(1)
            
            # Buscar departamento (palabras comunes)
            dept_keywords = ['ventas', 'it', 'marketing', 'finanzas', 'recursos humanos', 'rh']
            for line in lines:
                line_lower = line.lower()
                for keyword in dept_keywords:
                    if keyword in line_lower:
                        extracted_data['departamento'] = line
                        break
        
        return extracted_data
    
    def validate_employee_data(self, extracted_data):
        """Validar datos extraídos contra la base de datos"""
        if not extracted_data:
            return {'success': False, 'error': 'No se pudieron extraer datos'}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        validation_results = {}
        
        # Validar por ID si existe
        if 'id' in extracted_data:
            cursor.execute("SELECT * FROM empleados WHERE id = ?", (extracted_data['id'],))
            employee = cursor.fetchone()
            if employee:
                validation_results['empleado_encontrado'] = {
                    'id': employee[0],
                    'nombre': employee[1],
                    'departamento': employee[2],
                    'salario': employee[3],
                    'edad': employee[4],
                    'ciudad': employee[5],
                    'experiencia_anos': employee[6],
                    'nivel_educacion': employee[7],
                    'fecha_ingreso': employee[8]
                }
                validation_results['coincidencia_id'] = True
            else:
                validation_results['coincidencia_id'] = False
        
        # Validar por nombre si existe
        if 'nombre' in extracted_data:
            # Buscar nombres similares
            cursor.execute("SELECT * FROM empleados WHERE nombre LIKE ?", (f"%{extracted_data['nombre']}%",))
            employees = cursor.fetchall()
            if employees:
                validation_results['empleados_similares'] = [
                    {
                        'id': emp[0],
                        'nombre': emp[1],
                        'departamento': emp[2]
                    } for emp in employees
                ]
                validation_results['coincidencia_nombre'] = True
            else:
                validation_results['coincidencia_nombre'] = False
        
        # Validar departamento
        if 'departamento' in extracted_data:
            cursor.execute("SELECT DISTINCT departamento FROM empleados")
            valid_departments = [row[0] for row in cursor.fetchall()]
            
            dept_lower = extracted_data['departamento'].lower()
            validation_results['departamento_valido'] = any(
                valid.lower() in dept_lower or dept_lower in valid.lower() 
                for valid in valid_departments
            )
        
        conn.close()
        
        return validation_results
    
    def process_image(self, image_base64):
        """Procesar imagen base64 y extraer información"""
        try:
            # Decodificar imagen base64
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # Convertir a numpy array
            image_np = np.array(image)
            
            # Preprocesar imagen
            processed_image = self.preprocess_image(image_np)
            
            # Extraer texto
            extracted_text = self.extract_text_from_image(processed_image)
            
            # Parsear datos
            extracted_data = self.parse_employee_card(extracted_text)
            
            # Validar datos
            validation_results = self.validate_employee_data(extracted_data)
            
            return {
                'success': True,
                'texto_extraido': extracted_text,
                'datos_extraidos': extracted_data,
                'validacion': validation_results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'texto_extraido': '',
                'datos_extraidos': {},
                'validacion': {}
            }
    
    def create_sample_card(self, employee_data, output_path):
        """Crear una tarjeta de empleado de muestra"""
        from PIL import Image, ImageDraw, ImageFont
        
        # Crear imagen
        width, height = 400, 300
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        # Configurar fuente (usar fuente por defecto)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
            font_small = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Dibujar contenido
        y_position = 30
        
        # Título
        draw.text((20, y_position), "TARJETA DE EMPLEADO", fill='black', font=font)
        y_position += 40
        
        # Información del empleado
        info_lines = [
            f"Nombre: {employee_data['nombre']}",
            f"ID: {employee_data['id']}",
            f"Departamento: {employee_data['departamento']}",
            f"Salario: ${employee_data['salario']:,}",
            f"Edad: {employee_data['edad']} años",
            f"Ciudad: {employee_data['ciudad']}",
            f"Experiencia: {employee_data['experiencia_anos']} años",
            f"Educación: {employee_data['nivel_educacion']}"
        ]
        
        for line in info_lines:
            draw.text((20, y_position), line, fill='black', font=font_small)
            y_position += 25
        
        # Guardar imagen
        image.save(output_path)
        print(f"✅ Tarjeta de empleado creada: {output_path}")

def create_sample_cards():
    """Crear tarjetas de empleado de muestra"""
    processor = OCRProcessor()
    
    # Cargar datos de empleados
    conn = sqlite3.connect(processor.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empleados LIMIT 3")
    employees = cursor.fetchall()
    conn.close()
    
    # Crear directorio si no existe
    os.makedirs("data/sample_cards", exist_ok=True)
    
    # Crear tarjetas
    for i, employee in enumerate(employees):
        employee_data = {
            'nombre': employee[1],
            'id': employee[0],
            'departamento': employee[2],
            'salario': employee[3],
            'edad': employee[4],
            'ciudad': employee[5],
            'experiencia_anos': employee[6],
            'nivel_educacion': employee[7]
        }
        
        output_path = f"data/sample_cards/empleado_{employee[0]}.png"
        processor.create_sample_card(employee_data, output_path)

def test_ocr():
    """Función de prueba para OCR"""
    processor = OCRProcessor()
    
    # Crear tarjetas de muestra
    print("🖼️ Creando tarjetas de empleado de muestra...")
    create_sample_cards()
    
    # Procesar una tarjeta de muestra
    sample_card_path = "data/sample_cards/empleado_1.png"
    if os.path.exists(sample_card_path):
        with open(sample_card_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode()
        
        print(f"\n🧪 PROCESANDO TARJETA: {sample_card_path}")
        result = processor.process_image(image_base64)
        
        if result['success']:
            print("✅ OCR exitoso:")
            print(f"Texto extraído: {result['texto_extraido'][:100]}...")
            print(f"Datos extraídos: {result['datos_extraidos']}")
            print(f"Validación: {result['validacion']}")
        else:
            print(f"❌ Error en OCR: {result['error']}")

if __name__ == "__main__":
    test_ocr() 