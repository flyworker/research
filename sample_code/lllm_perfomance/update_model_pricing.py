#!/usr/bin/env python3
"""
Update Model Pricing Script
===========================

This script updates the input and output pricing for all models in the database
with more realistic and varied pricing based on model size and capabilities.
"""

import sqlite3
import sys
import os

# Add scripts directory to path
sys.path.append('scripts')
from database import DatabaseManager

def update_model_pricing():
    """Update model pricing with realistic values."""
    
    # Define pricing tiers based on model size and capabilities
    pricing_data = [
        # Small models (3-12B) - Lower pricing
        ("SpicedQ3 A3B 30B", 0.15, 0.45),
        ("Mixtral 8×7B", 0.20, 0.60),  # MoE model, slightly higher
        ("Stheno 8B", 0.18, 0.55),
        ("TheSpice 8B", 0.18, 0.55),
        ("Lyra 12B V4", 0.22, 0.65),
        ("Magnum 12B", 0.22, 0.65),
        
        # Medium models (22-24B) - Medium pricing
        ("WizardLM-2 8×22B", 0.35, 0.95),
        ("Codex 24B", 0.38, 1.05),
        ("Shimizu 24B", 0.38, 1.05),
        
        # Large models (70-72B) - Higher pricing
        ("DeepSeek-R1 70B Distill", 0.65, 1.85),
        ("Euryale 70B", 0.65, 1.85),
        ("Magnum 72B", 0.68, 1.90),
        
        # Very large models (235B+) - Premium pricing
        ("Qwen3 235B-A22B", 1.20, 3.50),
        ("Minimax 456B", 1.85, 5.20),
        ("DeepSeek V3 671B", 2.50, 7.00),
    ]
    
    db = DatabaseManager("scripts/llm_calculator.db")
    
    print("🔄 Updating model pricing...")
    print("=" * 50)
    
    updated_count = 0
    for model_name, input_price, output_price in pricing_data:
        try:
            # Get the model config
            model_configs = db.get_model_configs()
            target_model = None
            
            for model in model_configs:
                if model.name == model_name:
                    target_model = model
                    break
            
            if target_model:
                # Update pricing
                target_model.input_price_per_m = input_price
                target_model.output_price_per_m = output_price
                
                # Update in database
                success = db.update_model_config(target_model)
                
                if success:
                    print(f"✅ {model_name}: ${input_price:.2f} → ${output_price:.2f}")
                    updated_count += 1
                else:
                    print(f"❌ Failed to update {model_name}")
            else:
                print(f"⚠️  Model not found: {model_name}")
                
        except Exception as e:
            print(f"❌ Error updating {model_name}: {str(e)}")
    
    print("=" * 50)
    print(f"🎉 Updated {updated_count} out of {len(pricing_data)} models")
    
    # Show updated pricing
    print("\n📊 Updated Model Pricing:")
    print("-" * 60)
    print(f"{'Model':<25} {'Input':<8} {'Output':<8} {'Size':<8}")
    print("-" * 60)
    
    updated_models = db.get_model_configs()
    for model in updated_models:
        print(f"{model.name:<25} ${model.input_price_per_m:<7.2f} ${model.output_price_per_m:<7.2f} {model.parameters_b:<7.0f}B")

if __name__ == "__main__":
    update_model_pricing() 