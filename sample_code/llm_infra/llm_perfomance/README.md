# LLM Performance Calculator

A comprehensive FastAPI-based web application for calculating GPU profitability and performance metrics for Large Language Model (LLM) inference operations.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or uv package manager

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd sample_code/llm_perfomance
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database (first time only):**
   ```bash
   python scripts/init_database.py
   ```

4. **Run the application:**
   ```bash
   python gpu_profit_calculator.py
   ```

5. **Open in browser:**
   ```
   http://localhost:8001
   ```

## 📁 Project Structure

```
llm_perfomance/
├── gpu_profit_calculator.py          # Main FastAPI application
├── gpu_profit_calculator_clean.py    # Clean version of the main app
├── update_model_pricing.py           # Model pricing update utility
├── update_openrouter_pricing.py      # OpenRouter pricing sync
├── requirements.txt                  # Python dependencies
├── llm_calculator.db                 # SQLite database
├── Dockerfile                        # Docker container configuration
├── docker-compose.yml                # Docker Compose configuration
├── .dockerignore                     # Docker build exclusions
├── templates/                        # HTML templates and static files
│   ├── gpu_profit_calculator.html    # Main calculator interface
│   ├── settings.html                 # Settings management page
│   └── static/                       # CSS, JS, and other static assets
├── docs/                             # Comprehensive documentation
│   ├── README.md                     # Main documentation
│   ├── DATABASE_README.md            # Database schema and operations
│   ├── GPU_PROFIT_README.md          # Profit calculation methodology
│   ├── MODEL_SETTINGS_README.md      # Model configuration guide
│   ├── GPU_SETTINGS_GUIDE.md         # GPU configuration guide
│   ├── DATABASE_FILE_GUIDE.md        # Database file management
│   └── INSTALL_DEEPSEEK_V3_8H100.md  # DeepSeek installation guide
└── scripts/                          # Utility scripts and database management
    ├── database.py                   # Database models and schemas
    ├── database_manager.py           # Database operations and CRUD
    ├── model_settings.py             # Model configuration management
    ├── llm_valuation.py              # LLM valuation calculations
    ├── excel_to_models.py            # Import models from Excel files
    ├── populate_real_tps.py          # Populate real TPS data
    ├── migrate_database.py           # Database migration utilities
    ├── init_database.py              # Database initialization
    ├── update_gpu_costs.py           # Update GPU cost data
    ├── gpu_settings_utils.py         # GPU settings utilities
    ├── llm_calculator.db             # Database file (copy)
    └── model_tier_with_3090_3080.xlsx # Model tier data
```

## 🎯 Core Features

### GPU Profit Calculator
- **Real-time Profitability Analysis**: Calculate profit/loss for GPU-based LLM inference
- **Multi-GPU Support**: H100, A100, RTX 3090, RTX 3080 configurations
- **Cost Optimization**: Compare different GPU configurations and model combinations
- **Performance Metrics**: TPS (Tokens Per Second) calculations and optimization

### Model Management
- **Comprehensive Model Database**: Pre-configured models with pricing and performance data
- **Auto-population**: Automatic TPS and pricing from predefined models
- **Free vs Paid Models**: Support for both free and commercial models
- **OpenRouter Integration**: Sync pricing from OpenRouter API

### Settings & Configuration
- **GPU Settings Management**: Add, edit, and remove GPU configurations
- **Model Settings**: Configure model parameters, pricing, and performance data
- **Database Management**: SQLite-based configuration storage
- **Real-time Updates**: Dynamic configuration updates without restart

## 🔧 Configuration

### Database Setup
The application uses SQLite for data persistence. The database includes:
- **GPU Configurations**: Cost per hour, VRAM, GPU type
- **Model Configurations**: Parameters, pricing, TPS, context windows
- **Performance Data**: Real-world TPS measurements

### Environment Configuration
- **Port**: Default 8001 (configurable in main application)
- **Database Path**: `scripts/llm_calculator.db`
- **Static Files**: Served from `templates/static/`

### Environment Variables
```bash
# Application settings
PYTHONPATH=/app                    # Python path for imports
PYTHONDONTWRITEBYTECODE=1         # Don't write .pyc files
PYTHONUNBUFFERED=1                # Unbuffered Python output

# Database settings (optional)
DATABASE_PATH=scripts/llm_calculator.db  # Custom database path

# Server settings (optional)
HOST=0.0.0.0                      # Server host
PORT=8001                         # Server port
```

