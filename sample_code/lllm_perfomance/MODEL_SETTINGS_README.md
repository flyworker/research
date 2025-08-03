# Model Settings and Configuration

This file (`model_settings.py`) contains centralized configuration for all models, pricing, and infrastructure presets used by the LLM calculators.

## Overview

The settings file provides:
- **Model configurations** with detailed specifications
- **GPU infrastructure presets** for different deployment scenarios
- **Pricing tiers** and market data
- **vLLM deployment configurations**
- **Utility functions** for data access and conversion

## Structure

### ModelConfig Dataclass
Each model is defined using a `ModelConfig` dataclass with the following fields:

```python
@dataclass
class ModelConfig:
    name: str                    # Display name
    slug: str                    # Model identifier
    parameters_b: float          # Billions of parameters
    context_window: str          # Max context length
    precision: str               # fp8, fp16, MoE, AWQ
    typical_gpu: str             # Recommended GPU type
    input_price_per_m: str       # Input price per million tokens
    output_price_per_m: str      # Output price per million tokens
    tokens_per_gpu_tps: int      # Tokens per second per GPU
    openrouter_link: str         # OpenRouter model page
    description: str             # Model description
    is_free: bool               # Free tier flag
    is_moe: bool                # Mixture of Experts flag
    is_awq: bool                # AWQ quantization flag
```

## Model Categories

### Free Models
- **DeepSeek models**: V3 0324, R1 0528, R1 original
- **Open source models**: Llama 3, Mistral, Mixtral, Gemma
- **Commercial free tiers**: Claude 3, Gemini Pro
- **Specialized models**: OpenChat, DeepSeek Coder

### Paid Models
- **Premium models**: Claude 3 Opus, Gemini Pro 1.5
- **Standard models**: Llama 3.1, Mistral, Mixtral
- **DeepSeek models**: Chat V3, Coder V3
- **Self-hosted**: DeepSeek-V3-0324-AWQ

## GPU Infrastructure Presets

### Available Configurations
```python
GPU_PRESETS = {
    "8x_H100_80GB": {
        "name": "8× H100 80GB",
        "gpu_count": 8,
        "gpu_cost_per_hour": 2.0,
        "total_vram_gb": 640,
        "typical_models": ["DeepSeek-V3-0324-AWQ", "Llama-3-70B"],
        "description": "High-performance cluster for large models"
    },
    "4x_H100_80GB": {
        "name": "4× H100 80GB",
        "gpu_count": 4,
        "gpu_cost_per_hour": 2.0,
        "total_vram_gb": 320,
        "typical_models": ["DeepSeek-Coder-33B", "Llama-3-8B"],
        "description": "Mid-range cluster for medium models"
    },
    "2x_H100_80GB": {
        "name": "2× H100 80GB",
        "gpu_count": 2,
        "gpu_cost_per_hour": 2.0,
        "total_vram_gb": 160,
        "typical_models": ["Llama-3-8B", "Mistral-7B"],
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
```

## Pricing Tiers

### Market Segmentation
```python
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
```

## vLLM Configuration Presets

### Deployment Configurations
```python
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
```

## Utility Functions

### Data Access Functions
```python
# Get model by name
model = get_model_by_name("DeepSeek V3 0324 (free)")

# Get models by type
free_models = get_models_by_type("free")
paid_models = get_models_by_type("paid")
moe_models = get_models_by_type("moe")
awq_models = get_models_by_type("awq")

# Get infrastructure presets
gpu_config = get_gpu_preset("8x_H100_80GB")
vllm_config = get_vllm_preset("deepseek_v3_0324_awq")

# Convert price strings to floats
price = format_price("$0.28")  # Returns 0.28

# Convert ModelConfig to dictionary
model_dict = get_model_dict(model)
```

## Usage Examples

