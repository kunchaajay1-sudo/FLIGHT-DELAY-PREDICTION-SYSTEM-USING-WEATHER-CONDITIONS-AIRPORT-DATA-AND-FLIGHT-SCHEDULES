"""
Flight Analytics Utilities
Generates detailed analytical datasets and insights for flight delay prediction
"""

import numpy as np
import pandas as pd
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

def generate_flight_delay_dataset(n_samples=1000, random_state=42):
    """Generate synthetic flight delay dataset"""
    np.random.seed(random_state)
    
    data = {
        'Flight_Number': [f'FL{i:04d}' for i in range(n_samples)],
        'Airline': np.random.choice(['United', 'Delta', 'American', 'Southwest', 'JetBlue'], n_samples),
        'Departure_Airport': np.random.choice(['JFK', 'LAX', 'ORD', 'ATL', 'DFW'], n_samples),
        'Arrival_Airport': np.random.choice(['JFK', 'LAX', 'ORD', 'ATL', 'DFW'], n_samples),
        'Day_of_Week': np.random.randint(1, 8, n_samples),
        'Month': np.random.randint(1, 13, n_samples),
        'Hour_of_Day': np.random.randint(0, 24, n_samples),
        'Distance_Miles': np.random.randint(200, 3000, n_samples),
        'Temperature_F': np.random.uniform(32, 95, n_samples),
        'Wind_Speed_mph': np.random.uniform(0, 40, n_samples),
        'Precipitation_inches': np.random.uniform(0, 2, n_samples),
        'Visibility_miles': np.random.uniform(1, 10, n_samples),
        'Cloud_Cover_percent': np.random.uniform(0, 100, n_samples),
        'Departure_Delay_minutes': np.random.randint(-10, 60, n_samples),
        'Airport_Congestion_percent': np.random.uniform(0, 100, n_samples),
        'Runway_Availability_count': np.random.randint(1, 5, n_samples),
        'Aircraft_Age_years': np.random.randint(1, 25, n_samples),
        'Previous_Flight_Delay_minutes': np.random.randint(-10, 120, n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Generate delay target
    delay_prob = 0.3
    delay_prob += (df['Wind_Speed_mph'] / 40) * 0.2
    delay_prob += (df['Precipitation_inches'] / 2) * 0.2
    delay_prob += (df['Airport_Congestion_percent'] / 100) * 0.2
    delay_prob += (df['Departure_Delay_minutes'] / 60) * 0.15
    delay_prob += (np.abs(df['Visibility_miles'] - 5) / 10) * 0.15
    delay_prob = np.minimum(delay_prob, 0.95)
    
    df['Delayed'] = (np.random.random(n_samples) < delay_prob).astype(int)
    df['Actual_Delay_minutes'] = np.where(
        df['Delayed'] == 1,
        np.random.exponential(scale=25, size=n_samples) + 15,
        0
    ).astype(int)
    
    return df

def analyze_delay_by_airline(df):
    """Analyze delay statistics by airline"""
    print("[1] Analyzing delays by airline...")
    
    stats = []
    for airline in df['Airline'].unique():
        subset = df[df['Airline'] == airline]
        delayed = subset[subset['Delayed'] == 1]
        
        stats.append({
            'Airline': airline,
            'Total_Flights': len(subset),
            'Delayed_Flights': len(delayed),
            'Delay_Rate': len(delayed) / len(subset),
            'Avg_Delay_Minutes': delayed['Actual_Delay_minutes'].mean() if len(delayed) > 0 else 0,
            'Max_Delay_Minutes': delayed['Actual_Delay_minutes'].max() if len(delayed) > 0 else 0,
            'Min_Delay_Minutes': delayed['Actual_Delay_minutes'].min() if len(delayed) > 0 else 0
        })
    
    stats_df = pd.DataFrame(stats).sort_values('Delay_Rate', ascending=False)
    stats_df.to_csv('/home/ubuntu/delay_by_airline_stats.csv', index=False)
    print("✓ Saved: delay_by_airline_stats.csv")
    return stats_df

def analyze_delay_by_airport(df):
    """Analyze delay statistics by airport"""
    print("[2] Analyzing delays by airport...")
    
    stats = []
    for airport in df['Departure_Airport'].unique():
        subset = df[df['Departure_Airport'] == airport]
        delayed = subset[subset['Delayed'] == 1]
        
        stats.append({
            'Airport': airport,
            'Total_Departures': len(subset),
            'Delayed_Departures': len(delayed),
            'Delay_Rate': len(delayed) / len(subset),
            'Avg_Delay_Minutes': delayed['Actual_Delay_minutes'].mean() if len(delayed) > 0 else 0,
            'Avg_Congestion': subset['Airport_Congestion_percent'].mean()
        })
    
    stats_df = pd.DataFrame(stats).sort_values('Delay_Rate', ascending=False)
    stats_df.to_csv('/home/ubuntu/delay_by_airport_stats.csv', index=False)
    print("✓ Saved: delay_by_airport_stats.csv")
    return stats_df

def analyze_weather_impact(df):
    """Analyze weather impact on delays"""
    print("[3] Analyzing weather impact...")
    
    # Categorize weather conditions
    df_weather = df.copy()
    
    # Wind speed categories
    df_weather['Wind_Category'] = pd.cut(df_weather['Wind_Speed_mph'], 
                                         bins=[0, 10, 20, 30, 40],
                                         labels=['Light', 'Moderate', 'Strong', 'Severe'])
    
    # Precipitation categories
    df_weather['Precipitation_Category'] = pd.cut(df_weather['Precipitation_inches'],
                                                   bins=[0, 0.1, 0.5, 1.0, 2.0],
                                                   labels=['None', 'Light', 'Moderate', 'Heavy'])
    
    # Visibility categories
    df_weather['Visibility_Category'] = pd.cut(df_weather['Visibility_miles'],
                                               bins=[0, 3, 5, 8, 10],
                                               labels=['Poor', 'Fair', 'Good', 'Excellent'])
    
    stats = []
    
    # Wind impact
    for wind_cat in ['Light', 'Moderate', 'Strong', 'Severe']:
        subset = df_weather[df_weather['Wind_Category'] == wind_cat]
        if len(subset) > 0:
            delayed = subset[subset['Delayed'] == 1]
            stats.append({
                'Weather_Factor': f'Wind: {wind_cat}',
                'Sample_Count': len(subset),
                'Delay_Rate': len(delayed) / len(subset),
                'Avg_Delay_Minutes': delayed['Actual_Delay_minutes'].mean() if len(delayed) > 0 else 0
            })
    
    # Precipitation impact
    for precip_cat in ['None', 'Light', 'Moderate', 'Heavy']:
        subset = df_weather[df_weather['Precipitation_Category'] == precip_cat]
        if len(subset) > 0:
            delayed = subset[subset['Delayed'] == 1]
            stats.append({
                'Weather_Factor': f'Precipitation: {precip_cat}',
                'Sample_Count': len(subset),
                'Delay_Rate': len(delayed) / len(subset),
                'Avg_Delay_Minutes': delayed['Actual_Delay_minutes'].mean() if len(delayed) > 0 else 0
            })
    
    stats_df = pd.DataFrame(stats)
    stats_df.to_csv('/home/ubuntu/weather_impact_stats.csv', index=False)
    print("✓ Saved: weather_impact_stats.csv")
    return stats_df

def analyze_temporal_patterns(df):
    """Analyze temporal patterns in delays"""
    print("[4] Analyzing temporal patterns...")
    
    stats = []
    
    # By day of week
    day_names = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 
                 5: 'Friday', 6: 'Saturday', 7: 'Sunday'}
    
    for day in range(1, 8):
        subset = df[df['Day_of_Week'] == day]
        delayed = subset[subset['Delayed'] == 1]
        
        stats.append({
            'Time_Period': f'Day: {day_names[day]}',
            'Total_Flights': len(subset),
            'Delayed_Flights': len(delayed),
            'Delay_Rate': len(delayed) / len(subset) if len(subset) > 0 else 0,
            'Avg_Delay_Minutes': delayed['Actual_Delay_minutes'].mean() if len(delayed) > 0 else 0
        })
    
    # By hour of day
    for hour in [6, 12, 18, 24]:
        subset = df[df['Hour_of_Day'] == hour]
        if len(subset) > 0:
            delayed = subset[subset['Delayed'] == 1]
            stats.append({
                'Time_Period': f'Hour: {hour:02d}:00',
                'Total_Flights': len(subset),
                'Delayed_Flights': len(delayed),
                'Delay_Rate': len(delayed) / len(subset),
                'Avg_Delay_Minutes': delayed['Actual_Delay_minutes'].mean() if len(delayed) > 0 else 0
            })
    
    stats_df = pd.DataFrame(stats)
    stats_df.to_csv('/home/ubuntu/temporal_patterns_stats.csv', index=False)
    print("✓ Saved: temporal_patterns_stats.csv")
    return stats_df

def generate_operational_insights(df):
    """Generate operational insights"""
    print("[5] Generating operational insights...")
    
    insights = []
    
    # Overall statistics
    insights.append(f"Total Flights Analyzed: {len(df)}")
    insights.append(f"Delayed Flights: {(df['Delayed'] == 1).sum()} ({(df['Delayed'] == 1).sum() / len(df) * 100:.1f}%)")
    insights.append(f"On-Time Flights: {(df['Delayed'] == 0).sum()} ({(df['Delayed'] == 0).sum() / len(df) * 100:.1f}%)")
    
    # Average delays
    delayed_flights = df[df['Delayed'] == 1]
    insights.append(f"\nAverage Delay Duration: {delayed_flights['Actual_Delay_minutes'].mean():.1f} minutes")
    insights.append(f"Maximum Delay: {delayed_flights['Actual_Delay_minutes'].max()} minutes")
    insights.append(f"Minimum Delay: {delayed_flights['Actual_Delay_minutes'].min()} minutes")
    
    # Weather correlation
    high_wind = df[df['Wind_Speed_mph'] > 20]
    high_wind_delay_rate = (high_wind['Delayed'] == 1).sum() / len(high_wind)
    insights.append(f"\nDelay Rate with High Wind (>20 mph): {high_wind_delay_rate:.1%}")
    
    heavy_precip = df[df['Precipitation_inches'] > 0.5]
    heavy_precip_delay_rate = (heavy_precip['Delayed'] == 1).sum() / len(heavy_precip) if len(heavy_precip) > 0 else 0
    insights.append(f"Delay Rate with Heavy Precipitation (>0.5 in): {heavy_precip_delay_rate:.1%}")
    
    # Congestion impact
    high_congestion = df[df['Airport_Congestion_percent'] > 75]
    high_congestion_delay_rate = (high_congestion['Delayed'] == 1).sum() / len(high_congestion)
    insights.append(f"Delay Rate with High Airport Congestion (>75%): {high_congestion_delay_rate:.1%}")
    
    # Airline performance
    best_airline = df.groupby('Airline')['Delayed'].apply(lambda x: (x == 0).sum() / len(x)).idxmax()
    worst_airline = df.groupby('Airline')['Delayed'].apply(lambda x: (x == 1).sum() / len(x)).idxmax()
    
    insights.append(f"\nBest Performing Airline: {best_airline}")
    insights.append(f"Worst Performing Airline: {worst_airline}")
    
    # Write insights to file
    with open('/home/ubuntu/flight_operational_insights.txt', 'w') as f:
        f.write("FLIGHT DELAY PREDICTION SYSTEM - OPERATIONAL INSIGHTS\n")
        f.write("="*60 + "\n\n")
        for insight in insights:
            f.write(insight + "\n")
    
    print("✓ Saved: flight_operational_insights.txt")
    return insights

def generate_delay_predictions(df, n_predictions=20):
    """Generate sample delay predictions for different flight scenarios"""
    print("[6] Generating sample delay predictions...")
    
    predictions = []
    
    scenarios = [
        {'Airline': 'United', 'Departure_Airport': 'JFK', 'Wind_Speed_mph': 5, 'Precipitation_inches': 0, 'Airport_Congestion_percent': 30},
        {'Airline': 'Delta', 'Departure_Airport': 'LAX', 'Wind_Speed_mph': 25, 'Precipitation_inches': 0.5, 'Airport_Congestion_percent': 80},
        {'Airline': 'American', 'Departure_Airport': 'ORD', 'Wind_Speed_mph': 35, 'Precipitation_inches': 1.5, 'Airport_Congestion_percent': 90},
        {'Airline': 'Southwest', 'Departure_Airport': 'ATL', 'Wind_Speed_mph': 10, 'Precipitation_inches': 0.1, 'Airport_Congestion_percent': 50},
        {'Airline': 'JetBlue', 'Departure_Airport': 'DFW', 'Wind_Speed_mph': 15, 'Precipitation_inches': 0, 'Airport_Congestion_percent': 40},
    ]
    
    for i, scenario in enumerate(scenarios):
        risk_score = 0
        risk_factors = []
        
        # Wind risk
        if scenario['Wind_Speed_mph'] > 20:
            risk_score += 30
            risk_factors.append('High wind conditions')
        
        # Precipitation risk
        if scenario['Precipitation_inches'] > 0.5:
            risk_score += 25
            risk_factors.append('Heavy precipitation')
        
        # Congestion risk
        if scenario['Airport_Congestion_percent'] > 75:
            risk_score += 35
            risk_factors.append('High airport congestion')
        
        # Determine prediction
        if risk_score >= 50:
            prediction = 'High Delay Risk'
            expected_delay = 30
        elif risk_score >= 30:
            prediction = 'Moderate Delay Risk'
            expected_delay = 15
        else:
            prediction = 'Low Delay Risk'
            expected_delay = 5
        
        predictions.append({
            'Scenario_ID': i + 1,
            'Airline': scenario['Airline'],
            'Departure_Airport': scenario['Departure_Airport'],
            'Wind_Speed_mph': scenario['Wind_Speed_mph'],
            'Precipitation_inches': scenario['Precipitation_inches'],
            'Airport_Congestion_percent': scenario['Airport_Congestion_percent'],
            'Risk_Score': risk_score,
            'Risk_Factors': '; '.join(risk_factors) if risk_factors else 'Favorable conditions',
            'Delay_Prediction': prediction,
            'Expected_Delay_Minutes': expected_delay
        })
    
    pred_df = pd.DataFrame(predictions)
    pred_df.to_csv('/home/ubuntu/delay_prediction_scenarios.csv', index=False)
    print("✓ Saved: delay_prediction_scenarios.csv")
    return pred_df

def main():
    print("="*80)
    print("FLIGHT ANALYTICS UTILITIES - GENERATING DETAILED DATASETS")
    print("="*80)
    print()
    
    # Generate main dataset
    print("Generating flight delay dataset...")
    df = generate_flight_delay_dataset(n_samples=1000)
    print(f"✓ Dataset created: {df.shape[0]} records\n")
    
    # Generate analytical datasets
    analyze_delay_by_airline(df)
    analyze_delay_by_airport(df)
    analyze_weather_impact(df)
    analyze_temporal_patterns(df)
    generate_operational_insights(df)
    generate_delay_predictions(df)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE - All datasets generated successfully")
    print("="*80)

if __name__ == "__main__":
    main()
