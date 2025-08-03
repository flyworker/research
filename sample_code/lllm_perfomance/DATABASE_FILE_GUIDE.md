# Database File Storage Guide

This guide explains how configurations are saved directly to the SQLite database file (`llm_calculator.db`) in your LLM performance project.

## Overview

Your project uses **SQLite** as the database engine, which stores all data in a single file (`llm_calculator.db`). This provides:

- ✅ **Direct file storage**: All data saved to one file
- ✅ **No external dependencies**: No database server required
- ✅ **Portable**: Easy to backup, move, or share
- ✅ **Reliable**: ACID compliant transactions
- ✅ **Fast**: Optimized for read/write operations

## Database File Location

```
sample_code/lllm_perfomance/
├── llm_calculator.db          # Main database file
├── database.py               # Database management code
├── database_manager.py       # Command-line database tools
└── gpu_profit_calculator.py  # Web interface
```

## Database Schema

The database contains 5 main tables:

### 1. `gpu_configs` - GPU Specifications
```sql
- id (PRIMARY KEY)
- name (TEXT) - GPU model name
- gpu_type (TEXT) - Data Center, Consumer, Workstation
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

### 2. `deployment_configs` - Saved Configurations
```sql
- id (PRIMARY KEY)
- name (TEXT) - Configuration name
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

### 3. `model_configs` - Model Specifications
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

### 4. `user_preferences` - User Settings
```sql
- id (PRIMARY KEY)
- key (TEXT UNIQUE) - Preference key
- value (TEXT) - Preference value
- description (TEXT) - Description
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### 5. `calculation_history` - Historical Data
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

## How Configurations Are Saved

### 1. Web Interface Saving
When you click "💾 Save Configuration" in the web interface:

```python
# Frontend JavaScript collects form data
config = {
    "name": "8x H100 DeepSeek V3",
    "notes": "High-performance deployment",
    "gpu_cost": 2.0,
    "gpu_count": 8,
    "input_tps": 1000,
    "output_tps": 2000,
    "input_price": 0.28,
    "output_price": 0.88,
    "selected_model": "DeepSeek V3 671B",
    "selected_gpu": "NVIDIA H100 80GB"
}

# Backend API saves to database
@app.post("/save-configuration")
async def save_configuration(request: Request):
    data = await request.json()
    
    # Create deployment configuration
    deployment_config = DeploymentConfig(
        name=data.get("name", ""),
        gpu_config_id=1,
        gpu_count=data.get("gpu_count", 0),
        model_name=data.get("selected_model", ""),
        input_tps=data.get("input_tps", 0),
        output_tps=data.get("output_tps", 0),
        input_price_per_m=data.get("input_price", 0.0),
        output_price_per_m=data.get("output_price", 0.0),
        profit_per_day=calculated_profit,
        roi_percentage=calculated_roi,
        notes=data.get("notes", ""),
        is_favorite=False
    )
    
    # Save to database file
    config_id = db.insert_deployment_config(deployment_config)
```

### 2. Direct Database Operations
You can also work with the database file directly:

```python
from database import DatabaseManager

# Initialize database
db = DatabaseManager("llm_calculator.db")

# Save configuration directly
deployment_config = DeploymentConfig(
    name="My Configuration",
    gpu_count=4,
    model_name="Llama 3.1 70B",
    input_tps=500,
    output_tps=1000,
    input_price_per_m=0.25,
    output_price_per_m=0.75,
    profit_per_day=120.0,
    roi_percentage=15.0,
    notes="Test configuration"
)

config_id = db.insert_deployment_config(deployment_config)
print(f"Configuration saved with ID: {config_id}")
```

## Database Management Tools

### 1. Command-Line Database Manager
Use the `database_manager.py` script for direct database operations:

```bash
# Show database information
python database_manager.py info

# Show configuration statistics
python database_manager.py stats

# Export configurations to JSON
python database_manager.py export

# Create database backup
python database_manager.py backup

# List all saved configurations
python database_manager.py list

# Search configurations
python database_manager.py search

# Clean up old configurations
python database_manager.py clean
```

### 2. Web API Endpoints
The web interface provides API endpoints for database operations:

```bash
# Get database information
GET /database/info

# Get configuration statistics
GET /database/stats

# Export configurations
POST /database/export

# Create database backup
POST /database/backup
```

### 3. Direct SQLite Access
You can also access the database file directly using SQLite tools:

```bash
# Open database with SQLite CLI
sqlite3 llm_calculator.db