### In LLM Valuation Calculator
```python
from model_settings import get_model_by_name, get_models_by_type

# Get all free models for dropdown
free_models = get_models_by_type("free")
model_options = [model.name for model in free_models]

# Get specific model details
selected_model = get_model_by_name("DeepSeek V3 0324 (free)")
if selected_model:
    tps = selected_model.tokens_per_gpu_tps
    context_window = selected_model.context_window
```

### In GPU Profit Calculator
```python
from model_settings import get_gpu_preset, get_model_by_name

# Get GPU configuration
gpu_config = get_gpu_preset("8x_H100_80GB")
gpu_cost = gpu_config["gpu_cost_per_hour"]
gpu_count = gpu_config["gpu_count"]

# Get model for pricing
model = get_model_by_name("DeepSeek Chat V3 0324")
input_price = format_price(model.input_price_per_m)
output_price = format_price(model.output_price_per_m)
```

### For vLLM Deployment
```python
from model_settings import get_vllm_preset

# Get vLLM configuration
vllm_config = get_vllm_preset("deepseek_v3_0324_awq")

# Build vLLM command
cmd = f"""python3 -m vllm.entrypoints.openai.api_server \\
    --model {vllm_config['model']} \\
    --tensor-parallel-size {vllm_config['tensor_parallel_size']} \\
    --dtype {vllm_config['dtype']} \\
    --max-model-len {vllm_config['max_model_len']} \\
    --gpu-memory-utilization {vllm_config['gpu_memory_utilization']} \\
    --port {vllm_config['port']}"""
```

## Adding New Models

### 1. Add to FREE_MODELS or PAID_MODELS
```python
ModelConfig(
    name="New Model Name",
    slug="provider/model-name",
    parameters_b=7,
    context_window="8K",
    precision="fp16",
    typical_gpu="A100",
    input_price_per_m="$0.05",
    output_price_per_m="$0.15",
    tokens_per_gpu_tps=800,
    openrouter_link="https://openrouter.ai/models/provider/model-name",
    description="Description of the model",
    is_free=True,  # or False for paid
    is_moe=False,  # True if MoE model
    is_awq=False   # True if AWQ quantized
)
```

### 2. Add GPU Preset (if needed)
```python
"new_gpu_config": {
    "name": "New GPU Configuration",
    "gpu_count": 4,
    "gpu_cost_per_hour": 1.8,
    "total_vram_gb": 320,
    "typical_models": ["Model1", "Model2"],
    "description": "Description of this configuration"
}
```

### 3. Add vLLM Preset (if needed)
```python
"new_model_vllm": {
    "model": "provider/model-name",
    "tensor_parallel_size": 4,
    "dtype": "auto",
    "max_model_len": 8192,
    "gpu_memory_utilization": 0.90,
    "max_num_seqs": 256,
    "max_num_batched_tokens": 8192,
    "port": 8000,
    "description": "Description of vLLM setup"
}
```

## Data Sources

### Pricing Information
- **OpenRouter**: Real-time pricing from OpenRouter API
- **Market rates**: Current competitive pricing
- **Self-hosted**: Estimated costs based on infrastructure

### Model Specifications
- **Hugging Face**: Model cards and documentation
- **Provider documentation**: Official model specifications
- **Benchmarking**: Performance testing results

### Infrastructure Costs
- **Cloud providers**: AWS, Azure, GCP pricing
- **On-premise**: Hardware and operational costs
- **Specialized providers**: RunPod, Vast.ai, etc.

## Maintenance

### Regular Updates
- **Pricing**: Update monthly based on market changes
- **Models**: Add new models as they become available
- **Specifications**: Update based on new benchmarks
- **Infrastructure**: Update costs based on market changes

### Version Control
- Keep track of changes in git
- Document major updates
- Maintain backward compatibility
- Test with calculators after updates

## Integration

This settings file is designed to be imported by:
- `llm_valuation.py` - LLM throughput calculator
- `gpu_profit_calculator.py` - GPU profitability calculator
- Future calculators and tools
- Deployment scripts and automation

The centralized approach ensures consistency across all tools and makes maintenance easier. 