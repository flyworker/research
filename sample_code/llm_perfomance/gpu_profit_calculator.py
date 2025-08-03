from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import sys
sys.path.append('scripts')

from model_settings import ALL_MODELS, get_model_by_name, format_price
from database import DatabaseManager, GPUConfig, ModelConfig

app = FastAPI(title="GPU Profit Calculator")

# Create templates directory if it doesn't exist
templates_dir = "templates"
os.makedirs(templates_dir, exist_ok=True)

# Create static directory if it doesn't exist
static_dir = "templates/static"
os.makedirs(static_dir, exist_ok=True)

templates = Jinja2Templates(directory=templates_dir)

# Mount static files
app.mount("/static", StaticFiles(directory="templates/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def gpu_profit_calculator(request: Request):
    """Render the GPU profit calculator form."""
    # Get models from database
    db = DatabaseManager("scripts/llm_calculator.db")
    all_models = db.get_model_configs()
    free_models = [m for m in all_models if m.is_free]
    paid_models = [m for m in all_models if not m.is_free]
    
    # Get GPU configurations from database
    gpu_configs = db.get_gpu_configs()
    
    # Create GPU name mapping from short names to full database names
    gpu_name_mapping = {}
    for gpu in gpu_configs:
        # Map short names to full names
        if "H100" in gpu.name:
            gpu_name_mapping["H100"] = gpu.name
        elif "A100" in gpu.name:
            gpu_name_mapping["A100"] = gpu.name
        elif "RTX 3090" in gpu.name:
            gpu_name_mapping["RTX 3090"] = gpu.name
        elif "RTX 3080" in gpu.name:
            gpu_name_mapping["RTX 3080"] = gpu.name
    
    return templates.TemplateResponse("gpu_profit_calculator.html", {
        "request": request,
        "free_models": free_models,
        "paid_models": paid_models,
        "gpu_configs": gpu_configs,
        "gpu_name_mapping": gpu_name_mapping
    })

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Render the settings page."""
    db = DatabaseManager("scripts/llm_calculator.db")
    gpu_configs = db.get_gpu_configs()
    model_configs = db.get_model_configs()
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "gpu_configs": gpu_configs,
        "model_configs": model_configs
    })

@app.post("/settings/add-gpu")
async def add_gpu(
    name: str = Form(...),
    cost_per_hour: float = Form(...),
    vram_gb: int = Form(...),
    gpu_type: str = Form(...)
):
    """Add a new GPU configuration."""
    try:
        db = DatabaseManager("scripts/llm_calculator.db")
        gpu_config = GPUConfig(
            name=name,
            cost_per_hour=cost_per_hour,
            vram_gb=vram_gb,
            gpu_type=gpu_type
        )
        gpu_id = db.insert_gpu_config(gpu_config)
        return JSONResponse({"success": True, "message": f"GPU {name} added successfully", "gpu_id": gpu_id})
    except Exception as e:
        return JSONResponse({"success": False, "message": f"Error adding GPU: {str(e)}"})

@app.post("/settings/update-gpu")
async def update_gpu(
    name: str = Form(...),
    cost_per_hour: float = Form(...),
    vram_gb: int = Form(...),
    gpu_type: str = Form(...)
):
    """Update an existing GPU configuration."""
    try:
        db = DatabaseManager("scripts/llm_calculator.db")
        # First get the existing GPU config
        gpu_configs = db.get_gpu_configs()
        existing_gpu = None
        for gpu in gpu_configs:
            if gpu.name == name:
                existing_gpu = gpu
                break
        
        if existing_gpu:
            # Update the existing config
            existing_gpu.cost_per_hour = cost_per_hour
            existing_gpu.vram_gb = vram_gb
            existing_gpu.gpu_type = gpu_type
            success = db.update_gpu_config(existing_gpu)
            if success:
                return JSONResponse({"success": True, "message": f"GPU {name} updated successfully"})
            else:
                return JSONResponse({"success": False, "message": f"Failed to update GPU {name}"})
        else:
            return JSONResponse({"success": False, "message": f"GPU {name} not found"})
    except Exception as e:
        return JSONResponse({"success": False, "message": f"Error updating GPU: {str(e)}"})

@app.delete("/settings/delete-gpu/{gpu_name}")
async def delete_gpu(gpu_name: str):
    """Delete a GPU configuration."""
    try:
        db = DatabaseManager("scripts/llm_calculator.db")
        success = db.delete_gpu_config(gpu_name)
        if success:
            return JSONResponse({"success": True, "message": f"GPU {gpu_name} deleted successfully"})
        else:
            return JSONResponse({"success": False, "message": f"Failed to delete GPU {gpu_name}"})
    except Exception as e:
        return JSONResponse({"success": False, "message": f"Error deleting GPU: {str(e)}"})

@app.post("/settings/add-model")
async def add_model(
    name: str = Form(...),
    slug: str = Form(...),
    parameters_b: float = Form(...),
    context_window: str = Form(...),
    precision: str = Form(...),
    typical_gpu: str = Form(...),
    input_price_per_m: float = Form(...),
    output_price_per_m: float = Form(...),
    tokens_per_gpu_tps: int = Form(...),
    openrouter_link: str = Form(None),
    description: str = Form(None),
    is_free: bool = Form(False)
):
    """Add a new model configuration."""
    try:
        db = DatabaseManager("scripts/llm_calculator.db")
        model_config = ModelConfig(
            name=name,
            slug=slug,
            parameters_b=parameters_b,
            context_window=context_window,
            precision=precision,
            typical_gpu=typical_gpu,
            input_price_per_m=input_price_per_m,
            output_price_per_m=output_price_per_m,
            tokens_per_gpu_tps=tokens_per_gpu_tps,
            openrouter_link=openrouter_link,
            description=description,
            is_free=is_free
        )
        model_id = db.insert_model_config(model_config)
        return JSONResponse({"success": True, "message": f"Model {name} added successfully", "model_id": model_id})
    except Exception as e:
        return JSONResponse({"success": False, "message": f"Error adding model: {str(e)}"})

@app.post("/settings/update-model")
async def update_model(
    name: str = Form(...),
    slug: str = Form(None),
    parameters_b: float = Form(None),
    context_window: str = Form(None),
    precision: str = Form(None),
    typical_gpu: str = Form(None),
    input_price_per_m: float = Form(None),
    output_price_per_m: float = Form(None),
    tokens_per_gpu_tps: int = Form(None),
    openrouter_link: str = Form(None),
    description: str = Form(None),
    is_free: bool = Form(False)
):
    """Update an existing model configuration."""
    try:
        db = DatabaseManager("scripts/llm_calculator.db")
        # First get the existing model config
        model_configs = db.get_model_configs()
        existing_model = None
        for model in model_configs:
            if model.name == name:
                existing_model = model
                break
        
        if existing_model:
            # Update only the fields that are provided (not None)
            if slug is not None:
                existing_model.slug = slug
            if parameters_b is not None:
                existing_model.parameters_b = parameters_b
            if context_window is not None:
                existing_model.context_window = context_window
            if precision is not None:
                existing_model.precision = precision
            if typical_gpu is not None:
                existing_model.typical_gpu = typical_gpu
            if input_price_per_m is not None:
                existing_model.input_price_per_m = input_price_per_m
            if output_price_per_m is not None:
                existing_model.output_price_per_m = output_price_per_m
            if tokens_per_gpu_tps is not None:
                existing_model.tokens_per_gpu_tps = tokens_per_gpu_tps
            if openrouter_link is not None:
                existing_model.openrouter_link = openrouter_link
            if description is not None:
                existing_model.description = description
            existing_model.is_free = is_free  # Boolean can be updated directly
            success = db.update_model_config(existing_model)
            if success:
                return JSONResponse({"success": True, "message": f"Model {name} updated successfully"})
            else:
                return JSONResponse({"success": False, "message": f"Failed to update model {name}"})
        else:
            return JSONResponse({"success": False, "message": f"Model {name} not found"})
    except Exception as e:
        return JSONResponse({"success": False, "message": f"Error updating model: {str(e)}"})

@app.delete("/settings/delete-model/{model_name}")
async def delete_model(model_name: str):
    """Delete a model configuration."""
    try:
        db = DatabaseManager("scripts/llm_calculator.db")
        success = db.delete_model_config(model_name)
        if success:
            return JSONResponse({"success": True, "message": f"Model {model_name} deleted successfully"})
        else:
            return JSONResponse({"success": False, "message": f"Failed to delete model {model_name}"})
    except Exception as e:
        return JSONResponse({"success": False, "message": f"Error deleting model: {str(e)}"})

@app.get("/settings/get-model/{model_name}")
async def get_model(model_name: str):
    """Get model data by name for editing."""
    try:
        db = DatabaseManager("scripts/llm_calculator.db")
        model_configs = db.get_model_configs()
        for model in model_configs:
            if model.name == model_name:
                return JSONResponse({
                    "success": True,
                    "model": {
                        "name": model.name,
                        "slug": model.slug,
                        "parameters_b": model.parameters_b,
                        "context_window": model.context_window,
                        "precision": model.precision,
                        "typical_gpu": model.typical_gpu,
                        "input_price_per_m": model.input_price_per_m,
                        "output_price_per_m": model.output_price_per_m,
                        "tokens_per_gpu_tps": model.tokens_per_gpu_tps,
                        "openrouter_link": model.openrouter_link,
                        "description": model.description,
                        "is_free": model.is_free
                    }
                })
        return JSONResponse({"success": False, "message": f"Model {model_name} not found"})
    except Exception as e:
        return JSONResponse({"success": False, "message": f"Error getting model: {str(e)}"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 