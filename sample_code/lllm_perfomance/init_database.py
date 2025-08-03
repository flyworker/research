#!/usr/bin/env python3
"""
Database Initialization Script
==============================

This script initializes the database with default data including:
- GPU configurations
- Model configurations from Excel
- Default user preferences
"""

from database import DatabaseManager, GPUConfig, ModelConfig
from model_settings import ALL_MODELS
import os

def init_database():
    """Initialize database with all default data."""
    print("Initializing LLM Calculator Database...")
    
    # Create database manager
    db = DatabaseManager()
    
    # Check if database already has data
    existing_gpus = db.get_gpu_configs(active_only=False)
    existing_models = db.get_model_configs(active_only=False)
    
    if existing_gpus:
        print(f"Database already contains {len(existing_gpus)} GPU configurations")
    else:
        print("Populating GPU configurations...")
        db.populate_default_data()
        print("✓ GPU configurations populated")
    
    if existing_models:
        print(f"Database already contains {len(existing_models)} model configurations")
    else:
        print("Populating model configurations from Excel...")
        populate_models_from_excel(db)
        print("✓ Model configurations populated")
    
    print("\nDatabase initialization complete!")
    print(f"GPU Configurations: {len(db.get_gpu_configs())}")
    print(f"Model Configurations: {len(db.get_model_configs())}")
    
    # Show some sample data
    print("\nSample GPU Configurations:")
    gpus = db.get_gpu_configs()
    for gpu in gpus[:3]:
        print(f"  • {gpu.name}: ${gpu.cost_per_hour}/hour, {gpu.vram_gb}GB VRAM")
    
    print("\nSample Model Configurations:")
    models = db.get_model_configs()
    for model in models[:3]:
        print(f"  • {model.name}: {model.parameters_b}B params, {model.tokens_per_gpu_tps} TPS")

def populate_models_from_excel(db: DatabaseManager):
    """Populate database with models from Excel data."""
    for model in ALL_MODELS:
        # Convert ModelConfig from model_settings to database ModelConfig
        db_model = ModelConfig(
            name=model.name,
            slug=model.slug,
            parameters_b=model.parameters_b,
            context_window=model.context_window,
            precision=model.precision,
            typical_gpu=model.typical_gpu,
            input_price_per_m=float(model.input_price_per_m.replace('$', '')) if model.input_price_per_m and model.input_price_per_m != '-' else 0.0,
            output_price_per_m=float(model.output_price_per_m.replace('$', '')) if model.output_price_per_m and model.output_price_per_m != '-' else 0.0,
            tokens_per_gpu_tps=model.tokens_per_gpu_tps,
            openrouter_link=model.openrouter_link or "",
            description=model.description or "",
            is_free=model.is_free,
            is_moe=model.is_moe,
            is_awq=model.is_awq,
            is_active=True
        )
        
        db.insert_model_config(db_model)

def show_database_stats():
    """Show database statistics."""
    db = DatabaseManager()
    
    print("\n" + "="*50)
    print("DATABASE STATISTICS")
    print("="*50)
    
    # GPU stats
    gpus = db.get_gpu_configs()
    print(f"\nGPU Configurations: {len(gpus)}")
    for gpu in gpus:
        print(f"  • {gpu.name} ({gpu.gpu_type}): ${gpu.cost_per_hour}/hour")
    
    # Model stats
    models = db.get_model_configs()
    free_models = [m for m in models if m.is_free]
    paid_models = [m for m in models if not m.is_free]
    
    print(f"\nModel Configurations: {len(models)}")
    print(f"  • Free Models: {len(free_models)}")
    print(f"  • Paid Models: {len(paid_models)}")
    
    # Show some examples
    print(f"\nFree Models (first 3):")
    for model in free_models[:3]:
        print(f"  • {model.name} ({model.parameters_b}B)")
    
    print(f"\nPaid Models (first 3):")
    for model in paid_models[:3]:
        print(f"  • {model.name} ({model.parameters_b}B)")
    
    # Deployment stats
    deployments = db.get_deployment_configs()
    favorites = db.get_deployment_configs(favorites_only=True)
    
    print(f"\nDeployment Configurations: {len(deployments)}")
    print(f"  • Favorites: {len(favorites)}")
    
    # History stats
    history = db.get_calculation_history(limit=1000)
    print(f"\nCalculation History: {len(history)} entries")
    
    # User preferences
    default_gpu_cost = db.get_user_preference("default_gpu_cost", "Not set")
    default_gpu_count = db.get_user_preference("default_gpu_count", "Not set")
    currency = db.get_user_preference("currency", "Not set")
    
    print(f"\nUser Preferences:")
    print(f"  • Default GPU Cost: ${default_gpu_cost}/hour")
    print(f"  • Default GPU Count: {default_gpu_count}")
    print(f"  • Currency: {currency}")

def export_database_to_json():
    """Export database data to JSON for backup/analysis."""
    db = DatabaseManager()
    
    data = {
        "gpu_configs": [asdict(gpu) for gpu in db.get_gpu_configs(active_only=False)],
        "model_configs": [asdict(model) for model in db.get_model_configs(active_only=False)],
        "deployment_configs": [asdict(deployment) for deployment in db.get_deployment_configs()],
        "calculation_history": db.get_calculation_history(limit=1000)
    }
    
    import json
    with open("database_export.json", "w") as f:
        json.dump(data, f, indent=2, default=str)
    
    print("Database exported to database_export.json")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init":
            init_database()
        elif command == "stats":
            show_database_stats()
        elif command == "export":
            export_database_to_json()
        else:
            print("Usage: python init_database.py [init|stats|export]")
    else:
        # Default: initialize database
        init_database()
        show_database_stats() 