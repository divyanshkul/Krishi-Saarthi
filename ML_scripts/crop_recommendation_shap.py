import pandas as pd

import numpy as np

import requests

from datetime import datetime

from sklearn.ensemble import RandomForestRegressor

from sklearn.model_selection import train_test_split

from sklearn.preprocessing import LabelEncoder

from sklearn.metrics import r2_score, mean_absolute_error

import shap

import joblib

import warnings

warnings.filterwarnings('ignore')



class WeatherEnhancedCropSystem:

    def __init__(self, crop_df):

        Complete system: Weather Intelligence + Crop Prediction + SHAP Explainability

        

        Args:

            crop_df: Your crop yield dataset (pandas DataFrame)

        self.df = crop_df

        self.model = None

        self.encoders = {}

        self.scaler = None

        self.feature_names = []

        self.shap_explainer = None

        

        

        self._clean_dataset()

        

       

        self.state_cities = {

            'Assam': 'Guwahati', 'Punjab': 'Chandigarh', 'Maharashtra': 'Mumbai',

            'Karnataka': 'Bengaluru', 'Tamil Nadu': 'Chennai', 'West Bengal': 'Kolkata',

            'Uttar Pradesh': 'Lucknow', 'Gujarat': 'Ahmedabad', 'Rajasthan': 'Jaipur',

            'Odisha': 'Bhubaneswar', 'Andhra Pradesh': 'Hyderabad', 'Kerala': 'Kochi',

            'Haryana': 'Gurugram', 'Madhya Pradesh': 'Bhopal', 'Bihar': 'Patna'

        }

    

    def _clean_dataset(self):

        print("Cleaning dataset...")

        

        string_columns = ['Crop', 'Season', 'State']

        for col in string_columns:

            if col in self.df.columns:

                self.df[col] = self.df[col].astype(str).str.strip()

        

        initial_rows = len(self.df)

        self.df = self.df.dropna()

        

        

        

        print(f"Cleaned dataset: {len(self.df)} records (removed {initial_rows - len(self.df)} outliers)")

    

    def get_live_weather(self, state):

        city = self.state_cities.get(state)

        if not city:

            return None

        

        url = f"https://wttr.in/{city}?format=j1"

        

        try:

            print(f"Fetching live weather for {city}...")

            response = requests.get(url, timeout=8)

            response.raise_for_status()

            data = response.json()

            

            current = data['current_condition'][0]

            today = data['weather'][0]

            

            weather_data = {

                'city': city,

                'temperature_c': float(current['temp_C']),

                'humidity': int(current['humidity']),

                'weather_desc': current['weatherDesc'][0]['value'],

                'precipitation_mm': float(current.get('precipMM', 0)),

                'wind_speed_kmh': float(current['windspeedKmph']),

                'max_temp_c': float(today['maxtempC']),

                'min_temp_c': float(today['mintempC'])

            }

            

            print(f"Live weather: {weather_data['temperature_c']}°C, {weather_data['weather_desc']}")

            return weather_data

            

        except requests.RequestException as e:

            print(f"Weather fetch failed: {e}")

            return None

    

    def get_historical_data_and_optimization(self, state, season, area):

        print(f"Analyzing historical data for {state} + {season}...")

        

        filtered_data = self.df[

            (self.df['State'] == state) & 

            (self.df['Season'] == season)

        ]

        

        if len(filtered_data) > 0:

            top_quartile_yield = filtered_data['Yield'].quantile(0.75)

            top_performers = filtered_data[filtered_data['Yield'] >= top_quartile_yield]

            

            optimal_fertilizer_per_ha = (top_performers['Fertilizer'] / top_performers['Area']).mean()

            optimal_pesticide_per_ha = (top_performers['Pesticide'] / top_performers['Area']).mean()

            

            historical = {

                'avg_rainfall_mm': round(filtered_data['Annual_Rainfall'].mean(), 1),

                'sample_size': len(filtered_data),

                'confidence': min(len(filtered_data) / 100, 1.0),

                'optimal_fertilizer_per_ha': round(optimal_fertilizer_per_ha, 1),

                'optimal_pesticide_per_ha': round(optimal_pesticide_per_ha, 3),

                'optimal_fertilizer_total': round(optimal_fertilizer_per_ha * area, 1),

                'optimal_pesticide_total': round(optimal_pesticide_per_ha * area, 3),

                'top_performers_count': len(top_performers),

                'avg_top_yield': round(top_performers['Yield'].mean(), 2)

            }

            

            print(f"Found {historical['sample_size']} records, {historical['top_performers_count']} top performers")

            

        else:

            state_data = self.df[self.df['State'] == state]

            if len(state_data) > 0:

                optimal_fert_per_ha = (state_data['Fertilizer'] / state_data['Area']).mean()

                optimal_pest_per_ha = (state_data['Pesticide'] / state_data['Area']).mean()

                

                historical = {

                    'avg_rainfall_mm': round(state_data['Annual_Rainfall'].mean(), 1),

                    'optimal_fertilizer_total': round(optimal_fert_per_ha * area, 1),

                    'optimal_pesticide_total': round(optimal_pest_per_ha * area, 3),

                    'confidence': 0.6

                }

            else:

                overall_fert_per_ha = (self.df['Fertilizer'] / self.df['Area']).mean()

                overall_pest_per_ha = (self.df['Pesticide'] / self.df['Area']).mean()

                

                historical = {

                    'avg_rainfall_mm': round(self.df['Annual_Rainfall'].mean(), 1),

                    'optimal_fertilizer_total': round(overall_fert_per_ha * area, 1),

                    'optimal_pesticide_total': round(overall_pest_per_ha * area, 3),

                    'confidence': 0.3

                }

        

        return historical

    

    def estimate_seasonal_rainfall(self, live_weather, historical_data):

        base_rainfall = historical_data['avg_rainfall_mm']

        

        if not live_weather:

            return base_rainfall, 'Historical average'

        

        adjustment_factor = 1.0

        current_precip = live_weather['precipitation_mm']

        

        if current_precip > 10:

            adjustment_factor = 1.15

        elif current_precip > 5:

            adjustment_factor = 1.08

        elif current_precip < 0.1:

            adjustment_factor = 0.95

        

        estimated_rainfall = round(base_rainfall * adjustment_factor, 1)

        return estimated_rainfall, f'Historical + live weather adjustment'

    

    def train_crop_model(self):

        print(f"\nTraining crop prediction model...")

        

        self.df['Fertilizer_per_hectare'] = self.df['Fertilizer'] / self.df['Area']

        self.df['Pesticide_per_hectare'] = self.df['Pesticide'] / self.df['Area']

        

        self.encoders['State'] = LabelEncoder()

        self.encoders['Season'] = LabelEncoder() 

        self.encoders['Crop'] = LabelEncoder()

        

        self.df['State_Encoded'] = self.encoders['State'].fit_transform(self.df['State'])

        self.df['Season_Encoded'] = self.encoders['Season'].fit_transform(self.df['Season'])

        self.df['Crop_Encoded'] = self.encoders['Crop'].fit_transform(self.df['Crop'])

        

        self.feature_names = [

            'State_Encoded', 'Season_Encoded', 'Crop_Encoded',

            'Area', 'Annual_Rainfall', 'Fertilizer', 'Pesticide',

            'Fertilizer_per_hectare', 'Pesticide_per_hectare'

        ]

        

        

        X = self.df[self.feature_names]

        y = self.df['Yield']

        

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        

        self.model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42)

        self.model.fit(X_train, y_train)

        

        train_pred = self.model.predict(X_train)

        test_pred = self.model.predict(X_test)

        

        train_r2 = r2_score(y_train, train_pred)

        test_r2 = r2_score(y_test, test_pred)

        test_mae = mean_absolute_error(y_test, test_pred)

        

        print(f"Model trained successfully!")

        print(f"   Training R²: {train_r2:.4f}")

        print(f"   Test R²: {test_r2:.4f}")

        print(f"   Test MAE: {test_mae:.3f} tons/hectare")

        

        print(f"Initializing SHAP explainer...")

        self.shap_explainer = shap.TreeExplainer(self.model)

        print(f"SHAP explainer ready!")

        

        return X_train, X_test, y_train, y_test

    

    def predict_crop_yield_with_shap(self, state, season, crop, area, annual_rainfall, fertilizer, pesticide):

        Predict crop yield and generate SHAP explanations

        

        Returns:

            Dict with prediction and SHAP explanation

        try:

            state_encoded = self.encoders['State'].transform([state])[0]

            season_encoded = self.encoders['Season'].transform([season])[0]

            crop_encoded = self.encoders['Crop'].transform([crop])[0]

            

            features = np.array([

                state_encoded, season_encoded, crop_encoded,

                area, annual_rainfall, fertilizer, pesticide,

                fertilizer / area,
                pesticide / area
            ]).reshape(1, -1)

            

            predicted_yield = self.model.predict(features)[0]

            

            shap_values = self.shap_explainer.shap_values(features)

            

            base_value = self.shap_explainer.expected_value

            if hasattr(base_value, 'item'):

                base_value = base_value.item()

            elif isinstance(base_value, (list, np.ndarray)):

                base_value = float(base_value[0] if len(base_value) > 0 else base_value)

            

            shap_explanation = {

                'base_yield': base_value,

                'predicted_yield': predicted_yield,

                'feature_contributions': {

                    'state': float(shap_values[0][0]),

                    'season': float(shap_values[0][1]), 

                    'crop_type': float(shap_values[0][2]),

                    'area': float(shap_values[0][3]),

                    'rainfall': float(shap_values[0][4]),

                    'fertilizer': float(shap_values[0][5]),

                    'pesticide': float(shap_values[0][6]),

                    'fertilizer_per_ha': float(shap_values[0][7]),

                    'pesticide_per_ha': float(shap_values[0][8])

                }

            }

            

            return {

                'crop': crop,

                'predicted_yield': round(predicted_yield, 2),

                'shap_explanation': shap_explanation,

                'success': True

            }

            

        except ValueError as e:

            return {'success': False, 'error': str(e)}

    

    def get_crop_recommendations_with_shap(self, state, season, area, annual_rainfall, fertilizer, pesticide, top_n=5):

        Get crop recommendations with SHAP explanations for each

        print(f"\n Generating crop recommendations with SHAP explanations...")

        

        recommendations = []

        crop_list = list(self.encoders['Crop'].classes_)

        

        for crop in crop_list:

            result = self.predict_crop_yield_with_shap(

                state, season, crop, area, annual_rainfall, fertilizer, pesticide

            )

            

            if result['success'] and result['predicted_yield'] > 0:

                recommendations.append(result)

        

        recommendations.sort(key=lambda x: x['predicted_yield'], reverse=True)

        

        return recommendations[:top_n]

    

    def generate_natural_language_explanation(self, shap_explanation, crop):

        Convert SHAP values to natural language explanations

        contributions = shap_explanation['feature_contributions']

        base_yield = shap_explanation['base_yield']

        predicted_yield = shap_explanation['predicted_yield']

        

        if hasattr(base_yield, 'item'):

            base_yield = base_yield.item()

        elif isinstance(base_yield, (list, np.ndarray)):

            base_yield = float(base_yield[0] if len(base_yield) > 0 else base_yield)

        

        sorted_contributions = sorted(

            contributions.items(), 

            key=lambda x: abs(x[1]), 

            reverse=True

        )

        

        explanation_text = f"🌾 {crop} is predicted to yield {predicted_yield:.2f} tons/hectare\n"

        explanation_text += f"   (Base model prediction: {base_yield:.2f} tons/hectare)\n\n"

        explanation_text += "Key factors influencing this prediction:\n"

        

        for feature, contribution in sorted_contributions[:5]:
            if abs(contribution) > 0.01:
                direction = "increases" if contribution > 0 else "decreases"

                

                if feature == 'rainfall':

                    explanation_text += f"   Rainfall conditions {direction} yield by {abs(contribution):.2f} tons/hectare\n"

                elif feature == 'fertilizer':

                    explanation_text += f"   Fertilizer amount {direction} yield by {abs(contribution):.2f} tons/hectare\n"

                elif feature == 'state':

                    explanation_text += f"   Regional conditions {direction} yield by {abs(contribution):.2f} tons/hectare\n"

                elif feature == 'season':

                    explanation_text += f"   Seasonal factors {direction} yield by {abs(contribution):.2f} tons/hectare\n"

                elif feature == 'crop_type':

                    explanation_text += f"   Crop characteristics {direction} yield by {abs(contribution):.2f} tons/hectare\n"

                elif feature == 'fertilizer_per_ha':

                    explanation_text += f"    Fertilizer efficiency {direction} yield by {abs(contribution):.2f} tons/hectare\n"

                elif feature == 'pesticide_per_ha':

                    explanation_text += f"   Pest management {direction} yield by {abs(contribution):.2f} tons/hectare\n"

                else:

                    explanation_text += f"   • {feature.title()} {direction} yield by {abs(contribution):.2f} tons/hectare\n"

        

        return explanation_text

    

    def display_shap_recommendations(self, recommendations):

        Display crop recommendations with detailed SHAP explanations

        print(f"\n TOP CROP RECOMMENDATIONS WITH AI EXPLANATIONS")

        print("=" * 80)

        

        for i, rec in enumerate(recommendations, 1):

            print(f"\n{i}. {rec['crop'].upper()}")

            print("-" * 50)

            

            explanation = self.generate_natural_language_explanation(

                rec['shap_explanation'], rec['crop']

            )

            print(explanation)

            

            contributions = rec['shap_explanation']['feature_contributions']

            positive_factors = [(k, v) for k, v in contributions.items() if v > 0.01]

            negative_factors = [(k, v) for k, v in contributions.items() if v < -0.01]

            

            if positive_factors:

                print("Positive factors:")

                for factor, value in sorted(positive_factors, key=lambda x: x[1], reverse=True)[:3]:

                    print(f"   • {factor.replace('_', ' ').title()}: +{value:.3f}")

            

            if negative_factors:

                print("Limiting factors:")

                for factor, value in sorted(negative_factors, key=lambda x: x[1])[:3]:

                    print(f"   • {factor.replace('_', ' ').title()}: {value:.3f}")

            

            base_yield = rec['shap_explanation']['base_yield']

            predicted_yield = rec['predicted_yield']

            

            if hasattr(base_yield, 'item'):

                base_yield = base_yield.item()

            elif isinstance(base_yield, (list, np.ndarray)):

                base_yield = float(base_yield[0] if len(base_yield) > 0 else base_yield)

            

            confidence = 'High' if abs(predicted_yield - base_yield) < 1 else 'Medium'

            print(f"\n Confidence: {confidence}")

            print(f" Prediction vs baseline: {predicted_yield:.2f} vs {base_yield:.2f}")

    

    def complete_recommendation_system(self, state, season, area):

        Complete system: Weather Intelligence → Resource Optimization → Crop Prediction → SHAP Explanations

        print(f"\nCOMPLETE AI CROP RECOMMENDATION SYSTEM")

        print("=" * 80)

        print(f"Location: {state} ({season} season)")

        print(f"Farm Area: {area} hectares")

        

        live_weather = self.get_live_weather(state)

        historical_data = self.get_historical_data_and_optimization(state, season, area)

        

        estimated_rainfall, reasoning = self.estimate_seasonal_rainfall(live_weather, historical_data)

        

        optimal_fertilizer = historical_data['optimal_fertilizer_total']

        optimal_pesticide = historical_data['optimal_pesticide_total']

        

        print(f"\nWEATHER INTELLIGENCE:")

        if live_weather:

            print(f"   Current: {live_weather['temperature_c']}°C, {live_weather['weather_desc']}")

        print(f"   Estimated seasonal rainfall: {estimated_rainfall} mm")

        print(f"   Reasoning: {reasoning}")

        

        print(f"\n🌱 OPTIMIZED RESOURCE USAGE:")

        print(f"   Fertilizer: {optimal_fertilizer} kg total")

        print(f"   Pesticide: {optimal_pesticide} kg total")

        print(f"   Based on top performers from {historical_data.get('sample_size', 'N/A')} historical records")

        

        recommendations = self.get_crop_recommendations_with_shap(

            state, season, area, estimated_rainfall, optimal_fertilizer, optimal_pesticide

        )

        

        self.display_shap_recommendations(recommendations)

        

        return {

            'weather_data': live_weather,

            'historical_data': historical_data,

            'estimated_rainfall': estimated_rainfall,

            'optimal_fertilizer': optimal_fertilizer,

            'optimal_pesticide': optimal_pesticide,

            'recommendations': recommendations

        }



