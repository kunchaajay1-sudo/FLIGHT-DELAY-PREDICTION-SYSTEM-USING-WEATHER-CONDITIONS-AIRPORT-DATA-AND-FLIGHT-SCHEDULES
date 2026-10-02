"""
Flight Delay Prediction System
Predicts flight delays using weather conditions, airport data, and flight schedules
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, confusion_matrix, roc_curve, auc, roc_auc_score)
import warnings
warnings.filterwarnings('ignore')

# Set style for visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10

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
    
    # Generate delay target (1 = delayed, 0 = on-time)
    # Delays are influenced by weather, congestion, and other factors
    delay_prob = 0.3
    
    # Increase delay probability based on adverse conditions
    delay_prob += (df['Wind_Speed_mph'] / 40) * 0.2
    delay_prob += (df['Precipitation_inches'] / 2) * 0.2
    delay_prob += (df['Airport_Congestion_percent'] / 100) * 0.2
    delay_prob += (df['Departure_Delay_minutes'] / 60) * 0.15
    delay_prob += (np.abs(df['Visibility_miles'] - 5) / 10) * 0.15
    
    # Cap probability at 0.95
    delay_prob = np.minimum(delay_prob, 0.95)
    
    df['Delayed'] = (np.random.random(n_samples) < delay_prob).astype(int)
    
    # Actual delay duration (only for delayed flights)
    df['Actual_Delay_minutes'] = np.where(
        df['Delayed'] == 1,
        np.random.exponential(scale=25, size=n_samples) + 15,
        0
    ).astype(int)
    
    return df

def preprocess_data(df):
    """Preprocess the dataset for modeling"""
    df_processed = df.copy()
    
    # Encode categorical variables
    le_airline = LabelEncoder()
    le_dep_airport = LabelEncoder()
    le_arr_airport = LabelEncoder()
    
    df_processed['Airline_encoded'] = le_airline.fit_transform(df_processed['Airline'])
    df_processed['Departure_Airport_encoded'] = le_dep_airport.fit_transform(df_processed['Departure_Airport'])
    df_processed['Arrival_Airport_encoded'] = le_arr_airport.fit_transform(df_processed['Arrival_Airport'])
    
    # Select features for modeling
    feature_cols = [
        'Day_of_Week', 'Month', 'Hour_of_Day', 'Distance_Miles',
        'Temperature_F', 'Wind_Speed_mph', 'Precipitation_inches',
        'Visibility_miles', 'Cloud_Cover_percent', 'Departure_Delay_minutes',
        'Airport_Congestion_percent', 'Runway_Availability_count',
        'Aircraft_Age_years', 'Previous_Flight_Delay_minutes',
        'Airline_encoded', 'Departure_Airport_encoded', 'Arrival_Airport_encoded'
    ]
    
    return df_processed, feature_cols

def train_models(X_train, X_test, y_train, y_test):
    """Train multiple classification models"""
    models = {}
    results = {}
    
    # Model 1: Logistic Regression
    print("Training Logistic Regression...")
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train, y_train)
    y_pred_lr = lr_model.predict(X_test)
    y_pred_proba_lr = lr_model.predict_proba(X_test)[:, 1]
    
    models['Logistic Regression'] = lr_model
    results['Logistic Regression'] = {
        'predictions': y_pred_lr,
        'probabilities': y_pred_proba_lr,
        'accuracy': accuracy_score(y_test, y_pred_lr),
        'precision': precision_score(y_test, y_pred_lr),
        'recall': recall_score(y_test, y_pred_lr),
        'f1': f1_score(y_test, y_pred_lr),
        'roc_auc': roc_auc_score(y_test, y_pred_proba_lr)
    }
    
    # Model 2: Random Forest
    print("Training Random Forest...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    y_pred_rf = rf_model.predict(X_test)
    y_pred_proba_rf = rf_model.predict_proba(X_test)[:, 1]
    
    models['Random Forest'] = rf_model
    results['Random Forest'] = {
        'predictions': y_pred_rf,
        'probabilities': y_pred_proba_rf,
        'accuracy': accuracy_score(y_test, y_pred_rf),
        'precision': precision_score(y_test, y_pred_rf),
        'recall': recall_score(y_test, y_pred_rf),
        'f1': f1_score(y_test, y_pred_rf),
        'roc_auc': roc_auc_score(y_test, y_pred_proba_rf)
    }
    
    # Model 3: Gradient Boosting
    print("Training Gradient Boosting...")
    gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
    gb_model.fit(X_train, y_train)
    y_pred_gb = gb_model.predict(X_test)
    y_pred_proba_gb = gb_model.predict_proba(X_test)[:, 1]
    
    models['Gradient Boosting'] = gb_model
    results['Gradient Boosting'] = {
        'predictions': y_pred_gb,
        'probabilities': y_pred_proba_gb,
        'accuracy': accuracy_score(y_test, y_pred_gb),
        'precision': precision_score(y_test, y_pred_gb),
        'recall': recall_score(y_test, y_pred_gb),
        'f1': f1_score(y_test, y_pred_gb),
        'roc_auc': roc_auc_score(y_test, y_pred_proba_gb)
    }
    
    return models, results

def plot_delay_distribution(df):
    """Plot distribution of delayed vs on-time flights"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Count plot
    delay_counts = df['Delayed'].value_counts()
    colors = ['#2ecc71', '#e74c3c']
    axes[0].bar(['On-Time', 'Delayed'], [delay_counts[0], delay_counts[1]], 
                color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[0].set_ylabel('Count', fontsize=11, fontweight='bold')
    axes[0].set_title('Distribution of Flight Status', fontsize=12, fontweight='bold')
    axes[0].grid(axis='y', alpha=0.3)
    for i, v in enumerate([delay_counts[0], delay_counts[1]]):
        axes[0].text(i, v + 10, str(v), ha='center', fontweight='bold')
    
    # Pie chart
    axes[1].pie([delay_counts[0], delay_counts[1]], labels=['On-Time', 'Delayed'],
                colors=colors, autopct='%1.1f%%', startangle=90, 
                textprops={'fontsize': 11, 'fontweight': 'bold'})
    axes[1].set_title('Flight Status Distribution', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/flight_delay_distribution.png', dpi=300, bbox_inches='tight')
    print("Saved: flight_delay_distribution.png")
    plt.close()

def plot_model_comparison(results):
    """Compare model performance metrics"""
    models = list(results.keys())
    metrics = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
    
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()
    
    for idx, metric in enumerate(metrics):
        values = [results[m][metric] for m in models]
        axes[idx].bar(models, values, color=['#3498db', '#e74c3c', '#f39c12'], 
                     alpha=0.8, edgecolor='black', linewidth=1.5)
        axes[idx].set_ylabel(metric.upper(), fontsize=11, fontweight='bold')
        axes[idx].set_title(f'{metric.upper()} Comparison', fontsize=12, fontweight='bold')
        axes[idx].set_ylim([0, 1])
        axes[idx].grid(axis='y', alpha=0.3)
        for i, v in enumerate(values):
            axes[idx].text(i, v + 0.02, f'{v:.4f}', ha='center', fontweight='bold', fontsize=9)
    
    # Remove the extra subplot
    fig.delaxes(axes[5])
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/flight_model_performance_comparison.png', dpi=300, bbox_inches='tight')
    print("Saved: flight_model_performance_comparison.png")
    plt.close()

def plot_confusion_matrices(results, y_test):
    """Plot confusion matrices for all models"""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    for idx, (model_name, result) in enumerate(results.items()):
        cm = confusion_matrix(y_test, result['predictions'])
        
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx],
                   cbar=False, annot_kws={'fontsize': 12, 'fontweight': 'bold'})
        axes[idx].set_xlabel('Predicted', fontsize=11, fontweight='bold')
        axes[idx].set_ylabel('Actual', fontsize=11, fontweight='bold')
        axes[idx].set_title(f'{model_name}\nAccuracy: {result["accuracy"]:.4f}', 
                           fontsize=12, fontweight='bold')
        axes[idx].set_xticklabels(['On-Time', 'Delayed'])
        axes[idx].set_yticklabels(['On-Time', 'Delayed'])
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/flight_confusion_matrices.png', dpi=300, bbox_inches='tight')
    print("Saved: flight_confusion_matrices.png")
    plt.close()

