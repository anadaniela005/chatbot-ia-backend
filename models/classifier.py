import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import pickle
import os

class IntentClassifier:
    """Clasificador de intenciones para el chatbot"""
    
    def __init__(self):
        self.pipeline = None
        self.categories = [
            "conteo", "busqueda_max", "estadistica", "filtro", "busqueda_min", "prediccion"
        ]
        self.model_path = "models/intent_classifier.pkl"
        
    def create_training_data(self):
        """Crear datos de entrenamiento para el clasificador"""
        
        training_data = {
            "conteo": [
                "¿Cuántos empleados hay?",
                "¿Cuántos trabajadores tenemos?",
                "¿Cuál es el total de empleados?",
                "¿Cuánta gente trabaja aquí?",
                "¿Cuántos hay en total?",
                "¿Cuántos empleados hay en la empresa?",
                "¿Cuántos trabajadores hay?",
                "¿Cuál es el número total de empleados?"
            ],
            "busqueda_max": [
                "¿Quién gana más?",
                "¿Quién es el empleado mejor pagado?",
                "¿Cuál es el salario más alto?",
                "¿Quién tiene el sueldo más alto?",
                "¿Quién gana más dinero?",
                "¿Cuál es el empleado con mayor salario?",
                "¿Quién es el que más gana?",
                "¿Cuál es el sueldo máximo?"
            ],
            "estadistica": [
                "¿Cuál es el promedio de edad?",
                "¿Cuál es la edad promedio?",
                "¿Cuál es el salario promedio?",
                "¿Cuál es el sueldo promedio?",
                "¿Cuál es la experiencia promedio?",
                "¿Cuál es el promedio de experiencia?",
                "¿Cuál es la media de edad?",
                "¿Cuál es el promedio de salarios?"
            ],
            "filtro": [
                "¿Cuántos empleados hay en ventas?",
                "¿Cuántos trabajadores hay en IT?",
                "¿Cuántos empleados hay en marketing?",
                "¿Cuántos hay en finanzas?",
                "¿Cuántos empleados hay en recursos humanos?",
                "¿Cuántos trabajadores hay en el departamento de ventas?",
                "¿Cuántos empleados trabajan en IT?",
                "¿Cuántos hay en el área de marketing?"
            ],
            "busqueda_min": [
                "¿Quién es el más joven?",
                "¿Quién es el empleado más joven?",
                "¿Quién tiene menos edad?",
                "¿Quién es el más nuevo?",
                "¿Quién es el empleado con menos experiencia?",
                "¿Quién tiene menos años de experiencia?",
                "¿Quién es el más reciente?",
                "¿Quién es el empleado más reciente?"
            ],
            "prediccion": [
                "¿Cuánto ganaría un empleado de 30 años en IT?",
                "¿Cuál sería el salario de alguien con maestría en marketing?",
                "¿Cuánto ganaría alguien de 25 años con 3 años de experiencia?",
                "¿Cuál sería el sueldo de un empleado de 40 años en ventas?",
                "¿Cuánto ganaría alguien con doctorado en finanzas?",
                "¿Cuál sería el salario de un técnico de 28 años?",
                "¿Cuánto ganaría un empleado con licenciatura y 5 años de experiencia?",
                "¿Cuál sería el sueldo de alguien de 35 años en recursos humanos?"
            ]
        }
        
        X = []  # Preguntas
        y = []  # Categorías
        
        for category, questions in training_data.items():
            for question in questions:
                X.append(question.lower())
                y.append(category)
        
        return X, y
    
    def train(self):
        """Entrenar el clasificador"""
        print("🤖 Entrenando clasificador de intenciones...")
        
        # Crear datos de entrenamiento
        X, y = self.create_training_data()
        
        # Dividir en train y test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Crear pipeline con TF-IDF y Naive Bayes
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words=['el', 'la', 'los', 'las', 'de', 'del', 'en', 'con', 'por', 'para', 'a', 'al', 'se', 'es', 'son', 'está', 'están', 'hay', 'tiene', 'tienen', 'cuál', 'cuántos', 'quién', 'qué', 'cómo', 'dónde', 'cuándo', 'por qué']
            )),
            ('classifier', MultinomialNB())
        ])
        
        # Entrenar el modelo
        self.pipeline.fit(X_train, y_train)
        
        # Evaluar el modelo
        train_score = self.pipeline.score(X_train, y_train)
        test_score = self.pipeline.score(X_test, y_test)
        
        print(f"✅ Entrenamiento completado:")
        print(f"   - Precisión en entrenamiento: {train_score:.3f}")
        print(f"   - Precisión en prueba: {test_score:.3f}")
        
        # Guardar el modelo
        self.save_model()
        
        return train_score, test_score
    
    def predict(self, question):
        """Predecir la intención de una pregunta"""
        if self.pipeline is None:
            self.load_model()
        
        # Preprocesar la pregunta
        question_clean = question.lower().strip()
        
        # Predecir
        prediction = self.pipeline.predict([question_clean])[0]
        
        # Obtener probabilidades
        probabilities = self.pipeline.predict_proba([question_clean])[0]
        confidence = max(probabilities)
        
        return {
            "categoria": prediction,
            "confianza": float(confidence),
            "probabilidades": dict(zip(self.categories, probabilities.tolist()))
        }
    
    def save_model(self):
        """Guardar el modelo entrenado"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.pipeline, f)
        print(f"💾 Modelo guardado en {self.model_path}")
    
    def load_model(self):
        """Cargar el modelo entrenado"""
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                self.pipeline = pickle.load(f)
            print(f"📂 Modelo cargado desde {self.model_path}")
        else:
            print("⚠️ Modelo no encontrado. Entrenando nuevo modelo...")
            self.train()

def test_classifier():
    """Función de prueba para el clasificador"""
    classifier = IntentClassifier()
    
    # Entrenar el modelo
    classifier.train()
    
    # Probar algunas preguntas
    test_questions = [
        "¿Cuántos empleados hay?",
        "¿Quién gana más?",
        "¿Cuál es el promedio de edad?",
        "¿Cuántos empleados hay en ventas?",
        "¿Quién es el más joven?",
        "¿Cuánto ganaría un empleado de 30 años en IT?"
    ]
    
    print("\n🧪 PRUEBAS DEL CLASIFICADOR:")
    for question in test_questions:
        result = classifier.predict(question)
        print(f"Pregunta: {question}")
        print(f"  Categoría: {result['categoria']}")
        print(f"  Confianza: {result['confianza']:.3f}")
        print()

if __name__ == "__main__":
    test_classifier() 