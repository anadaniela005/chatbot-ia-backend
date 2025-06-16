import sqlite3
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pickle
import os

class SalaryPredictor:
    """Modelo de regresión para predecir salarios de empleados"""
    
    def __init__(self):
        self.model = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.model_path = "models/salary_predictor.pkl"
        self.encoders_path = "models/label_encoders.pkl"
        self.scaler_path = "models/scaler.pkl"
        
    def load_data(self):
        """Cargar datos de la base de datos"""
        conn = sqlite3.connect('data/empresa.db')
        query = """
        SELECT edad, experiencia_anos, departamento, nivel_educacion, salario
        FROM empleados
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def prepare_features(self, df):
        """Preparar features para el modelo"""
        # Codificar variables categóricas
        categorical_features = ['departamento', 'nivel_educacion']
        
        for feature in categorical_features:
            if feature not in self.label_encoders:
                self.label_encoders[feature] = LabelEncoder()
                df[f'{feature}_encoded'] = self.label_encoders[feature].fit_transform(df[feature])
            else:
                df[f'{feature}_encoded'] = self.label_encoders[feature].transform(df[feature])
        
        # Features numéricas
        X = df[['edad', 'experiencia_anos', 'departamento_encoded', 'nivel_educacion_encoded']].values
        y = df['salario'].values
        
        return X, y
    
    def train(self):
        """Entrenar el modelo de regresión"""
        print("📊 Entrenando modelo de predicción de salarios...")
        
        # Cargar datos
        df = self.load_data()
        print(f"📈 Datos cargados: {len(df)} empleados")
        
        # Preparar features
        X, y = self.prepare_features(df)
        
        # Dividir en train y test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Escalar features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Entrenar modelo
        self.model = LinearRegression()
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluar modelo
        y_pred_train = self.model.predict(X_train_scaled)
        y_pred_test = self.model.predict(X_test_scaled)
        
        # Calcular métricas
        mae_train = mean_absolute_error(y_train, y_pred_train)
        rmse_train = np.sqrt(mean_squared_error(y_train, y_pred_train))
        r2_train = r2_score(y_train, y_pred_train)
        
        mae_test = mean_absolute_error(y_test, y_pred_test)
        rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
        r2_test = r2_score(y_test, y_pred_test)
        
        print("✅ Entrenamiento completado:")
        print(f"   - MAE (train): ${mae_train:,.0f}")
        print(f"   - RMSE (train): ${rmse_train:,.0f}")
        print(f"   - R² (train): {r2_train:.3f}")
        print(f"   - MAE (test): ${mae_test:,.0f}")
        print(f"   - RMSE (test): ${rmse_test:,.0f}")
        print(f"   - R² (test): {r2_test:.3f}")
        
        # Guardar modelo y encoders
        self.save_model()
        
        return {
            'mae_train': mae_train,
            'rmse_train': rmse_train,
            'r2_train': r2_train,
            'mae_test': mae_test,
            'rmse_test': rmse_test,
            'r2_test': r2_test
        }
    
    def predict(self, edad, experiencia_anos, departamento, nivel_educacion):
        """Predecir salario para un empleado"""
        if self.model is None:
            self.load_model()
        
        # Preparar datos de entrada
        input_data = {
            'edad': [edad],
            'experiencia_anos': [experiencia_anos],
            'departamento': [departamento],
            'nivel_educacion': [nivel_educacion]
        }
        
        df_input = pd.DataFrame(input_data)
        
        # Codificar variables categóricas
        for feature in ['departamento', 'nivel_educacion']:
            if feature in self.label_encoders:
                df_input[f'{feature}_encoded'] = self.label_encoders[feature].transform(df_input[feature])
        
        # Preparar features
        X = df_input[['edad', 'experiencia_anos', 'departamento_encoded', 'nivel_educacion_encoded']].values
        
        # Escalar features
        X_scaled = self.scaler.transform(X)
        
        # Predecir
        salario_predicho = self.model.predict(X_scaled)[0]
        
        # Calcular confianza (basada en R² del modelo)
        confianza = 0.8  # Valor base, se puede ajustar
        
        return {
            'salario_predicho': float(salario_predicho),
            'confianza': confianza,
            'features_usadas': {
                'edad': edad,
                'experiencia_anos': experiencia_anos,
                'departamento': departamento,
                'nivel_educacion': nivel_educacion
            }
        }
    
    def save_model(self):
        """Guardar el modelo y encoders"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        # Guardar modelo
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        # Guardar encoders
        with open(self.encoders_path, 'wb') as f:
            pickle.dump(self.label_encoders, f)
        
        # Guardar scaler
        with open(self.scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        print(f"💾 Modelo guardado en {self.model_path}")
    
    def load_model(self):
        """Cargar el modelo y encoders"""
        if (os.path.exists(self.model_path) and 
            os.path.exists(self.encoders_path) and 
            os.path.exists(self.scaler_path)):
            
            # Cargar modelo
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            # Cargar encoders
            with open(self.encoders_path, 'rb') as f:
                self.label_encoders = pickle.load(f)
            
            # Cargar scaler
            with open(self.scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            
            print(f"📂 Modelo cargado desde {self.model_path}")
        else:
            print("⚠️ Modelo no encontrado. Entrenando nuevo modelo...")
            self.train()
    
    def get_feature_importance(self):
        """Obtener importancia de features"""
        if self.model is None:
            self.load_model()
        
        feature_names = ['edad', 'experiencia_anos', 'departamento', 'nivel_educacion']
        coefficients = self.model.coef_
        
        importance = dict(zip(feature_names, coefficients))
        return importance

def test_regression():
    """Función de prueba para el modelo de regresión"""
    predictor = SalaryPredictor()
    
    # Entrenar el modelo
    metrics = predictor.train()
    
    # Probar algunas predicciones
    test_cases = [
        (30, 5, "IT", "Licenciatura"),
        (40, 10, "Ventas", "Maestría"),
        (25, 2, "Marketing", "Técnico"),
        (35, 8, "Finanzas", "Doctorado")
    ]
    
    print("\n🧪 PRUEBAS DE PREDICCIÓN:")
    for edad, exp, dept, educ in test_cases:
        result = predictor.predict(edad, exp, dept, educ)
        print(f"Edad: {edad}, Exp: {exp} años, Dept: {dept}, Educ: {educ}")
        print(f"  Salario predicho: ${result['salario_predicho']:,.0f}")
        print(f"  Confianza: {result['confianza']:.3f}")
        print()
    
    # Mostrar importancia de features
    importance = predictor.get_feature_importance()
    print("📊 IMPORTANCIA DE FEATURES:")
    for feature, coef in importance.items():
        print(f"  {feature}: {coef:.2f}")

if __name__ == "__main__":
    test_regression() 