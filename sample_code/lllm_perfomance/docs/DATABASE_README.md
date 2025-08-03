# Database Management System

A comprehensive SQLite database system for storing and managing LLM calculator configuration data, including GPU specifications, model configurations, deployment settings, and calculation history.

## Overview

The database system provides persistent storage for:
- **GPU Configurations**: Detailed specifications, pricing, and performance data
- **Model Configurations**: All models from your Excel data with pricing and TPS
- **Deployment Configurations**: Saved deployment scenarios and favorites
- **User Preferences**: Default settings and user customizations
- **Calculation History**: Track all calculations for analysis and comparison

## Database Schema

### Tables

#### 1. `gpu_configs`
Stores GPU specifications and pricing:
```sql
- id (PRIMARY KEY)
- name (TEXT) - GPU model name
- gpu_type (TEXT) - Data Center or Consumer
- vram_gb (INTEGER) - VRAM in GB
- cost_per_hour (REAL) - Hourly cost
- cost_per_month (REAL) - Monthly cost
- power_watts (INTEGER) - Power consumption
- memory_bandwidth_gbps (INTEGER) - Memory bandwidth
- fp16_performance_tflops (REAL) - FP16 performance
- fp8_performance_tflops (REAL) - FP8 performance
- description (TEXT) - GPU description
- is_active (BOOLEAN) - Active status
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

#### 2. `model_configs`
Stores model configurations from Excel:
```sql
- id (PRIMARY KEY)
- name (TEXT) - Model name
- slug (TEXT) - Model identifier
- parameters_b (REAL) - Billions of parameters
- context_window (TEXT) - Max context length
- precision (TEXT) - fp8, fp16, MoE, AWQ
- typical_gpu (TEXT) - Recommended GPU
- input_price_per_m (REAL) - Input price per million tokens
- output_price_per_m (REAL) - Output price per million tokens
- tokens_per_gpu_tps (INTEGER) - Tokens per second per GPU
- openrouter_link (TEXT) - OpenRouter model page
- description (TEXT) - Model description
- is_free (BOOLEAN) - Free tier flag
- is_moe (BOOLEAN) - Mixture of Experts flag
- is_awq (BOOLEAN) - AWQ quantization flag
- is_active (BOOLEAN) - Active status
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

#### 3. `deployment_configs`
Stores saved deployment scenarios:
```sql
- id (PRIMARY KEY)
- name (TEXT) - Deployment name
- gpu_config_id (INTEGER) - Reference to gpu_configs
- gpu_count (INTEGER) - Number of GPUs
- model_name (TEXT) - Model name
- input_tps (INTEGER) - Input tokens per second
- output_tps (INTEGER) - Output tokens per second
- input_price_per_m (REAL) - Input pricing
- output_price_per_m (REAL) - Output pricing
- profit_per_day (REAL) - Calculated daily profit
- roi_percentage (REAL) - Return on investment
- notes (TEXT) - User notes
- is_favorite (BOOLEAN) - Favorite flag
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

#### 4. `user_preferences`
Stores user settings and defaults:
```sql
- id (PRIMARY KEY)
- key (TEXT UNIQUE) - Preference key
- value (TEXT) - Preference value
- description (TEXT) - Description
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

#### 5. `calculation_history`
Tracks all calculations for analysis:
```sql
- id (PRIMARY KEY)
- deployment_config_id (INTEGER) - Reference to deployment_configs
- gpu_cost_per_hour (REAL) - GPU cost used
- gpu_count (INTEGER) - GPU count used
- input_tps (INTEGER) - Input TPS used
- output_tps (INTEGER) - Output TPS used
- input_price_per_m (REAL) - Input price used
- output_price_per_m (REAL) - Output price used
- profit_per_day (REAL) - Calculated profit
- roi_percentage (REAL) - Calculated ROI
- calculation_date (TIMESTAMP) - When calculated
```

## Usage

### Initialization

```python
from database import get_db

# Get database instance
db = get_db()

# Initialize with default data
python init_database.py
```

### GPU Management

```python
from database import GPUConfig

# Add new GPU
gpu = GPUConfig(
    name="NVIDIA H100 80GB",
    gpu_type="Data Center",
    vram_gb=80,
    cost_per_hour=2.0,
    cost_per_month=1440.0,
    power_watts=700,
    memory_bandwidth_gbps=3350,
    fp16_performance_tflops=989.0,
    fp8_performance_tflops=1979.0,
    description="NVIDIA's flagship data center GPU"
)

gpu_id = db.insert_gpu_config(gpu)

# Get all GPUs
gpus = db.get_gpu_configs()

# Get specific GPU
gpu = db.get_gpu_config_by_id(gpu_id)
```

