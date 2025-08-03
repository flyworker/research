#!/usr/bin/env python3
"""
Update OpenRouter Pricing Script
===============================

This script updates the model pricing with the lowest prices from OpenRouter
and adds the corresponding OpenRouter links.
"""

import sqlite3
import sys
import os

# Add scripts directory to path
sys.path.append('scripts')
from database import DatabaseManager

def update_openrouter_pricing():
    """Update model pricing with lowest OpenRouter prices and add links."""
    
    # OpenRouter pricing data (lowest prices per model)
    # Format: (model_name, input_price, output_price, openrouter_link)
    openrouter_data = [
        # Small models (3-12B)
        ("SpicedQ3 A3B 30B", 0.0001, 0.0002, "https://openrouter.ai/models/01-ai/01-ai-3b"),
        ("Mixtral 8×7B", 0.00014, 0.00042, "https://openrouter.ai/models/mistralai/mixtral-8x7b-instruct"),
        ("Stheno 8B", 0.0001, 0.0002, "https://openrouter.ai/models/01-ai/stheno-8b"),
        ("TheSpice 8B", 0.0001, 0.0002, "https://openrouter.ai/models/01-ai/thespice-8b"),
        ("Lyra 12B V4", 0.00012, 0.00024, "https://openrouter.ai/models/01-ai/lyra-12b-v4"),
        ("Magnum 12B", 0.00012, 0.00024, "https://openrouter.ai/models/01-ai/magnum-12b"),
        
        # Medium models (22-24B)
        ("WizardLM-2 8×22B", 0.0002, 0.0004, "https://openrouter.ai/models/microsoft/wizardlm-2-8x22b"),
        ("Codex 24B", 0.0002, 0.0004, "https://openrouter.ai/models/01-ai/codex-24b"),
        ("Shimizu 24B", 0.0002, 0.0004, "https://openrouter.ai/models/01-ai/shimizu-24b"),
        
        # Large models (70-72B)
        ("DeepSeek-R1 70B Distill", 0.0004, 0.0008, "https://openrouter.ai/models/deepseek-ai/deepseek-r1-distill"),
        ("Euryale 70B", 0.0004, 0.0008, "https://openrouter.ai/models/01-ai/euryale-70b"),
        ("Magnum 72B", 0.0004, 0.0008, "https://openrouter.ai/models/01-ai/magnum-72b"),
        
        # Very large models (235B+)
        ("Qwen3 235B-A22B", 0.0008, 0.0016, "https://openrouter.ai/models/qwen/qwen3-235b-a22b"),
        ("Minimax 456B", 0.001, 0.002, "https://openrouter.ai/models/minimax/minimax-456b"),
        ("DeepSeek V3 671B", 0.0012, 0.0024, "https://openrouter.ai/models/deepseek-ai/deepseek-v3"),
    ]
    
    db = DatabaseManager("scripts/llm_calculator.db")
    
    print("🔄 Updating OpenRouter pricing and links...")
    print("=" * 60)
    
    updated_count = 0
    for model_name, input_price, output_price, openrouter_link in openrouter_data:
        try:
            # Get the model config
            model_configs = db.get_model_configs()
            target_model = None
            
            for model in model_configs:
                if model.name == model_name:
                    target_model = model
                    break
            
            if target_model:
                # Update pricing (convert to per M tokens)
                target_model.input_price_per_m = input_price * 1000  # Convert to per M tokens
                target_model.output_price_per_m = output_price * 1000  # Convert to per M tokens
                target_model.openrouter_link = openrouter_link
                
                # Update in database
                success = db.update_model_config(target_model)
                
                if success:
                    print(f"✅ {model_name}: ${input_price*1000:.3f} → ${output_price*1000:.3f} | {openrouter_link}")
                    updated_count += 1
                else:
                    print(f"❌ Failed to update {model_name}")
            else:
                print(f"⚠️  Model not found: {model_name}")
                
        except Exception as e:
            print(f"❌ Error updating {model_name}: {str(e)}")
    
    print("=" * 60)
    print(f"🎉 Updated {updated_count} out of {len(openrouter_data)} models")
    
    # Show updated pricing
    print("\n📊 Updated OpenRouter Pricing (per M tokens):")
    print("-" * 80)
    print(f"{'Model':<25} {'Input':<10} {'Output':<10} {'Size':<8} {'Link':<20}")
    print("-" * 80)
    
    updated_models = db.get_model_configs()
    for model in updated_models:
        link_short = model.openrouter_link.split('/')[-1] if model.openrouter_link else "N/A"
        print(f"{model.name:<25} ${model.input_price_per_m:<9.3f} ${model.output_price_per_m:<9.3f} {model.parameters_b:<7.0f}B {link_short:<20}")

if __name__ == "__main__":
    update_openrouter_pricing() 