def plot_roc_curves(results, y_test):
    """Plot ROC curves for all models"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    colors = ['#3498db', '#e74c3c', '#f39c12']
    
    for idx, (model_name, result) in enumerate(results.items()):
        fpr, tpr, _ = roc_curve(y_test, result['probabilities'])
        roc_auc = result['roc_auc']
        
        ax.plot(fpr, tpr, color=colors[idx], lw=2.5, 
               label=f'{model_name} (AUC = {roc_auc:.4f})')
    
    ax.plot([0, 1], [0, 1], 'k--', lw=2, label='Random Classifier')
    ax.set_xlabel('False Positive Rate', fontsize=11, fontweight='bold')
    ax.set_ylabel('True Positive Rate', fontsize=11, fontweight='bold')
    ax.set_title('ROC Curves - Flight Delay Prediction', fontsize=12, fontweight='bold')
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/flight_roc_curves.png', dpi=300, bbox_inches='tight')
    print("Saved: flight_roc_curves.png")
    plt.close()

def plot_feature_importance(models, feature_names):
    """Plot feature importance for tree-based models"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Random Forest
    rf_importance = models['Random Forest'].feature_importances_
    rf_indices = np.argsort(rf_importance)[-10:]
    axes[0].barh(range(len(rf_indices)), rf_importance[rf_indices], 
                color='#e74c3c', alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[0].set_yticks(range(len(rf_indices)))
    axes[0].set_yticklabels([feature_names[i] for i in rf_indices], fontsize=10)
    axes[0].set_xlabel('Importance', fontsize=11, fontweight='bold')
    axes[0].set_title('Random Forest - Feature Importance', fontsize=12, fontweight='bold')
    axes[0].grid(axis='x', alpha=0.3)
    
    # Gradient Boosting
    gb_importance = models['Gradient Boosting'].feature_importances_
    gb_indices = np.argsort(gb_importance)[-10:]
    axes[1].barh(range(len(gb_indices)), gb_importance[gb_indices], 
                color='#f39c12', alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[1].set_yticks(range(len(gb_indices)))
    axes[1].set_yticklabels([feature_names[i] for i in gb_indices], fontsize=10)
    axes[1].set_xlabel('Importance', fontsize=11, fontweight='bold')
    axes[1].set_title('Gradient Boosting - Feature Importance', fontsize=12, fontweight='bold')
    axes[1].grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/flight_feature_importance.png', dpi=300, bbox_inches='tight')
    print("Saved: flight_feature_importance.png")
    plt.close()

def plot_weather_impact(df):
    """Plot weather impact on flight delays"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Wind Speed vs Delay
    delayed = df[df['Delayed'] == 1]
    on_time = df[df['Delayed'] == 0]
    
    axes[0, 0].scatter(on_time['Wind_Speed_mph'], on_time['Actual_Delay_minutes'], 
                      alpha=0.5, s=30, color='#2ecc71', label='On-Time', edgecolors='black', linewidth=0.5)
    axes[0, 0].scatter(delayed['Wind_Speed_mph'], delayed['Actual_Delay_minutes'], 
                      alpha=0.5, s=30, color='#e74c3c', label='Delayed', edgecolors='black', linewidth=0.5)
    axes[0, 0].set_xlabel('Wind Speed (mph)', fontsize=11, fontweight='bold')
    axes[0, 0].set_ylabel('Delay Duration (minutes)', fontsize=11, fontweight='bold')
    axes[0, 0].set_title('Wind Speed vs Flight Delay', fontsize=12, fontweight='bold')
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.3)
    
    # Precipitation vs Delay
    axes[0, 1].scatter(on_time['Precipitation_inches'], on_time['Actual_Delay_minutes'], 
                      alpha=0.5, s=30, color='#2ecc71', label='On-Time', edgecolors='black', linewidth=0.5)
    axes[0, 1].scatter(delayed['Precipitation_inches'], delayed['Actual_Delay_minutes'], 
                      alpha=0.5, s=30, color='#e74c3c', label='Delayed', edgecolors='black', linewidth=0.5)
    axes[0, 1].set_xlabel('Precipitation (inches)', fontsize=11, fontweight='bold')
    axes[0, 1].set_ylabel('Delay Duration (minutes)', fontsize=11, fontweight='bold')
    axes[0, 1].set_title('Precipitation vs Flight Delay', fontsize=12, fontweight='bold')
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.3)
    
    # Visibility vs Delay
    axes[1, 0].scatter(on_time['Visibility_miles'], on_time['Actual_Delay_minutes'], 
                      alpha=0.5, s=30, color='#2ecc71', label='On-Time', edgecolors='black', linewidth=0.5)
    axes[1, 0].scatter(delayed['Visibility_miles'], delayed['Actual_Delay_minutes'], 
                      alpha=0.5, s=30, color='#e74c3c', label='Delayed', edgecolors='black', linewidth=0.5)
    axes[1, 0].set_xlabel('Visibility (miles)', fontsize=11, fontweight='bold')
    axes[1, 0].set_ylabel('Delay Duration (minutes)', fontsize=11, fontweight='bold')
    axes[1, 0].set_title('Visibility vs Flight Delay', fontsize=12, fontweight='bold')
    axes[1, 0].legend()
    axes[1, 0].grid(alpha=0.3)
    
    # Airport Congestion vs Delay
    axes[1, 1].scatter(on_time['Airport_Congestion_percent'], on_time['Actual_Delay_minutes'], 
                      alpha=0.5, s=30, color='#2ecc71', label='On-Time', edgecolors='black', linewidth=0.5)
    axes[1, 1].scatter(delayed['Airport_Congestion_percent'], delayed['Actual_Delay_minutes'], 
                      alpha=0.5, s=30, color='#e74c3c', label='Delayed', edgecolors='black', linewidth=0.5)
    axes[1, 1].set_xlabel('Airport Congestion (%)', fontsize=11, fontweight='bold')
    axes[1, 1].set_ylabel('Delay Duration (minutes)', fontsize=11, fontweight='bold')
    axes[1, 1].set_title('Airport Congestion vs Flight Delay', fontsize=12, fontweight='bold')
    axes[1, 1].legend()
    axes[1, 1].grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/flight_weather_impact.png', dpi=300, bbox_inches='tight')
    print("Saved: flight_weather_impact.png")
    plt.close()

def plot_delay_by_airline(df):
    """Plot delay statistics by airline"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Delay rate by airline
    airline_delay_rate = df.groupby('Airline')['Delayed'].mean().sort_values(ascending=False)
    axes[0].bar(airline_delay_rate.index, airline_delay_rate.values, 
               color='#3498db', alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[0].set_ylabel('Delay Rate', fontsize=11, fontweight='bold')
    axes[0].set_title('Flight Delay Rate by Airline', fontsize=12, fontweight='bold')
    axes[0].set_ylim([0, 1])
    for i, v in enumerate(airline_delay_rate.values):
        axes[0].text(i, v + 0.02, f'{v:.2%}', ha='center', fontweight='bold')
    axes[0].grid(axis='y', alpha=0.3)
    
    # Average delay duration by airline
    airline_avg_delay = df[df['Delayed'] == 1].groupby('Airline')['Actual_Delay_minutes'].mean().sort_values(ascending=False)
    axes[1].bar(airline_avg_delay.index, airline_avg_delay.values, 
               color='#e74c3c', alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[1].set_ylabel('Average Delay (minutes)', fontsize=11, fontweight='bold')
    axes[1].set_title('Average Delay Duration by Airline', fontsize=12, fontweight='bold')
    for i, v in enumerate(airline_avg_delay.values):
        axes[1].text(i, v + 1, f'{v:.1f}', ha='center', fontweight='bold')
    axes[1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/flight_delay_by_airline.png', dpi=300, bbox_inches='tight')
    print("Saved: flight_delay_by_airline.png")
    plt.close()

def main():
    print("="*80)
    print("FLIGHT DELAY PREDICTION SYSTEM - MACHINE LEARNING ANALYSIS")
    print("="*80)
    
    # Generate dataset
    print("\n[1] Generating synthetic flight delay dataset...")
    df = generate_flight_delay_dataset(n_samples=1000)
    df.to_csv('/home/ubuntu/flight_delay_data.csv', index=False)
    print(f"Dataset generated: {df.shape[0]} records")
    print(f"Delayed flights: {(df['Delayed'] == 1).sum()} ({(df['Delayed'] == 1).sum() / len(df) * 100:.1f}%)")
    print(f"On-time flights: {(df['Delayed'] == 0).sum()} ({(df['Delayed'] == 0).sum() / len(df) * 100:.1f}%)")
    
    # Preprocess data
    print("\n[2] Preprocessing data...")
    df_processed, feature_cols = preprocess_data(df)
    
    # Prepare features and target
    X = df_processed[feature_cols]
    y = df_processed['Delayed']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"Training set: {X_train_scaled.shape[0]} samples, {X_train_scaled.shape[1]} features")
    print(f"Test set: {X_test_scaled.shape[0]} samples")
    
    # Train models
    print("\n[3] Training classification models...")
    models, results = train_models(X_train_scaled, X_test_scaled, y_train, y_test)
    
    # Print results
    print("\n[4] Model Performance Results:")
    print("-" * 80)
    for model_name, result in results.items():
        print(f"\n{model_name}:")
        print(f"  Accuracy:  {result['accuracy']:.6f}")
        print(f"  Precision: {result['precision']:.6f}")
        print(f"  Recall:    {result['recall']:.6f}")
        print(f"  F1-Score:  {result['f1']:.6f}")
        print(f"  ROC-AUC:   {result['roc_auc']:.6f}")
    
    # Generate visualizations
    print("\n[5] Generating visualizations...")
    plot_delay_distribution(df)
    plot_model_comparison(results)
    plot_confusion_matrices(results, y_test)
    plot_roc_curves(results, y_test)
    plot_feature_importance(models, feature_cols)
    plot_weather_impact(df)
    plot_delay_by_airline(df)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE - All visualizations saved")
    print("="*80)

if __name__ == "__main__":
    main()
