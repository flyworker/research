from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import sys
sys.path.append('scripts')

from model_settings import ALL_MODELS, get_model_by_name, format_price
from database import DatabaseManager, GPUConfig

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
    # Get models from settings
    free_models = [m for m in ALL_MODELS if m.is_free]
    paid_models = [m for m in ALL_MODELS if not m.is_free]
    
    # Get GPU configurations from database
    db = DatabaseManager()
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
    db = DatabaseManager()
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
        db = DatabaseManager()
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
        db = DatabaseManager()
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
        db = DatabaseManager()
        success = db.delete_gpu_config(gpu_name)
        if success:
            return JSONResponse({"success": True, "message": f"GPU {gpu_name} deleted successfully"})
        else:
            return JSONResponse({"success": False, "message": f"Failed to delete GPU {gpu_name}"})
    except Exception as e:
        return JSONResponse({"success": False, "message": f"Error deleting GPU: {str(e)}"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 