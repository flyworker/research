# GPU Settings Data Usage Guide

This guide explains how to effectively use GPU settings data in your LLM performance project for analysis, optimization, and decision-making.

## Overview

Your project includes a comprehensive GPU settings system with:
- **Database Storage**: SQLite database with GPU configurations
- **Web Interface**: Settings management page
- **Analysis Tools**: Utilities for GPU optimization
- **Integration**: Seamless connection with profit calculations

## 1. Database Management

### Accessing GPU Settings

```python
from database import DatabaseManager, GPUConfig

# Initialize database
db = DatabaseManager()

# Get all active GPU configurations
gpu_configs = db.get_gpu_configs(active_only=True)

# Get specific GPU by name
h100_gpu = db.get_gpu_config_by_name("NVIDIA H100 80GB")

# Use GPU settings in calculations
for gpu in gpu_configs:
    hourly_cost = gpu.cost_per_hour
    vram_gb = gpu.vram_gb
    gpu_type = gpu.gpu_type
    power_watts = gpu.power_watts
```

### GPU Configuration Structure

```python
@dataclass
class GPUConfig:
    id: Optional[int] = None
    name: str = ""                    # GPU model name
    gpu_type: str = ""                # Data Center, Consumer, Workstation
    vram_gb: int = 0                  # VRAM in GB
    cost_per_hour: float = 0.0        # Hourly cost
    cost_per_month: float = 0.0       # Monthly cost
    power_watts: int = 0              # Power consumption
    memory_bandwidth_gbps: int = 0    # Memory bandwidth
    fp16_performance_tflops: float = 0.0  # FP16 performance
    fp8_performance_tflops: float = 0.0   # FP8 performance
    description: str = ""             # GPU description
    is_active: bool = True            # Active status
```

## 2. Web Interface Usage

### Managing GPU Settings

1. **Access Settings Page**: Click "⚙️ GPU Settings" button in the calculator
2. **Add New GPU**: Fill out the form with GPU specifications
3. **Edit Existing GPU**: Click "✏️ Edit" to modify configurations
4. **Delete GPU**: Click "🗑️ Delete" to remove (marks as inactive)

### Dynamic GPU Selection

The calculator now supports dynamic GPU selection:
- Select from available GPU configurations
- Auto-fills cost and specifications
- Integrates with model selection for optimal matching

## 3. Analysis and Optimization

### Using GPU Settings Analyzer

```python
from gpu_settings_utils import GPUSettingsAnalyzer

# Initialize analyzer
db = DatabaseManager()
analyzer = GPUSettingsAnalyzer(db)

# Analyze model compatibility
model_name = "DeepSeek V3 671B"
recommendations = analyzer.analyze_model_gpu_compatibility(model_name)

for rec in recommendations[:3]:
    print(f"GPU: {rec.gpu_config.name}")
    print(f"Efficiency Score: {rec.efficiency_score:.1f}/100")
    print(f"Required GPUs: {rec.required_gpus}")
    print(f"Total Cost/Hour: ${rec.total_cost_per_hour:.2f}")
    print(f"Reasoning: {rec.reasoning}")
```

### Cost Analysis

```python
# Analyze cost efficiency
cost_analysis = analyzer.analyze_cost_efficiency(
    gpu_config=gpu,
    gpu_count=8,
    target_tps=1000,
    input_price=0.28,
    output_price=0.88
)

print(f"Monthly Cost: ${cost_analysis.monthly_cost:.2f}")
print(f"ROI: {cost_analysis.roi_percentage:.1f}%")
print(f"Cost per Token: ${cost_analysis.cost_per_token:.6f}")
```

### GPU Configuration Comparison

```python
# Compare different GPU configurations
comparisons = analyzer.compare_gpu_configurations(
    model_name="DeepSeek V3 671B",
    target_tps=1000
)

for comp in comparisons[:3]:
    print(f"GPU: {comp['gpu_name']}")
    print(f"ROI: {comp['roi_percentage']:.1f}%")
    print(f"Monthly Cost: ${comp['monthly_cost']:.2f}")
    print(f"Required GPUs: {comp['required_gpus']}")
```

## 4. Model-GPU Compatibility

### VRAM Requirements Estimation

```python
from model_settings import estimate_vram_requirement

# Estimate VRAM requirements for a model
model = get_model_by_name("DeepSeek V3 671B")
required_vram = estimate_vram_requirement(
    model.parameters_b,  # 671.0
    model.precision      # "fp16"
)
print(f"Required VRAM: {required_vram}GB")
```

### Finding Compatible GPUs

```python
# Get compatible GPUs for a model
compatible_gpus = []
for gpu in gpu_configs:
    if gpu.vram_gb >= required_vram:
        compatible_gpus.append(gpu)

# Sort by cost efficiency
compatible_gpus.sort(key=lambda g: g.cost_per_hour / g.vram_gb)
```

## 5. Budget Optimization

### Finding Best GPU for Budget

```python
# Get best GPU within budget
best_gpu = analyzer.get_best_gpu_for_budget(
    budget_per_hour=2.0,
    min_vram_gb=40
)

if best_gpu:
    print(f"Best GPU: {best_gpu.name}")
    print(f"Cost: ${best_gpu.cost_per_hour:.2f}/hour")
    print(f"VRAM: {best_gpu.vram_gb}GB")
```

