# LLM Performance Calculator

A FastAPI-based web application for calculating GPU profitability for LLM inference.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python gpu_profit_calculator.py
   ```

3. **Open in browser:**
   ```
   http://localhost:8001
   ```

## 📁 Project Structure

```
lllm_perfomance/
├── gpu_profit_calculator.py    # Main FastAPI application
├── requirements.txt            # Python dependencies
├── templates/                  # HTML templates
│   ├── gpu_profit_calculator.html  # Main calculator page
│   └── settings.html              # Settings page
├── docs/                       # Documentation
│   ├── README.md
│   ├── DATABASE_README.md
│   ├── GPU_PROFIT_README.md
│   └── ...
└── scripts/                    # Utility scripts
    ├── database.py
    ├── database_manager.py
    ├── model_settings.py
    ├── llm_valuation.py
    ├── excel_to_models.py
    ├── populate_real_tps.py
    ├── migrate_database.py
    ├── init_database.py
    ├── update_gpu_costs.py
    ├── gpu_settings_utils.py
    ├── llm_calculator.db
    └── model_tier_with_3090_3080.xlsx
```

## 🎯 Features

- **GPU Profit Calculator**: Calculate profitability for GPU-based LLM inference
- **Model Selection**: Auto-populate TPS and pricing from predefined models
- **GPU Selection**: Choose from available GPU configurations with auto-selection
- **Real-time Calculations**: Instant profit/loss analysis
- **Settings Management**: Configure GPU costs and model parameters

## 🔧 Configuration

- **GPU Settings**: Manage GPU configurations and costs
- **Model Settings**: Configure model parameters and pricing
- **Database**: SQLite database for storing configurations

## 📚 Documentation

See the `docs/` folder for detailed documentation:
- `DATABASE_README.md` - Database schema and management
- `GPU_PROFIT_README.md` - Profit calculation methodology
- `MODEL_SETTINGS_README.md` - Model configuration guide
- `GPU_SETTINGS_GUIDE.md` - GPU configuration guide

## 🛠️ Development

Utility scripts in the `scripts/` folder:
- `database.py` - Database models and schemas
- `database_manager.py` - Database operations
- `model_settings.py` - Model configuration management
- `llm_valuation.py` - LLM valuation calculations
- `excel_to_models.py` - Import models from Excel
- `populate_real_tps.py` - Populate real TPS data
- `migrate_database.py` - Database migration utilities
- `init_database.py` - Database initialization
- `update_gpu_costs.py` - Update GPU cost data
- `gpu_settings_utils.py` - GPU settings utilities 