def demo_complete_system():

    Demo the complete integrated system

    print(" COMPLETE AI CROP RECOMMENDATION SYSTEM DEMO")

    print("Weather Intelligence + Resource Optimization + ML Prediction + SHAP Explanations")

    print("=" * 90)

    

    try:

        df = pd.read_csv('crop_yield.csv')

        print(f"Loaded dataset: {len(df)} records")

    except FileNotFoundError:

        print(" Dataset not found. Please check the dataset path")

        return

    

    system = WeatherEnhancedCropSystem(df)

    

    system.train_crop_model()

    

    test_cases = [

        {'state': 'Assam', 'season': 'Kharif', 'area': 5.0},

        {'state': 'Punjab', 'season': 'Rabi', 'area': 3.0},

    ]

    

    for i, test in enumerate(test_cases, 1):

        print(f"\n" + "="*100)

        print(f"DEMO CASE {i}")

        print("="*100)

        

        results = system.complete_recommendation_system(**test)

        

        print(f"\n SYSTEM SUMMARY:")

        print(f"   Weather confidence: {results['historical_data'].get('confidence', 0.5):.1%}")

        print(f"   Top recommendation: {results['recommendations'][0]['crop']} ({results['recommendations'][0]['predicted_yield']:.2f} tons/hectare)")

        print(f"   AI explanation: Transparent SHAP-based reasoning provided")



if __name__ == "__main__":

    demo_complete_system()