### Scaling Analysis

```python
# Analyze scaling requirements
scaling_info = calculate_gpu_scaling(
    model=model,
    gpu_config=gpu_config,
    target_tps=1000
)

print(f"Required GPUs: {scaling_info['required_gpus']}")
print(f"Efficiency: {scaling_info['efficiency_percentage']:.1f}%")
print(f"Monthly Cost: ${scaling_info['monthly_cost']:.2f}")
```

## 6. Integration Examples

### Profit Calculator Integration

```python
# In your FastAPI route
@app.get("/", response_class=HTMLResponse)
async def gpu_profit_calculator(request: Request):
    # Get GPU configurations from database
    gpu_configs = db.get_gpu_configs()
    
    return templates.TemplateResponse("gpu_profit_calculator.html", {
        "request": request,
        "free_models": free_models,
        "paid_models": paid_models,
        "gpu_configs": gpu_configs  # Pass to template
    })
```

### Model Selection Integration

```python
# Auto-select optimal GPU for model
def auto_select_gpu(model_name: str, budget: float = None):
    model = get_model_by_name(model_name)
    if not model:
        return None
    
    recommendations = analyzer.analyze_model_gpu_compatibility(model_name)
    
    if budget:
        # Filter by budget
        recommendations = [r for r in recommendations 
                          if r.total_cost_per_hour <= budget]
    
    return recommendations[0] if recommendations else None
```

## 7. Best Practices

### 1. Regular Updates
- Keep GPU costs updated with market prices
- Add new GPU models as they become available
- Update VRAM requirements based on model testing

### 2. Cost Monitoring
- Track GPU costs over time
- Monitor ROI changes
- Compare cloud vs. on-premise costs

### 3. Performance Optimization
- Use efficiency scores for GPU selection
- Consider VRAM utilization
- Balance cost vs. performance

### 4. Scaling Strategy
- Plan for GPU scaling requirements
- Consider multi-GPU configurations
- Factor in power and cooling costs

## 8. Example Workflows

### Workflow 1: New Model Deployment

```python
def deploy_new_model(model_name: str, target_tps: int, budget: float):
    # 1. Get model specifications
    model = get_model_by_name(model_name)
    
    # 2. Find compatible GPUs
    recommendations = analyzer.analyze_model_gpu_compatibility(model_name)
    
    # 3. Filter by budget
    affordable_options = [r for r in recommendations 
                         if r.total_cost_per_hour <= budget]
    
    # 4. Select optimal configuration
    if affordable_options:
        best_option = affordable_options[0]
        print(f"Recommended: {best_option.gpu_config.name}")
        print(f"GPUs needed: {best_option.required_gpus}")
        print(f"Total cost: ${best_option.total_cost_per_hour:.2f}/hour")
        return best_option
    
    return None
```

### Workflow 2: Cost Optimization

```python
def optimize_costs(current_config: Dict):
    # 1. Analyze current costs
    current_analysis = analyzer.analyze_cost_efficiency(
        current_config['gpu'],
        current_config['gpu_count'],
        current_config['target_tps'],
        current_config['input_price'],
        current_config['output_price']
    )
    
    # 2. Find alternatives
    alternatives = analyzer.compare_gpu_configurations(
        current_config['model_name'],
        current_config['target_tps']
    )
    
    # 3. Identify savings
    for alt in alternatives:
        savings = current_analysis.monthly_cost - alt['monthly_cost']
        if savings > 0:
            print(f"Switch to {alt['gpu_name']}: Save ${savings:.2f}/month")
```

## 9. Troubleshooting

### Common Issues

1. **No Compatible GPUs**: Increase budget or reduce model requirements
2. **Low ROI**: Check pricing or consider different models
3. **High Costs**: Look for more efficient GPU configurations
4. **VRAM Issues**: Consider model quantization or multi-GPU setups

### Debugging

```python
# Debug GPU compatibility
def debug_gpu_compatibility(model_name: str):
    model = get_model_by_name(model_name)
    required_vram = estimate_vram_requirement(model.parameters_b, model.precision)
    
    print(f"Model: {model_name}")
    print(f"Parameters: {model.parameters_b}B")
    print(f"Precision: {model.precision}")
    print(f"Required VRAM: {required_vram}GB")
    
    gpu_configs = db.get_gpu_configs()
    for gpu in gpu_configs:
        compatible = gpu.vram_gb >= required_vram
        print(f"  {gpu.name}: {gpu.vram_gb}GB - {'✓' if compatible else '✗'}")
```

## 10. Future Enhancements

### Planned Features
- GPU performance benchmarking
- Dynamic pricing updates
- Cloud GPU integration
- Power consumption analysis
- Cooling requirements calculation

### API Extensions
- REST API for GPU management
- Real-time cost monitoring
- Automated optimization recommendations
- Historical cost tracking

This guide provides a comprehensive framework for using GPU settings data effectively in your LLM performance project. The system is designed to be flexible, scalable, and easy to integrate with your existing workflows. 