### Model Management

```python
from database import ModelConfig

# Add new model
model = ModelConfig(
    name="DeepSeek V3 671B",
    slug="custom/deepseek-v3-671b",
    parameters_b=671.0,
    context_window="8K",
    precision="fp16",
    typical_gpu="H100",
    input_price_per_m=0.28,
    output_price_per_m=0.88,
    tokens_per_gpu_tps=310,
    description="Enterprise tier model"
)

model_id = db.insert_model_config(model)

# Get all models
models = db.get_model_configs()

# Get model by name
model = db.get_model_config_by_name("DeepSeek V3 671B")
```

### Deployment Management

```python
from database import DeploymentConfig

# Save deployment configuration
deployment = DeploymentConfig(
    name="8x H100 DeepSeek V3",
    gpu_config_id=1,  # H100
    gpu_count=8,
    model_name="DeepSeek V3 671B",
    input_tps=93,
    output_tps=217,
    input_price_per_m=0.28,
    output_price_per_m=0.88,
    profit_per_day=1200.0,
    roi_percentage=45.0,
    notes="High-performance deployment",
    is_favorite=True
)

deployment_id = db.insert_deployment_config(deployment)

# Get favorite deployments
favorites = db.get_deployment_configs(favorites_only=True)
```

### User Preferences

```python
# Set preferences
db.set_user_preference("default_gpu_cost", "2.0", "Default GPU cost per hour")
db.set_user_preference("default_gpu_count", "8", "Default number of GPUs")
db.set_user_preference("currency", "USD", "Preferred currency")

# Get preferences
default_cost = db.get_user_preference("default_gpu_cost", "1.0")
default_count = db.get_user_preference("default_gpu_count", "4")
currency = db.get_user_preference("currency", "USD")
```

### Calculation History

```python
# Save calculation
db.save_calculation_history(
    deployment_config_id=1,
    gpu_cost_per_hour=2.0,
    gpu_count=8,
    input_tps=1000,
    output_tps=2000,
    input_price_per_m=0.28,
    output_price_per_m=0.88,
    profit_per_day=1200.0,
    roi_percentage=45.0
)

# Get calculation history
history = db.get_calculation_history(limit=50)
```

## Database Commands

### Initialize Database
```bash
python init_database.py
```

### Show Statistics
```bash
python init_database.py stats
```

### Export to JSON
```bash
python init_database.py export
```

## Default Data

### GPU Configurations
- **NVIDIA H100 80GB**: $2.00/hour, 80GB VRAM, Data Center
- **NVIDIA A100 80GB**: $1.50/hour, 80GB VRAM, Data Center
- **NVIDIA RTX 3090**: $0.75/hour, 24GB VRAM, Consumer
- **NVIDIA RTX 3080**: $0.55/hour, 10GB VRAM, Consumer

### Model Configurations
- **15 models** from your Excel data
- **3 free models**: Stheno 8B, TheSpice 8B, Lyra 12B V4
- **12 paid models**: Including DeepSeek V3 671B, Mixtral 8×7B, etc.

### User Preferences
- **Default GPU Cost**: $2.0/hour
- **Default GPU Count**: 8
- **Currency**: USD

## Integration with Calculator

The database can be integrated with the GPU Profit Calculator to:
- Load GPU configurations dynamically
- Save deployment scenarios
- Track calculation history
- Store user preferences
- Provide persistent data across sessions

## Benefits

1. **Persistent Storage**: All data persists between sessions
2. **Scalable**: Easy to add new GPUs, models, and configurations
3. **Historical Analysis**: Track all calculations for trend analysis
4. **User Customization**: Save preferences and favorite deployments
5. **Data Integrity**: Proper foreign key relationships and constraints
6. **Export/Import**: JSON export for backup and analysis

## File Structure

```
database.py          # Main database management system
init_database.py     # Database initialization script
llm_calculator.db    # SQLite database file (created automatically)
DATABASE_README.md   # This documentation
```

The database system provides a robust foundation for managing all LLM calculator data with full CRUD operations, relationships, and historical tracking. 