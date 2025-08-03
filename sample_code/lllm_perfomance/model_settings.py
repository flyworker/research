"""
Model Settings and Pricing Configuration
========================================

This file contains preset models, pricing data, and configuration options
for LLM deployment analysis and profitability calculations.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """Configuration for a single model."""
    name: str
    slug: str
    parameters_b: float
    context_window: str
    precision: str
    typical_gpu: str
    input_price_per_m: Optional[str]
    output_price_per_m: Optional[str]
    tokens_per_gpu_tps: int
    openrouter_link: Optional[str] = None
    description: Optional[str] = None
    is_free: bool = False
    is_moe: bool = False
    is_awq: bool = False

# GPU Infrastructure Presets
GPU_PRESETS = {
    "8x_H100_80GB": {
        "name": "8× H100 80GB",
        "gpu_count": 8,
        "gpu_cost_per_hour": 2.0,
        "total_vram_gb": 640,
        "typical_models": ["DeepSeek-V3-0324-AWQ", "Llama-3-70B", "Mixtral-8x7B"],
        "description": "High-performance cluster for large models"
    },
    "4x_H100_80GB": {
        "name": "4× H100 80GB", 
        "gpu_count": 4,
        "gpu_cost_per_hour": 2.0,
        "total_vram_gb": 320,
        "typical_models": ["DeepSeek-Coder-33B", "Llama-3-8B", "Mistral-7B"],
        "description": "Mid-range cluster for medium models"
    },
    "2x_H100_80GB": {
        "name": "2× H100 80GB",
        "gpu_count": 2, 
        "gpu_cost_per_hour": 2.0,
        "total_vram_gb": 160,
        "typical_models": ["Llama-3-8B", "Mistral-7B", "Gemma-7B"],
        "description": "Entry-level cluster for smaller models"
    },
    "8x_A100_80GB": {
        "name": "8× A100 80GB",
        "gpu_count": 8,
        "gpu_cost_per_hour": 1.5,
        "total_vram_gb": 640,
        "typical_models": ["DeepSeek-V3-0324", "Llama-3-70B"],
        "description": "Cost-effective alternative to H100"
    },
    "Cloud_H100": {
        "name": "Cloud H100 (RunPod)",
        "gpu_count": 1,
        "gpu_cost_per_hour": 2.99,
        "total_vram_gb": 80,
        "typical_models": ["DeepSeek-Coder-33B", "Llama-3-8B"],
        "description": "Cloud-based H100 for testing"
    }
}

# Model Presets - Free Models
FREE_MODELS = [
    # Excel Models - Free Tier
    ModelConfig(
        name="Stheno 8B",
        slug="custom/stheno-8b",
        parameters_b=8.0,
        context_window="8K",
        precision="fp16",
        typical_gpu="RTX 3090",
        input_price_per_m="$0.28",
        output_price_per_m="$0.88",
        tokens_per_gpu_tps=2000,
        openrouter_link="",
        description="Free/Entry tier model from Excel data",
        is_free=True,
        is_moe=False,
        is_awq=False
    ),
    ModelConfig(
        name="TheSpice 8B",
        slug="custom/thespice-8b",
        parameters_b=8.0,
        context_window="8K",
        precision="fp16",
        typical_gpu="RTX 3090",
        input_price_per_m="$0.28",
        output_price_per_m="$0.88",
        tokens_per_gpu_tps=2000,
        openrouter_link="",
        description="Free/Entry tier model from Excel data",
        is_free=True,
        is_moe=False,
        is_awq=False
    ),
    ModelConfig(
        name="Lyra 12B V4",
        slug="custom/lyra-12b-v4",
        parameters_b=12.0,
        context_window="8K",
        precision="fp16",
        typical_gpu="RTX 3090",
        input_price_per_m="$0.28",
        output_price_per_m="$0.88",
        tokens_per_gpu_tps=1700,
        openrouter_link="",
        description="Free/Entry tier model from Excel data",
        is_free=True,
        is_moe=False,
        is_awq=False
    )
]

# Model Presets - Paid Models
PAID_MODELS = [
    # Excel Models - Paid Tier
    ModelConfig(
        name="Mixtral 8×7B",
        slug="custom/mixtral-8×7b",
        parameters_b=7.0,
        context_window="32K",
        precision="MoE",
        typical_gpu="RTX 3090",
        input_price_per_m="$0.28",
        output_price_per_m="$0.88",
        tokens_per_gpu_tps=3000,
        openrouter_link="",
        description="Standard tier model from Excel data",
        is_free=False,
        is_moe=True,
        is_awq=False
    ),
    ModelConfig(
        name="SpicedQ3 A3B 30B",
        slug="custom/spicedq3-a3b-30b",
        parameters_b=3.0,
        context_window="32K",
        precision="fp16",
        typical_gpu="H100",
        input_price_per_m="$0.28",
        output_price_per_m="$0.88",
        tokens_per_gpu_tps=1200,
        openrouter_link="",
        description="Standard tier model from Excel data",
        is_free=False,
        is_moe=False,
        is_awq=False
    ),
    ModelConfig(
        name="Magnum 12B",
        slug="custom/magnum-12b",
        parameters_b=12.0,
        context_window="32K",
        precision="fp16",
        typical_gpu="RTX 3090",
        input_price_per_m="$0.28",
        output_price_per_m="$0.88",
        tokens_per_gpu_tps=2100,
        openrouter_link="",
        description="Standard tier model from Excel data",
        is_free=False,
        is_moe=False,
        is_awq=False
    ),
    ModelConfig(
        name="Codex 24B",
        slug="custom/codex-24b",
        parameters_b=24.0,
        context_window="32K",
        precision="fp16",
        typical_gpu="RTX 3080",
        input_price_per_m="$0.28",
        output_price_per_m="$0.88",
        tokens_per_gpu_tps=1300,
        openrouter_link="",
        description="Standard tier model from Excel data",
        is_free=False,
        is_moe=False,
        is_awq=False
    ),
    ModelConfig(
        name="Shimizu 24B",
        slug="custom/shimizu-24b",
        parameters_b=24.0,
        context_window="32K",
        precision="fp16",
        typical_gpu="RTX 3080",
        input_price_per_m="$0.28",
        output_price_per_m="$0.88",
        tokens_per_gpu_tps=1300,
        openrouter_link="",
        description="Standard tier model from Excel data",
        is_free=False,
        is_moe=False,
        is_awq=False
    ),
    ModelConfig(
        name="DeepSeek-R1 70B Distill",
        slug="custom/deepseek-r1-70b-distill",
        parameters_b=70.0,
        context_window="8K",
        precision="fp16",
        typical_gpu="A100",
        input_price_per_m="$0.28",
        output_price_per_m="$0.88",
        tokens_per_gpu_tps=437,
        openrouter_link="",
        description="Premium tier model from Excel data",
        is_free=False,
        is_moe=False,
        is_awq=False
    ),
    ModelConfig(
        name="Euryale 70B",
        slug="custom/euryale-70b",
        parameters_b=70.0,
        context_window="8K",
        precision="fp16",
        typical_gpu="A100",
        input_price_per_m="$0.28",
        output_price_per_m="$0.88",
        tokens_per_gpu_tps=437,
        openrouter_link="",
        description="Premium tier model from Excel data",
        is_free=False,
        is_moe=False,
        is_awq=False
    ),
    ModelConfig(
        name="Magnum 72B",
        slug="custom/magnum-72b",
        parameters_b=72.0,
        context_window="8K",
        precision="fp16",
        typical_gpu="A100",
        input_price_per_m="$0.28",
        output_price_per_m="$0.88",
        tokens_per_gpu_tps=462,
        openrouter_link="",
        description="Premium tier model from Excel data",
        is_free=False,
        is_moe=False,
        is_awq=False
    ),
    ModelConfig(
        name="WizardLM-2 8×22B",
        slug="custom/wizardlm-2-8×22b",
        parameters_b=22.0,
        context_window="8K",
        precision="fp16",
        typical_gpu="RTX 3080",
        input_price_per_m="$0.28",
        output_price_per_m="$0.88",
        tokens_per_gpu_tps=2250,
        openrouter_link="",
        description="Enterprise tier model from Excel data",
        is_free=False,
        is_moe=False,
        is_awq=False
    ),
    ModelConfig(
        name="Qwen3 235B-A22B",
        slug="custom/qwen3-235b-a22b",
        parameters_b=235.0,
        context_window="8K",
        precision="fp16",
        typical_gpu="RTX 3080",
        input_price_per_m="$0.28",
        output_price_per_m="$0.88",
        tokens_per_gpu_tps=2350,
        openrouter_link="",
        description="Enterprise tier model from Excel data",
        is_free=False,
        is_moe=False,
        is_awq=False
    ),
    ModelConfig(
        name="Minimax 456B",
        slug="custom/minimax-456b",
        parameters_b=456.0,
        context_window="8K",
        precision="fp16",
        typical_gpu="H100",
        input_price_per_m="$0.28",
        output_price_per_m="$0.88",
        tokens_per_gpu_tps=1250,
        openrouter_link="",
        description="Enterprise tier model from Excel data",
        is_free=False,
        is_moe=False,
        is_awq=False
    ),
    ModelConfig(
        name="DeepSeek V3 671B",
        slug="custom/deepseek-v3-671b",
        parameters_b=671.0,
        context_window="8K",
        precision="fp16",
        typical_gpu="H100",
        input_price_per_m="$0.28",
        output_price_per_m="$0.88",
        tokens_per_gpu_tps=310,
        openrouter_link="",
        description="Enterprise tier model from Excel data",
        is_free=False,
        is_moe=False,
        is_awq=False
    )
]

# Combine all models
ALL_MODELS = FREE_MODELS + PAID_MODELS

# Pricing Tiers
PRICING_TIERS = {
    "budget": {
        "name": "Budget",
        "input_price_range": (0.05, 0.15),
        "output_price_range": (0.15, 0.45),
        "models": ["Llama 3.1 8B", "Mistral 7B", "Gemma 7B"]
    },
    "standard": {
        "name": "Standard",
        "input_price_range": (0.20, 0.50),
        "output_price_range": (0.60, 1.50),
        "models": ["Llama 3.1 70B", "Mixtral 8x7B", "Gemini Pro"]
    },
    "premium": {
        "name": "Premium",
        "input_price_range": (0.25, 3.00),
        "output_price_range": (1.25, 15.00),
        "models": ["Claude 3 Haiku", "Claude 3 Sonnet", "DeepSeek Chat"]
    },
    "enterprise": {
        "name": "Enterprise",
        "input_price_range": (3.00, 15.00),
        "output_price_range": (15.00, 75.00),
        "models": ["Claude 3 Opus", "Gemini Pro 1.5"]
    }
}

# vLLM Configuration Presets
VLLM_PRESETS = {
    "deepseek_v3_0324_awq": {
        "model": "deepseek-ai/DeepSeek-V3-0324-AWQ",
        "tensor_parallel_size": 8,
        "dtype": "auto",
        "max_model_len": 163000,
        "gpu_memory_utilization": 0.90,
        "max_num_seqs": 256,
        "max_num_batched_tokens": 8192,
        "port": 8000,
        "description": "DeepSeek V3 0324 AWQ on 8× H100"
    },
    "llama_3_70b": {
        "model": "meta-llama/Llama-3.1-70b-instruct",
        "tensor_parallel_size": 4,
        "dtype": "auto",
        "max_model_len": 8192,
        "gpu_memory_utilization": 0.90,
        "max_num_seqs": 256,
        "max_num_batched_tokens": 8192,
        "port": 8000,
        "description": "Llama 3.1 70B on 4× H100"
    },
    "mixtral_8x7b": {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "tensor_parallel_size": 2,
        "dtype": "auto",
        "max_model_len": 32768,
        "gpu_memory_utilization": 0.90,
        "max_num_seqs": 256,
        "max_num_batched_tokens": 8192,
        "port": 8000,
        "description": "Mixtral 8x7B on 2× H100"
    }
}

def get_model_by_name(name: str) -> Optional[ModelConfig]:
    """Get a model configuration by name."""
    for model in ALL_MODELS:
        if model.name == name:
            return model
    return None

def get_models_by_type(model_type: str) -> List[ModelConfig]:
    """Get models by type (free, paid, moe, awq)."""
    if model_type == "free":
        return FREE_MODELS
    elif model_type == "paid":
        return PAID_MODELS
    elif model_type == "moe":
        return [m for m in ALL_MODELS if m.is_moe]
    elif model_type == "awq":
        return [m for m in ALL_MODELS if m.is_awq]
    else:
        return ALL_MODELS

def get_gpu_preset(name: str) -> Optional[Dict[str, Any]]:
    """Get GPU infrastructure preset by name."""
    return GPU_PRESETS.get(name)

def get_vllm_preset(name: str) -> Optional[Dict[str, Any]]:
    """Get vLLM configuration preset by name."""
    return VLLM_PRESETS.get(name)

def format_price(price_str: str) -> float:
    """Convert price string to float."""
    if not price_str or price_str == "-":
        return 0.0
    return float(price_str.replace("$", ""))

def get_model_dict(model: ModelConfig) -> Dict[str, Any]:
    """Convert ModelConfig to dictionary format for compatibility."""
    return {
        "Model": model.name,
        "Slug": model.slug,
        "Parameters (B)": model.parameters_b,
        "Context window": model.context_window,
        "Precision": model.precision,
        "Typical GPU": model.typical_gpu,
        "Input $/M": model.input_price_per_m or "-",
        "Output $/M": model.output_price_per_m or "-",
        "Tokens per GPU TPS": model.tokens_per_gpu_tps,
        "OpenRouter Link": model.openrouter_link or "",
        "Description": model.description or "",
        "Is Free": model.is_free,
        "Is MoE": model.is_moe,
        "Is AWQ": model.is_awq
    } 

def get_compatible_gpus(model: ModelConfig, gpu_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get GPU configurations compatible with a given model."""
    compatible_gpus = []
    
    # Estimate VRAM requirements based on model parameters and precision
    estimated_vram = estimate_vram_requirement(model.parameters_b, model.precision)
    
    for gpu in gpu_configs:
        if gpu["total_vram_gb"] >= estimated_vram:
            compatible_gpus.append(gpu)
    
    # Sort by cost efficiency (cost per GB of VRAM)
    compatible_gpus.sort(key=lambda g: g["gpu_cost_per_hour"] / g["total_vram_gb"])
    return compatible_gpus

