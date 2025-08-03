from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
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

# Create the HTML template
template_path = os.path.join(templates_dir, "gpu_profit_calculator.html")
with open(template_path, "w") as f:
    f.write('''<!DOCTYPE html>
<html>
<head>
    <title>GPU Profit Calculator</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: 'Inter', sans-serif; }
        .input-field { @apply border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500; }
        .result-card { @apply bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6 shadow-sm; }
        .profit-positive { @apply text-green-600 font-semibold; }
        .profit-negative { @apply text-red-600 font-semibold; }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="container mx-auto px-4 py-8 max-w-6xl">
        <div class="text-center mb-8">
            <div class="flex justify-between items-center mb-4">
                <div></div>
                <h1 class="text-3xl font-bold text-gray-800">GPU Profit Calculator</h1>
                <button onclick="window.location.href='/settings'" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                    ⚙️ Settings
                </button>
            </div>
            <p class="text-gray-600">Calculate profitability for GPU-based LLM inference</p>
        </div>

        <div class="grid lg:grid-cols-3 gap-8">
            <!-- Input Form -->
            <div class="lg:col-span-2 bg-white rounded-lg shadow-md p-6">
                <h2 class="text-xl font-semibold mb-4 text-gray-800">Configuration</h2>
                
                <div class="grid md:grid-cols-2 gap-6">
                    <!-- Model Selection -->
                    <div class="md:col-span-2">
                        <label class="block text-sm font-medium text-gray-700 mb-1">Select Model (Optional)</label>
                        <select id="modelSelect" class="input-field w-full" onchange="onModelSelect()">
                            <option value="">-- Select a model to auto-fill parameters --</option>
                            <optgroup label="Free Models">
                                {% for model in free_models %}
                                <option value="{{ model.name }}" data-input-tps="{{ model.tokens_per_gpu_tps * 0.3 }}" data-output-tps="{{ model.tokens_per_gpu_tps * 0.7 }}" data-input-price="{{ model.input_price_per_m }}" data-output-price="{{ model.output_price_per_m }}" data-gpu="{{ model.typical_gpu }}" data-parameters="{{ model.parameters_b }}" data-precision="{{ model.precision }}">{{ model.name }} ({{ model.typical_gpu }}, {{ model.parameters_b }}B)</option>
                                {% endfor %}
                            </optgroup>
                            <optgroup label="Paid Models">
                                {% for model in paid_models %}
                                <option value="{{ model.name }}" data-input-tps="{{ model.tokens_per_gpu_tps * 0.3 }}" data-output-tps="{{ model.tokens_per_gpu_tps * 0.7 }}" data-input-price="{{ model.input_price_per_m }}" data-output-price="{{ model.output_price_per_m }}" data-gpu="{{ model.typical_gpu }}" data-parameters="{{ model.parameters_b }}" data-precision="{{ model.precision }}">{{ model.name }} ({{ model.typical_gpu }}, {{ model.parameters_b }}B)</option>
                                {% endfor %}
                            </optgroup>
                        </select>
                        <p class="text-xs text-gray-500 mt-1">Select a model to automatically populate TPS and pricing</p>
                    </div>
                    
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">GPU Cost per Hour ($)</label>
                        <input type="number" id="gpuCost" value="2.0" step="0.1" min="0" 
                               class="input-field w-full" onchange="calculateProfit()">
                    </div>
                    
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">GPU Count</label>
                        <input type="number" id="gpuCount" value="8" min="1" 
                               class="input-field w-full" onchange="calculateProfit()">
                    </div>
                    
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Input Tokens/sec</label>
                        <input type="number" id="inputTPS" value="1000" min="0" 
                               class="input-field w-full" onchange="calculateProfit()">
                    </div>
                    
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Output Tokens/sec</label>
                        <input type="number" id="outputTPS" value="2000" min="0" 
                               class="input-field w-full" onchange="calculateProfit()">
                    </div>
                    
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Input Price ($/M tokens)</label>
                        <input type="number" id="inputPrice" value="0.28" step="0.01" min="0" 
                               class="input-field w-full" onchange="calculateProfit()">
                    </div>
                    
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Output Price ($/M tokens)</label>
                        <input type="number" id="outputPrice" value="0.88" step="0.01" min="0" 
                               class="input-field w-full" onchange="calculateProfit()">
                    </div>
                </div>
            </div>

            <!-- Results -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-xl font-semibold mb-4 text-gray-800">Profitability Analysis</h2>
                
                <div class="space-y-3">
                    <div class="flex justify-between">
                        <span class="text-gray-600">Total TPS:</span>
                        <span class="font-mono font-semibold" id="totalTPS">3,000</span>
                    </div>
                    
                    <div class="flex justify-between">
                        <span class="text-gray-600">Tokens/hour:</span>
                        <span class="font-mono font-semibold" id="tokensPerHour">10,800,000</span>
                    </div>
                    
                    <div class="flex justify-between">
                        <span class="text-gray-600">Cost/hour:</span>
                        <span class="font-mono font-semibold text-red-600" id="costPerHour">$16.00</span>
                    </div>
                    
                    <div class="flex justify-between">
                        <span class="text-gray-600">Revenue/M tokens:</span>
                        <span class="font-mono font-semibold" id="revenuePerMTokens">$0.00</span>
                    </div>
                    
                    <div class="flex justify-between">
                        <span class="text-gray-600">Cost/M tokens:</span>
                        <span class="font-mono font-semibold text-red-600" id="costPerMTokens">$0.00</span>
                    </div>
                    
                    <div class="flex justify-between">
                        <span class="text-gray-600">Profit/M tokens:</span>
                        <span class="font-mono font-semibold" id="profitPerMTokens">$0.00</span>
                    </div>
                    
                    <hr class="my-4">
                    
                    <div class="flex justify-between text-lg">
                        <span class="text-gray-700 font-medium">Profit/hour:</span>
                        <span class="font-mono font-bold" id="profitPerHour">$0.00</span>
                    </div>
                    
                    <div class="flex justify-between text-xl">
                        <span class="text-gray-800 font-semibold">Profit/day:</span>
                        <span class="font-mono font-bold" id="profitPerDay">$0.00</span>
                    </div>
                    
                    <div class="flex justify-between text-lg">
                        <span class="text-gray-700 font-medium">ROI (30 days):</span>
                        <span class="font-mono font-bold" id="roi30Days">0%</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Additional Insights -->
        <div class="mt-8 bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-semibold mb-4 text-gray-800">Insights & Recommendations</h2>
            
            <div class="grid md:grid-cols-2 gap-6">
                <div>
                    <h3 class="font-semibold text-gray-700 mb-2">Break-even Analysis</h3>
                    <div class="space-y-2 text-sm">
                        <div class="flex justify-between">
                            <span>Break-even TPS:</span>
                            <span class="font-mono" id="breakEvenTPS">-</span>
                        </div>
                        <div class="flex justify-between">
                            <span>Current utilization:</span>
                            <span class="font-mono" id="utilization">-</span>
                        </div>
                    </div>
                </div>
                
                <div>
                    <h3 class="font-semibold text-gray-700 mb-2">Scaling Impact</h3>
                    <div class="space-y-2 text-sm">
                        <div class="flex justify-between">
                            <span>2x GPU count:</span>
                            <span class="font-mono" id="scaling2x">-</span>
                        </div>
                        <div class="flex justify-between">
                            <span>2x TPS:</span>
                            <span class="font-mono" id="tps2x">-</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Model Information -->
        <div class="mt-8 bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-semibold mb-4 text-gray-800">Selected Model Information</h2>
            <div id="modelInfo" class="text-gray-600">
                <p>Select a model above to see detailed information</p>
            </div>
        </div>
    </div>

    <script>
        function onModelSelect() {
            const select = document.getElementById('modelSelect');
            const selectedOption = select.options[select.selectedIndex];
            
            if (selectedOption.value) {
                const inputTPS = parseFloat(selectedOption.dataset.inputTps) || 0;
                const outputTPS = parseFloat(selectedOption.dataset.outputTps) || 0;
                const inputPrice = parseFloat(selectedOption.dataset.inputPrice?.replace('$', '')) || 0;
                const outputPrice = parseFloat(selectedOption.dataset.outputPrice?.replace('$', '')) || 0;
                const gpu = selectedOption.dataset.gpu || '';
                const parameters = selectedOption.dataset.parameters || '';
                const precision = selectedOption.dataset.precision || '';
                
                document.getElementById('inputTPS').value = Math.round(inputTPS);
                document.getElementById('outputTPS').value = Math.round(outputTPS);
                document.getElementById('inputPrice').value = inputPrice;
                document.getElementById('outputPrice').value = outputPrice;
                
                // Update model info with GPU details
                updateModelInfo(selectedOption.value, gpu, parameters, precision, inputTPS + outputTPS);
                
                calculateProfit();
            }
        }
        
        function updateModelInfo(modelName, gpu, parameters, precision, totalTPS) {
            const modelInfo = document.getElementById('modelInfo');
            modelInfo.innerHTML = `
                <div class="grid md:grid-cols-2 gap-4">
                    <div>
                        <h3 class="font-semibold text-gray-700 mb-2">GPU Requirements</h3>
                        <div class="space-y-2 text-sm">
                            <div class="flex justify-between">
                                <span>Recommended GPU:</span>
                                <span class="font-mono font-semibold text-blue-600">${gpu}</span>
                            </div>
                            <div class="flex justify-between">
                                <span>GPU Type:</span>
                                <span class="font-mono">${getGPUType(gpu)}</span>
                            </div>
                            <div class="flex justify-between">
                                <span>VRAM Required:</span>
                                <span class="font-mono">${getVRAMRequirement(parameters, precision)}</span>
                            </div>
                            <div class="flex justify-between">
                                <span>Cost/Hour:</span>
                                <span class="font-mono">${getGPUHourlyCost(gpu)}</span>
                            </div>
                        </div>
                    </div>
                    <div>
                        <h3 class="font-semibold text-gray-700 mb-2">Model Specifications</h3>
                        <div class="space-y-2 text-sm">
                            <div class="flex justify-between">
                                <span>Model:</span>
                                <span class="font-mono font-semibold">${modelName}</span>
                            </div>
                            <div class="flex justify-between">
                                <span>Parameters:</span>
                                <span class="font-mono">${parameters}B</span>
                            </div>
                            <div class="flex justify-between">
                                <span>Precision:</span>
                                <span class="font-mono">${precision}</span>
                            </div>
                            <div class="flex justify-between">
                                <span>Total TPS:</span>
                                <span class="font-mono">${totalTPS.toLocaleString()}</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="mt-4 p-3 bg-blue-50 rounded-lg">
                    <p class="text-sm text-blue-800"><strong>Note:</strong> Model parameters have been auto-filled based on ${gpu} specifications. Adjust GPU cost and count to match your actual deployment.</p>
                </div>
            `;
        }
        
        function getGPUType(gpu) {
            if (gpu.includes('H100')) return 'Data Center GPU';
            if (gpu.includes('A100')) return 'Data Center GPU';
            if (gpu.includes('RTX 3090')) return 'Consumer GPU';
            if (gpu.includes('RTX 3080')) return 'Consumer GPU';
            return 'GPU';
        }
        
        function getVRAMRequirement(parameters, precision) {
            const params = parseFloat(parameters);
            if (precision === 'MoE') {
                return '~80GB+ (MoE models)';
            } else if (params >= 100) {
                return '~80GB+ (Large models)';
            } else if (params >= 30) {
                return '~40-80GB';
            } else if (params >= 10) {
                return '~20-40GB';
            } else {
                return '~8-20GB';
            }
        }
        
        function getGPUHourlyCost(gpu) {
            if (gpu.includes('H100')) return '$2.00-3.00/hour';
            if (gpu.includes('A100')) return '$1.50-2.50/hour';
            if (gpu.includes('RTX 3090')) return '$0.50-1.00/hour';
            if (gpu.includes('RTX 3080')) return '$0.30-0.80/hour';
            return '$1.00-2.00/hour';
        }

        function calculateProfit() {
            const gpuCost = parseFloat(document.getElementById('gpuCost').value) || 0;
            const gpuCount = parseInt(document.getElementById('gpuCount').value) || 0;
            const inputTPS = parseFloat(document.getElementById('inputTPS').value) || 0;
            const outputTPS = parseFloat(document.getElementById('outputTPS').value) || 0;
            const inputPrice = parseFloat(document.getElementById('inputPrice').value) || 0;
            const outputPrice = parseFloat(document.getElementById('outputPrice').value) || 0;

            const totalTPS = inputTPS + outputTPS;
            const tokensPerHour = totalTPS * 3600;
            const costPerHour = gpuCost * gpuCount;
            const costPerMTokens = (costPerHour / tokensPerHour) * 1_000_000;

            const revenuePerMTokens = ((inputTPS * inputPrice) + (outputTPS * outputPrice)) / totalTPS;
            const profitPerMTokens = revenuePerMTokens - costPerMTokens;
            const profitPerHour = profitPerMTokens * tokensPerHour / 1_000_000;
            const profitPerDay = profitPerHour * 24;

            // Update display
            document.getElementById('totalTPS').textContent = totalTPS.toLocaleString();
            document.getElementById('tokensPerHour').textContent = tokensPerHour.toLocaleString();
            document.getElementById('costPerHour').textContent = '$' + costPerHour.toFixed(2);
            document.getElementById('revenuePerMTokens').textContent = '$' + revenuePerMTokens.toFixed(2);
            document.getElementById('costPerMTokens').textContent = '$' + costPerMTokens.toFixed(2);
            document.getElementById('profitPerMTokens').textContent = '$' + profitPerMTokens.toFixed(2);
            
            const profitPerHourElement = document.getElementById('profitPerHour');
            profitPerHourElement.textContent = '$' + profitPerHour.toFixed(2);
            profitPerHourElement.className = profitPerHour >= 0 ? 'font-mono font-bold profit-positive' : 'font-mono font-bold profit-negative';
            
            const profitPerDayElement = document.getElementById('profitPerDay');
            profitPerDayElement.textContent = '$' + profitPerDay.toFixed(2);
            profitPerDayElement.className = profitPerDay >= 0 ? 'font-mono font-bold profit-positive' : 'font-mono font-bold profit-negative';

            // Calculate ROI (assuming $20k per H100)
            const totalGPUInvestment = gpuCount * 20000;
            const roi30Days = totalGPUInvestment > 0 ? (profitPerDay * 30 / totalGPUInvestment * 100) : 0;
            document.getElementById('roi30Days').textContent = roi30Days.toFixed(1) + '%';

            // Break-even analysis
            if (revenuePerMTokens > 0) {
                const breakEvenTPS = costPerHour / (revenuePerMTokens * 3600 / 1_000_000);
                document.getElementById('breakEvenTPS').textContent = breakEvenTPS.toFixed(0);
                
                const utilization = totalTPS > 0 ? (totalTPS / breakEvenTPS * 100) : 0;
                document.getElementById('utilization').textContent = utilization.toFixed(1) + '%';
            } else {
                document.getElementById('breakEvenTPS').textContent = '∞';
                document.getElementById('utilization').textContent = '0%';
            }

            // Scaling impact
            const scaling2x = profitPerDay * 2;
            document.getElementById('scaling2x').textContent = '$' + scaling2x.toFixed(2);
            
            const tps2x = profitPerMTokens * (totalTPS * 2) * 3600 * 24 / 1_000_000;
            document.getElementById('tps2x').textContent = '$' + tps2x.toFixed(2);
        }

        // Initialize calculation on page load
        document.addEventListener('DOMContentLoaded', calculateProfit);
    </script>
</body>
</html>''')

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
        # First get the existing GPU config
        gpu_configs = db.get_gpu_configs()
        existing_gpu = None
        for gpu in gpu_configs:
            if gpu.name == gpu_name:
                existing_gpu = gpu
                break
        
        if existing_gpu:
            # Mark as inactive instead of deleting
            existing_gpu.is_active = False
            success = db.update_gpu_config(existing_gpu)
            if success:
                return JSONResponse({"success": True, "message": f"GPU {gpu_name} deleted successfully"})
            else:
                return JSONResponse({"success": False, "message": f"Failed to delete GPU {gpu_name}"})
        else:
            return JSONResponse({"success": False, "message": f"GPU {gpu_name} not found"})
    except Exception as e:
        return JSONResponse({"success": False, "message": f"Error deleting GPU: {str(e)}"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 