## 📚 Documentation

### Core Documentation
- **[DATABASE_README.md](docs/DATABASE_README.md)** - Database schema, operations, and management
- **[GPU_PROFIT_README.md](docs/GPU_PROFIT_README.md)** - Profit calculation methodology and formulas
- **[MODEL_SETTINGS_README.md](docs/MODEL_SETTINGS_README.md)** - Model configuration and management
- **[GPU_SETTINGS_GUIDE.md](docs/GPU_SETTINGS_GUIDE.md)** - GPU configuration and optimization

### Advanced Guides
- **[DATABASE_FILE_GUIDE.md](docs/DATABASE_FILE_GUIDE.md)** - Database file management and backup
- **[INSTALL_DEEPSEEK_V3_8H100.md](docs/INSTALL_DEEPSEEK_V3_8H100.md)** - DeepSeek model installation guide

## 🛠️ Development & Utilities

### Database Management Scripts
- `init_database.py` - Initialize database with default configurations
- `migrate_database.py` - Database schema migrations
- `database_manager.py` - CRUD operations for database entities

### Model Management Scripts
- `model_settings.py` - Model configuration and validation
- `excel_to_models.py` - Import model data from Excel spreadsheets
- `populate_real_tps.py` - Update TPS data with real measurements
- `llm_valuation.py` - Advanced LLM valuation calculations

### GPU Management Scripts
- `gpu_settings_utils.py` - GPU configuration utilities
- `update_gpu_costs.py` - Update GPU pricing data

### Pricing Updates
- `update_model_pricing.py` - Update model pricing from external sources
- `update_openrouter_pricing.py` - Sync pricing with OpenRouter API

## 🔄 API Endpoints

### Main Routes
- `GET /` - Main calculator interface
- `GET /settings` - Settings management page

### GPU Management
- `POST /settings/add-gpu` - Add new GPU configuration
- `POST /settings/update-gpu` - Update existing GPU configuration
- `DELETE /settings/delete-gpu/{gpu_name}` - Remove GPU configuration

### Model Management
- `POST /settings/add-model` - Add new model configuration
- `POST /settings/update-model` - Update existing model configuration
- `DELETE /settings/delete-model/{model_name}` - Remove model configuration
- `GET /settings/get-model/{model_name}` - Get model details

## 🚀 Deployment

### Local Development
```bash
# Development mode with auto-reload
uvicorn gpu_profit_calculator:app --reload --port 8001
```

### Production Deployment
```bash
# Production mode
uvicorn gpu_profit_calculator:app --host 0.0.0.0 --port 8001
```

### Docker Deployment

#### Using Docker Compose (Recommended)
```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

#### Using Docker directly
```bash
# Build the image
docker build -t llm-calculator .

# Run the container
docker run -d -p 8001:8001 --name llm-calculator llm-calculator

# View logs
docker logs -f llm-calculator

# Stop the container
docker stop llm-calculator
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the research repository. See the main [LICENSE](../LICENSE) file for details.

## 🔗 Dependencies

- **FastAPI** (>=0.110) - Modern web framework for building APIs
- **Uvicorn** (>=0.29) - ASGI server for FastAPI
- **Jinja2** (>=3.1) - Template engine for HTML rendering

## 📊 Performance Considerations

- **Async Operations**: All database operations are asynchronous
- **Caching**: Static files are served efficiently
- **Database Optimization**: SQLite with proper indexing
- **Memory Management**: Efficient data structures for large model datasets

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# If database doesn't exist, initialize it
python scripts/init_database.py
```

#### Port Already in Use
```bash
# Check what's using port 8001
lsof -i :8001

# Kill the process or use a different port
uvicorn gpu_profit_calculator:app --port 8002
```

#### Docker Build Issues
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t llm-calculator .
```

#### Import Errors
```bash
# Ensure scripts directory is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/scripts"

# Or run from the correct directory
cd sample_code/llm_perfomance
python gpu_profit_calculator.py
```

### Logs and Debugging
```bash
# Enable debug logging
export PYTHONPATH=/app
python -u gpu_profit_calculator.py

# Docker logs
docker-compose logs -f llm-calculator
``` 