def estimate_vram_requirement(parameters_b: float, precision: str) -> int:
    """Estimate VRAM requirement for a model."""
    base_vram = parameters_b * 2  # Base requirement: 2GB per billion parameters
    
    # Adjust based on precision
    if precision == "fp16":
        multiplier = 1.0
    elif precision == "fp8":
        multiplier = 0.5
    elif precision == "MoE":
        multiplier = 1.5  # MoE models need more VRAM
    elif precision == "AWQ":
        multiplier = 0.3  # Quantized models need less VRAM
    else:
        multiplier = 1.0
    
    estimated_vram = int(base_vram * multiplier)
    
    # Minimum VRAM requirements
    if estimated_vram < 8:
        estimated_vram = 8
    elif estimated_vram < 16:
        estimated_vram = 16
    elif estimated_vram < 24:
        estimated_vram = 24
    elif estimated_vram < 40:
        estimated_vram = 40
    elif estimated_vram < 80:
        estimated_vram = 80
    
    return estimated_vram

def get_optimal_gpu_config(model: ModelConfig, gpu_configs: List[Dict[str, Any]], 
                          budget_constraint: float = None) -> Optional[Dict[str, Any]]:
    """Get the optimal GPU configuration for a model within budget constraints."""
    compatible_gpus = get_compatible_gpus(model, gpu_configs)
    
    if not compatible_gpus:
        return None
    
    # Filter by budget if specified
    if budget_constraint:
        compatible_gpus = [g for g in compatible_gpus if g["gpu_cost_per_hour"] <= budget_constraint]
    
    if not compatible_gpus:
        return None
    
    # Return the most cost-effective option
    return compatible_gpus[0]

def calculate_gpu_scaling(model: ModelConfig, gpu_config: Dict[str, Any], 
                         target_tps: int) -> Dict[str, Any]:
    """Calculate GPU scaling requirements for a target TPS."""
    # Estimate single GPU TPS based on model parameters
    base_tps_per_gpu = model.tokens_per_gpu_tps
    
    # Calculate required GPU count
    required_gpus = max(1, int(target_tps / base_tps_per_gpu))
    
    # Calculate costs
    hourly_cost = gpu_config["gpu_cost_per_hour"] * required_gpus
    daily_cost = hourly_cost * 24
    monthly_cost = daily_cost * 30
    
    # Calculate efficiency metrics
    efficiency = (target_tps / (required_gpus * base_tps_per_gpu)) * 100
    
    return {
        "required_gpus": required_gpus,
        "hourly_cost": hourly_cost,
        "daily_cost": daily_cost,
        "monthly_cost": monthly_cost,
        "efficiency_percentage": efficiency,
        "tps_per_gpu": base_tps_per_gpu,
        "total_vram": gpu_config["total_vram_gb"] * required_gpus
    } 