# View all saved configurations
SELECT * FROM deployment_configs;

# View profitable configurations
SELECT name, profit_per_day, roi_percentage 
FROM deployment_configs 
WHERE profit_per_day > 0;

# Export to CSV
.mode csv
.headers on
.output configurations.csv
SELECT * FROM deployment_configs;
.quit
```

## File Operations

### 1. Backup Database
```python
from database import DatabaseManager

db = DatabaseManager()
backup_path = db.backup_database()
print(f"Database backed up to: {backup_path}")
```

### 2. Export to JSON
```python
from database import DatabaseManager

db = DatabaseManager()
success = db.export_configurations_to_json("my_configs.json")
if success:
    print("Configurations exported successfully")
```

### 3. Import from JSON
```python
from database import DatabaseManager

db = DatabaseManager()
results = db.import_configurations_from_json("my_configs.json")
print(f"Imported {results['imported']['deployment_configs']} configurations")
```

## Database File Properties

### File Information
- **Format**: SQLite 3.x database
- **Location**: `sample_code/lllm_perfomance/llm_calculator.db`
- **Size**: Typically 10KB - 1MB depending on data
- **Permissions**: Read/write for the application
- **Backup**: Automatic timestamped backups available

### Performance
- **Read Speed**: Very fast for small to medium datasets
- **Write Speed**: Fast for individual operations
- **Concurrency**: Supports multiple readers, single writer
- **Scalability**: Good for up to 100,000+ configurations

### Data Integrity
- **ACID Compliance**: Atomic, Consistent, Isolated, Durable
- **Automatic Recovery**: Handles crashes gracefully
- **Foreign Keys**: Maintains referential integrity
- **Constraints**: Enforces data validation

## Best Practices

### 1. Regular Backups
```python
# Create daily backups
from datetime import datetime
import shutil

timestamp = datetime.now().strftime("%Y%m%d")
backup_file = f"llm_calculator_backup_{timestamp}.db"
shutil.copy2("llm_calculator.db", backup_file)
```

### 2. Data Validation
```python
# Validate before saving
def validate_configuration(config):
    if config.gpu_count <= 0:
        raise ValueError("GPU count must be positive")
    if config.profit_per_day < -10000:
        raise ValueError("Profit seems unrealistic")
    return True
```

### 3. Error Handling
```python
try:
    config_id = db.insert_deployment_config(config)
    print(f"Configuration saved with ID: {config_id}")
except Exception as e:
    print(f"Error saving configuration: {e}")
    # Handle error appropriately
```

### 4. Database Maintenance
```python
# Clean up old data periodically
def cleanup_old_configurations(days_old=30):
    cutoff_date = datetime.now() - timedelta(days=days_old)
    # Mark old configurations as inactive
    # This preserves data while cleaning up the active list
```

## Troubleshooting

### Common Issues

1. **Database Locked**
   ```bash
   # Check if another process is using the database
   lsof llm_calculator.db
   # Restart the application if needed
   ```

2. **Corrupted Database**
   ```bash
   # Try to repair
   sqlite3 llm_calculator.db "PRAGMA integrity_check;"
   # Restore from backup if needed
   ```

3. **Permission Issues**
   ```bash
   # Check file permissions
   ls -la llm_calculator.db
   # Fix permissions if needed
   chmod 644 llm_calculator.db
   ```

### Recovery Procedures

1. **From Backup**
   ```bash
   cp llm_calculator_backup_20231201.db llm_calculator.db
   ```

2. **From JSON Export**
   ```python
   db = DatabaseManager()
   results = db.import_configurations_from_json("backup.json")
   ```

3. **Manual Recovery**
   ```sql
   -- Use SQLite to recover data
   sqlite3 llm_calculator.db
   .dump > recovery.sql
   -- Edit recovery.sql if needed
   sqlite3 new_database.db < recovery.sql
   ```

## Summary

Your LLM performance project uses a **SQLite database file** (`llm_calculator.db`) that:

- ✅ **Stores all configurations directly in the file**
- ✅ **Provides fast, reliable data access**
- ✅ **Supports backup and recovery operations**
- ✅ **Offers both web and command-line interfaces**
- ✅ **Maintains data integrity and relationships**
- ✅ **Scales well for typical usage patterns**

The database file is the single source of truth for all your GPU configurations, model settings, and calculation history. All data is persisted directly to this file, making it easy to backup, share, or migrate your configurations. 