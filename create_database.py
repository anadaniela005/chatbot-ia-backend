import sqlite3
import random
from datetime import datetime, timedelta
import os

def create_database():
    """Crear la base de datos y la tabla de empleados"""
    
    # Asegurar que el directorio data existe
    os.makedirs('data', exist_ok=True)
    
    # Conectar a la base de datos (se crea si no existe)
    conn = sqlite3.connect('data/empresa.db')
    cursor = conn.cursor()
    
    # Crear tabla empleados
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS empleados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            departamento TEXT NOT NULL,
            salario INTEGER NOT NULL,
            edad INTEGER NOT NULL,
            ciudad TEXT NOT NULL,
            experiencia_anos INTEGER NOT NULL,
            nivel_educacion TEXT NOT NULL,
            fecha_ingreso DATE NOT NULL
        )
    ''')
    
    conn.commit()
    print("✅ Tabla 'empleados' creada exitosamente")
    return conn, cursor

def generate_sample_data():
    """Generar datos de empleados realistas"""
    
    # Datos de prueba
    nombres = [
        "Ana García", "Carlos López", "María Rodríguez", "Juan Pérez", "Laura Martínez",
        "Diego Silva", "Sofia Herrera", "Andrés Morales", "Carmen Vega", "Roberto Castro",
        "Patricia Ruiz", "Fernando Torres", "Isabel Mendoza", "Ricardo Jiménez", "Elena Vargas",
        "Miguel Ángel Soto", "Adriana Flores", "José Luis Ríos", "Gabriela Ortega", "Francisco Méndez"
    ]
    
    departamentos = ["Ventas", "IT", "Marketing", "Finanzas", "Recursos Humanos"]
    
    ciudades = ["Ciudad de México", "Guadalajara", "Monterrey", "Puebla", "Tijuana"]
    
    niveles_educacion = ["Licenciatura", "Maestría", "Doctorado", "Técnico"]
    
    empleados = []
    
    for i, nombre in enumerate(nombres):
        # Generar datos aleatorios pero realistas
        departamento = random.choice(departamentos)
        ciudad = random.choice(ciudades)
        nivel_educacion = random.choice(niveles_educacion)
        
        # Edad entre 22 y 55 años
        edad = random.randint(22, 55)
        
        # Experiencia entre 0 y 20 años, pero no más que la edad - 18
        experiencia_max = min(20, edad - 18)
        experiencia_anos = random.randint(0, experiencia_max)
        
        # Salario basado en departamento, experiencia y educación
        salario_base = {
            "Ventas": 35000,
            "IT": 45000,
            "Marketing": 40000,
            "Finanzas": 50000,
            "Recursos Humanos": 38000
        }
        
        # Ajustes por nivel educativo
        ajuste_educacion = {
            "Técnico": 0.8,
            "Licenciatura": 1.0,
            "Maestría": 1.3,
            "Doctorado": 1.6
        }
        
        # Ajuste por experiencia (5% por año)
        ajuste_experiencia = 1 + (experiencia_anos * 0.05)
        
        salario = int(salario_base[departamento] * ajuste_educacion[nivel_educacion] * ajuste_experiencia)
        
        # Asegurar que el salario esté en el rango requerido (25,000 - 90,000)
        salario = max(25000, min(90000, salario))
        
        # Fecha de ingreso en los últimos 5 años
        fecha_actual = datetime.now()
        dias_atras = random.randint(0, 5 * 365)  # Últimos 5 años
        fecha_ingreso = fecha_actual - timedelta(days=dias_atras)
        
        empleados.append((
            nombre,
            departamento,
            salario,
            edad,
            ciudad,
            experiencia_anos,
            nivel_educacion,
            fecha_ingreso.strftime('%Y-%m-%d')
        ))
    
    return empleados

def populate_database(conn, cursor, empleados):
    """Poblar la base de datos con los empleados generados"""
    
    # Limpiar tabla existente
    cursor.execute("DELETE FROM empleados")
    
    # Insertar empleados
    cursor.executemany('''
        INSERT INTO empleados (nombre, departamento, salario, edad, ciudad, 
                              experiencia_anos, nivel_educacion, fecha_ingreso)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', empleados)
    
    conn.commit()
    print(f"✅ {len(empleados)} empleados insertados exitosamente")

def show_database_stats(conn, cursor):
    """Mostrar estadísticas de la base de datos"""
    
    # Total de empleados
    cursor.execute("SELECT COUNT(*) FROM empleados")
    total = cursor.fetchone()[0]
    
    # Estadísticas por departamento
    cursor.execute('''
        SELECT departamento, COUNT(*), AVG(salario), AVG(edad)
        FROM empleados 
        GROUP BY departamento
    ''')
    dept_stats = cursor.fetchall()
    
    # Estadísticas generales
    cursor.execute('''
        SELECT 
            AVG(salario) as salario_promedio,
            MIN(salario) as salario_min,
            MAX(salario) as salario_max,
            AVG(edad) as edad_promedio,
            AVG(experiencia_anos) as exp_promedio
        FROM empleados
    ''')
    general_stats = cursor.fetchone()
    
    print("\n📊 ESTADÍSTICAS DE LA BASE DE DATOS:")
    print(f"Total de empleados: {total}")
    print(f"\nSalario promedio: ${general_stats[0]:,.0f}")
    print(f"Rango de salarios: ${general_stats[1]:,} - ${general_stats[2]:,}")
    print(f"Edad promedio: {general_stats[3]:.1f} años")
    print(f"Experiencia promedio: {general_stats[4]:.1f} años")
    
    print(f"\n📋 POR DEPARTAMENTO:")
    for dept, count, avg_salary, avg_age in dept_stats:
        print(f"  {dept}: {count} empleados, ${avg_salary:,.0f} promedio, {avg_age:.1f} años promedio")

def main():
    """Función principal"""
    print("🚀 Creando base de datos de empleados...")
    
    # Crear base de datos
    conn, cursor = create_database()
    
    # Generar datos de prueba
    print("📝 Generando datos de empleados...")
    empleados = generate_sample_data()
    
    # Poblar base de datos
    print("💾 Insertando empleados en la base de datos...")
    populate_database(conn, cursor, empleados)
    
    # Mostrar estadísticas
    show_database_stats(conn, cursor)
    
    # Cerrar conexión
    conn.close()
    
    print("\n✅ Base de datos creada exitosamente en 'data/empresa.db'")
    print("📁 Estructura del proyecto lista para continuar con el desarrollo")

if __name__ == "__main__":
    main() 