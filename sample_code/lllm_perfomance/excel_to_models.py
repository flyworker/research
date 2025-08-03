#!/usr/bin/env python3
"""
Excel to Model Settings Converter
================================

This script reads the Excel file and converts it to ModelConfig objects
that can be integrated into the model_settings.py file.
"""

import pandas as pd
from model_settings import ModelConfig, ALL_MODELS
import re

def clean_tier_name(tier):
    """Clean tier name by removing emojis and extracting key info."""
    # Remove emojis and extract tier info
    tier_clean = re.sub(r'[🥇🥈🥉]', '', tier)
    tier_clean = tier_clean.strip()
    
    # Extract tier level
    if '免费' in tier_clean or '入门' in tier_clean:
        return "Free/Entry"
    elif '中端' in tier_clean or '标准' in tier_clean:
        return "Standard"
    elif '高端' in tier_clean or '专业' in tier_clean:
        return "Premium"
    elif '顶级' in tier_clean or '企业' in tier_clean:
        return "Enterprise"
    else:
        return tier_clean

def extract_parameters(model_name):
    """Extract parameter count from model name."""
    # Look for patterns like "8B", "12B", "70B", etc.
    match = re.search(r'(\d+)B', model_name, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return 7.0  # Default fallback

def determine_precision(model_name, tier):
    """Determine model precision based on name and tier."""
    if 'MoE' in model_name or 'mixtral' in model_name.lower():
        return "MoE"
    elif 'AWQ' in model_name:
        return "AWQ"
    elif 'fp8' in model_name.lower():
        return "fp8"
    else:
        return "fp16"

def determine_gpu_type(recommended_gpu):
    """Determine GPU type from recommended GPU."""
    if 'H100' in recommended_gpu:
        return "H100"
    elif 'A100' in recommended_gpu:
        return "A100"
    elif '3090' in recommended_gpu:
        return "RTX 3090"
    elif '3080' in recommended_gpu:
        return "RTX 3080"
    else:
        return "A100"  # Default

def create_model_config(row):
    """Create a ModelConfig from Excel row."""
    model_name = row['Model'].strip()
    tier = clean_tier_name(row['Tier'])
    
    # Determine if it's a free model
    is_free = '免费' in row['Tier'] or '入门' in row['Tier']
    
    # Extract parameters
    parameters_b = extract_parameters(model_name)
    
    # Determine precision
    precision = determine_precision(model_name, tier)
    
    # Determine GPU type
    gpu_type = determine_gpu_type(row['Recommended GPU'])
    
    # Calculate total TPS per GPU
    total_tps = row['Total TPS']
    gpu_count = row['GPU Count']
    tokens_per_gpu_tps = total_tps / gpu_count if gpu_count > 0 else total_tps
    
    # Create slug (simplified)
    slug = f"custom/{model_name.lower().replace(' ', '-')}"
    
    # Create context window (estimate based on tier)
    if tier == "Enterprise":
        context_window = "200K"
    elif tier == "Premium":
        context_window = "128K"
    elif tier == "Standard":
        context_window = "32K"
    else:
        context_window = "8K"
    
    return ModelConfig(
        name=model_name,
        slug=slug,
        parameters_b=parameters_b,
        context_window=context_window,
        precision=precision,
        typical_gpu=gpu_type,
        input_price_per_m=f"${row['Input Token Price (per M)']:.2f}",
        output_price_per_m=f"${row['Output Token Price (per M)']:.2f}",
        tokens_per_gpu_tps=int(tokens_per_gpu_tps),
        openrouter_link="",  # Will need to be added manually
        description=f"{tier} tier model from Excel data",
        is_free=is_free,
        is_moe=precision == "MoE",
        is_awq=precision == "AWQ"
    )

def main():
    """Main function to convert Excel to models."""
    print("Reading Excel file...")
    df = pd.read_excel('model_tier_with_3090_3080.xlsx')
    
    print(f"Found {len(df)} models in Excel file")
    print("\nColumns:", df.columns.tolist())
    
    # Convert each row to ModelConfig
    excel_models = []
    for index, row in df.iterrows():
        try:
            model_config = create_model_config(row)
            excel_models.append(model_config)
            print(f"✓ Converted: {model_config.name} ({model_config.parameters_b}B, {model_config.precision})")
        except Exception as e:
            print(f"✗ Error converting row {index}: {e}")
    
    print(f"\nSuccessfully converted {len(excel_models)} models")
    
    # Show summary by tier
    tiers = {}
    for model in excel_models:
        tier = "Free" if model.is_free else "Paid"
        if tier not in tiers:
            tiers[tier] = []
        tiers[tier].append(model)
    
    print("\nSummary by tier:")
    for tier, models in tiers.items():
        print(f"  {tier}: {len(models)} models")
        for model in models[:3]:  # Show first 3
            print(f"    - {model.name} ({model.parameters_b}B)")
        if len(models) > 3:
            print(f"    ... and {len(models) - 3} more")
    
    # Generate code to add to model_settings.py
    print("\n" + "="*60)
    print("CODE TO ADD TO model_settings.py:")
    print("="*60)
    
    print("\n# Excel Models - Free Tier")
    for model in [m for m in excel_models if m.is_free]:
        print(f"""    ModelConfig(
        name="{model.name}",
        slug="{model.slug}",
        parameters_b={model.parameters_b},
        context_window="{model.context_window}",
        precision="{model.precision}",
        typical_gpu="{model.typical_gpu}",
        input_price_per_m="{model.input_price_per_m}",
        output_price_per_m="{model.output_price_per_m}",
        tokens_per_gpu_tps={model.tokens_per_gpu_tps},
        openrouter_link="",
        description="{model.description}",
        is_free=True,
        is_moe={str(model.is_moe)},
        is_awq={str(model.is_awq)}
    ),""")
    
    print("\n# Excel Models - Paid Tier")
    for model in [m for m in excel_models if not m.is_free]:
        print(f"""    ModelConfig(
        name="{model.name}",
        slug="{model.slug}",
        parameters_b={model.parameters_b},
        context_window="{model.context_window}",
        precision="{model.precision}",
        typical_gpu="{model.typical_gpu}",
        input_price_per_m="{model.input_price_per_m}",
        output_price_per_m="{model.output_price_per_m}",
        tokens_per_gpu_tps={model.tokens_per_gpu_tps},
        openrouter_link="",
        description="{model.description}",
        is_free=False,
        is_moe={str(model.is_moe)},
        is_awq={str(model.is_awq)}
    ),""")
    
    print("\n" + "="*60)
    print("Next steps:")
    print("1. Copy the code above")
    print("2. Add to FREE_MODELS or PAID_MODELS in model_settings.py")
    print("3. Restart the calculators to see the new models")
    print("="*60)

if __name__ == "__main__":
    main() 