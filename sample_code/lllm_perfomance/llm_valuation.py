from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

# Hardware constants
GPU_COUNT = 8
TOKENS_PER_GPU_TPS = 700            # approximate output tokens per second per H100 in FP8
TOKENS_PER_USER_STREAM = 15         # perceived "real‑time" stream speed (tokens/sec)

# OpenRouter/DeepSeek API limits
REQUESTS_PER_MIN = 20
FREE_CALLS_PER_DAY = 50
PAID_CALLS_PER_DAY = 1000

# OpenRouter free and paid models reference
models = [
    # Free models
    {"Model": "DeepSeek V3 0324 (free)", "Slug": "deepseek/deepseek-v3-0324:free", "Parameters (B)": 236, "Context window": "128K", "Precision": "fp8", "Typical GPU": "H100", "Input $/M": "-", "Output $/M": "-", "Tokens per GPU TPS": 1200},
    {"Model": "DeepSeek R1 0528 (free)", "Slug": "deepseek/deepseek-r1-0528:free", "Parameters (B)": 236, "Context window": "164K", "Precision": "fp8", "Typical GPU": "H100", "Input $/M": "-", "Output $/M": "-", "Tokens per GPU TPS": 1200},
    {"Model": "DeepSeek R1 (original free)", "Slug": "deepseek/deepseek-r1:free", "Parameters (B)": 236, "Context window": "164K", "Precision": "fp8", "Typical GPU": "H100", "Input $/M": "-", "Output $/M": "-", "Tokens per GPU TPS": 1200},
    # Paid models
    {"Model": "DeepSeek Chat (V3 base)", "Slug": "deepseek/deepseek-chat", "Parameters (B)": "685B MoE (37B active)", "Context window": "163K", "Precision": "MoE", "Typical GPU": "H100", "Input $/M": "$0.38", "Output $/M": "$0.89", "Tokens per GPU TPS": 1200},
    {"Model": "DeepSeek Chat V3 0324", "Slug": "deepseek/deepseek-chat-v3-0324", "Parameters (B)": "685B MoE", "Context window": "163K", "Precision": "MoE", "Typical GPU": "H100", "Input $/M": "$0.28", "Output $/M": "$0.88", "Tokens per GPU TPS": 1200},
    {"Model": "DeepSeek R1", "Slug": "deepseek/deepseek-r1", "Parameters (B)": "671B dense (37B active)", "Context window": "128K", "Precision": "dense", "Typical GPU": "H100", "Input $/M": "$0.45", "Output $/M": "$2.15", "Tokens per GPU TPS": 1200},
    {"Model": "DeepSeek R1 0528", "Slug": "deepseek/deepseek-r1-0528", "Parameters (B)": "671B dense (May-28 patch)", "Context window": "164K", "Precision": "dense", "Typical GPU": "H100", "Input $/M": "$0.55", "Output $/M": "$2.19", "Tokens per GPU TPS": 1200},
    {"Model": "DeepSeek R1 Distill Qwen 7B", "Slug": "deepseek/r1-distill-qwen-7b", "Parameters (B)": "7B dense", "Context window": "131K", "Precision": "dense", "Typical GPU": "H100", "Input $/M": "$0.10", "Output $/M": "$0.20", "Tokens per GPU TPS": 1200},
    {"Model": "DeepSeek R1 0528 Qwen3 8B", "Slug": "deepseek/deepseek-r1-0528-qwen3-8b", "Parameters (B)": "8B dense", "Context window": "131K", "Precision": "dense", "Typical GPU": "H100", "Input $/M": "$0.01", "Output $/M": "$0.02", "Tokens per GPU TPS": 1200},
    {"Model": "DeepSeek R1 Distill Llama 8B", "Slug": "deepseek/r1-distill-llama-8b", "Parameters (B)": "8B dense", "Context window": "-", "Precision": "dense", "Typical GPU": "H100", "Input $/M": "$0.04", "Output $/M": "$0.04", "Tokens per GPU TPS": 1200},
    {"Model": "DeepSeek R1 Distill Qwen 32B", "Slug": "deepseek/r1-distill-qwen-32b", "Parameters (B)": "32B dense", "Context window": "128K", "Precision": "dense", "Typical GPU": "H100", "Input $/M": "$0.075", "Output $/M": "$0.15", "Tokens per GPU TPS": 1200},
    {"Model": "DeepSeek R1 Distill Qwen 14B", "Slug": "deepseek/r1-distill-qwen-14b", "Parameters (B)": "14B dense", "Context window": "131K", "Precision": "dense", "Typical GPU": "H100", "Input $/M": "$0.15", "Output $/M": "$0.15", "Tokens per GPU TPS": 1200},
    {"Model": "DeepSeek Prover V2", "Slug": "deepseek/deepseek-prover-v2", "Parameters (B)": "671B math/logic", "Context window": "164K", "Precision": "dense", "Typical GPU": "H100", "Input $/M": "$0.50", "Output $/M": "$2.18", "Tokens per GPU TPS": 1200},
    # Other free models (for completeness, no price)
    {"Model": "OpenChat 3.5 0106 (free)", "Slug": "openchat/openchat-3.5-0106:free", "Parameters (B)": 7, "Context window": "32K", "Precision": "fp16", "Typical GPU": "A100/H100", "Input $/M": "-", "Output $/M": "-", "Tokens per GPU TPS": 1200},
    {"Model": "Llama 3 8B Instruct (free)", "Slug": "meta-llama/llama-3-8b-instruct:free", "Parameters (B)": 8, "Context window": "8K", "Precision": "fp16", "Typical GPU": "A100/H100", "Input $/M": "-", "Output $/M": "-", "Tokens per GPU TPS": 1200},
    {"Model": "Llama 3 70B Instruct (free)", "Slug": "meta-llama/llama-3-70b-instruct:free", "Parameters (B)": 70, "Context window": "8K", "Precision": "fp16", "Typical GPU": "H100", "Input $/M": "-", "Output $/M": "-", "Tokens per GPU TPS": 1200},
    {"Model": "Mistral 7B Instruct (free)", "Slug": "mistralai/mistral-7b-instruct:free", "Parameters (B)": 7, "Context window": "32K", "Precision": "fp16", "Typical GPU": "A100/H100", "Input $/M": "-", "Output $/M": "-", "Tokens per GPU TPS": 1200},
    {"Model": "Mixtral 8x7B Instruct (free)", "Slug": "mistralai/mixtral-8x7b-instruct:free", "Parameters (B)": 46, "Context window": "32K", "Precision": "fp16", "Typical GPU": "H100", "Input $/M": "-", "Output $/M": "-", "Tokens per GPU TPS": 1200},
    {"Model": "DeepSeek Chat 67B (free)", "Slug": "deepseek/deepseek-chat:free", "Parameters (B)": 67, "Context window": "32K", "Precision": "fp16", "Typical GPU": "H100", "Input $/M": "-", "Output $/M": "-", "Tokens per GPU TPS": 1200},
    {"Model": "DeepSeek Coder 33B (free)", "Slug": "deepseek/deepseek-coder:free", "Parameters (B)": 33, "Context window": "16K", "Precision": "fp16", "Typical GPU": "H100", "Input $/M": "-", "Output $/M": "-", "Tokens per GPU TPS": 1200},
    {"Model": "Gemma 7B IT (free)", "Slug": "google/gemma-7b-it:free", "Parameters (B)": 7, "Context window": "8K", "Precision": "fp16", "Typical GPU": "A100/H100", "Input $/M": "-", "Output $/M": "-", "Tokens per GPU TPS": 1200},
    {"Model": "Gemma 2B IT (free)", "Slug": "google/gemma-2b-it:free", "Parameters (B)": 2, "Context window": "8K", "Precision": "fp16", "Typical GPU": "A100/H100", "Input $/M": "-", "Output $/M": "-", "Tokens per GPU TPS": 1200},
    {"Model": "Claude 3 Haiku (free)", "Slug": "anthropic/claude-3-haiku:free", "Parameters (B)": "?", "Context window": "200K", "Precision": "?", "Typical GPU": "H100", "Input $/M": "-", "Output $/M": "-", "Tokens per GPU TPS": 1200},
    {"Model": "Claude 3 Sonnet (free)", "Slug": "anthropic/claude-3-sonnet:free", "Parameters (B)": "?", "Context window": "200K", "Precision": "?", "Typical GPU": "H100", "Input $/M": "-", "Output $/M": "-", "Tokens per GPU TPS": 1200},
    {"Model": "Gemini Pro (free)", "Slug": "google/gemini-pro:free", "Parameters (B)": "?", "Context window": "32K", "Precision": "?", "Typical GPU": "H100", "Input $/M": "-", "Output $/M": "-", "Tokens per GPU TPS": 1200},
    {"Model": "DeepSeek‑V3‑0324‑AWQ (MoE 671B, self-hosted)", "Slug": "deepseek/deepseek-v3-0324-awq", "Parameters (B)": "671B MoE (AWQ)", "Context window": "128K", "Precision": "AWQ MoE", "Typical GPU": "H100", "Input $/M": "-", "Output $/M": "-", "Tokens per GPU TPS": 700},
]

# vLLM recommended parameters for 8xH100 80GB
VLLM_PARAMS = [
    ("--tensor-parallel-size", "8", "One per GPU"),
    ("--max-num-seqs", "128 (64 for 685B)", "Increase for smaller models"),
    ("--max-num-batched-tokens", "32768 (16384 for 685B)", "Lower for long context or big models"),
    ("--max-model-len", "128000–164000", "Match model context window"),
    ("--dtype", "float16 or auto", "Use bf16 if supported"),
    ("--gpu-memory-utilization", "0.90", "Up to 90% VRAM"),
    ("--enable-flash-attn", "(set)", "If supported"),
    ("--disable-paged-kv-cache", "(optional)", "For max speed, if enough VRAM"),
]
VLLM_COMMAND = (
    "python -m vllm.entrypoints.openai.api_server "
    "--model <your-model> "
    "--tensor-parallel-size 8 "
    "--max-num-seqs 128 "
    "--max-num-batched-tokens 32768 "
    "--max-model-len 163840 "
    "--dtype float16 "
    "--gpu-memory-utilization 0.90 "
    "--enable-flash-attn"
)

# Setup FastAPI and templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(templates_dir, exist_ok=True)
app = FastAPI()
app.mount("/static", StaticFiles(directory=os.path.join(templates_dir, "static")), name="static")
templates = Jinja2Templates(directory=templates_dir)

template_path = os.path.join(templates_dir, "calculator.html")
with open(template_path, "w") as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>OpenRouter Model Throughput Calculator</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2em; }
        .container { max-width: 700px; margin: auto; }
        label, select, input { display: block; margin: 1em 0 0.5em 0; }
        table { border-collapse: collapse; width: 100%; margin-top: 2em; }
        th, td { border: 1px solid #ccc; padding: 0.5em; text-align: left; }
        th { background: #f0f0f0; }
        .suggestion { background: #e6f7ff; border: 1px solid #91d5ff; padding: 1em; margin-top: 1em; font-size: 1.1em; }
        .section-title { margin-top: 2em; font-size: 1.2em; font-weight: bold; }
        .vllm-table th, .vllm-table td { font-size: 0.95em; }
        .vllm-code { background: #f7f7f7; border: 1px solid #ccc; padding: 1em; font-family: monospace; margin-top: 1em; }
        .warning { color: #b00; font-size: 1em; margin-top: 1em; }
        .token-note { color: #555; font-size: 0.95em; margin-bottom: 1em; }
        .value-note { color: #555; font-size: 0.95em; margin-top: 0.5em; }
    </style>
</head>
<body>
<div class="container">
    <h1>OpenRouter Model Throughput Calculator</h1>
    <form method="post">
        <label for="model">Model:</label>
        <select name="model" id="model">
            {% for m in models %}
            <option value="{{ m['Model'] }}" {% if m['Model'] == selected_model %}selected{% endif %}>{{ m['Model'] }}</option>
            {% endfor %}
        </select>
        <label for="tokens_per_request">Tokens per request:</label>
        <input type="number" name="tokens_per_request" id="tokens_per_request" value="{{ tokens_per_request }}" min="1" max="32768" required>
        <button type="submit">Calculate</button>
    </form>
    {% if warning %}<div class="warning">{{ warning }}</div>{% endif %}
    <div class="token-note">{{ token_note }}</div>
    {% if model_params %}
    <div class="section-title">OpenRouter Model Parameters</div>
    <table>
        {% for k, v in model_params.items() %}
        <tr><th>{{ k }}</th><td>{{ v }}</td></tr>
        {% endfor %}
    </table>
    <div class="section-title">Self-Hosted 8×H100 80GB Throughput</div>
    <table>
        {% for k, v in throughput.items() %}
        <tr><th>{{ k }}</th><td>{{ v }}</td></tr>
        {% endfor %}
    </table>
    <div class="value-note">Est. value per day = 70% × Daily capacity (M tokens) × Output $/M</div>
    {% if suggestion %}
    <div class="suggestion">{{ suggestion|safe }}</div>
    {% endif %}
    <div class="section-title">Recommended vLLM Parameters for 8×H100 80GB</div>
    <table class="vllm-table">
        <thead><tr><th>Parameter</th><th>Recommended Value</th><th>Notes</th></tr></thead>
        <tbody>
        {% for param, value, note in vllm_params %}
        <tr><td>{{ param }}</td><td>{{ value }}</td><td>{{ note }}</td></tr>
        {% endfor %}
        </tbody>
    </table>
    <div class="vllm-code">
        <b>Sample vLLM launch command:</b><br/>
        <code>{{ vllm_command }}</code>
    </div>
    {% endif %}
</div>
</body>
</html>
''')

def get_model_info(model_name: str):
    for m in models:
        if m["Model"] == model_name:
            return m
    # Default to DeepSeek‑V3‑0324‑AWQ (MoE 671B, self-hosted) if not found
    for m in models:
        if "AWQ" in m["Model"]:
            return m
    return models[0]

@app.get("/", response_class=HTMLResponse)
async def calculator_form(request: Request):
    # Reasonable default for tokens per request
    default_tokens = 2048
    return templates.TemplateResponse("calculator.html", {
        "request": request,
        "models": models,
        "selected_model": models[0]["Model"],
        "tokens_per_request": default_tokens,
        "model_params": None,
        "throughput": None,
        "suggestion": None,
        "vllm_params": VLLM_PARAMS,
        "vllm_command": VLLM_COMMAND,
        "warning": None,
        "token_note": "For most use cases, 512–4096 tokens per request is recommended. The maximum allowed is determined by the model's context window."
    })

@app.post("/", response_class=HTMLResponse)
async def calculator_submit(request: Request, model: str = Form(...), tokens_per_request: int = Form(...)):
    m = get_model_info(model)
    awq_model = get_model_info("DeepSeek‑V3‑0324‑AWQ (MoE 671B, self-hosted)")
    tokens_per_gpu_tps = awq_model.get("Tokens per GPU TPS", 700)
    cluster_tps = tokens_per_gpu_tps * GPU_COUNT
    max_concurrent_users = int(cluster_tps / TOKENS_PER_USER_STREAM)
    daily_capacity_mtokens = round(cluster_tps * 86400 / 1_000_000, 1)
    # Parse context window as integer (e.g., '128K' -> 128000)
    context_window = awq_model["Context window"]
    if isinstance(context_window, int):
        max_tokens = context_window
        context_window_k = f"{int(context_window/1000)}K"
    else:
        if isinstance(context_window, str) and context_window.endswith("K"):
            try:
                max_tokens = int(float(context_window[:-1]) * 1000)
            except Exception:
                max_tokens = 32768
            context_window_k = context_window
        else:
            max_tokens = 32768
            context_window_k = str(context_window)
    warning = None
    tpr = tokens_per_request
    if tpr > max_tokens:
        tpr = max_tokens
        warning = f"Tokens per request was limited to the model's maximum context window: {context_window_k} tokens."
    # Calculate estimated value generated per day at 70% capacity (if price info available)
    # Prefer the selected model's output price, fallback to self-hosted if not available
    output_price_str = m.get("Output $/M", "-")
    if not (output_price_str and output_price_str.startswith("$")):
        output_price_str = awq_model.get("Output $/M", "-")
    try:
        if output_price_str and output_price_str.startswith("$"):
            output_price = float(output_price_str[1:])
            value_per_day = round(daily_capacity_mtokens * 0.7 * output_price, 2)
            value_per_day_str = f"${value_per_day:,}"
        else:
            value_per_day_str = "-"
    except Exception:
        value_per_day_str = "-"
    throughput = {
        "Cluster TPS (hardware)": cluster_tps,
        "Concurrent users (hardware)": max_concurrent_users,
        "Daily capacity (M tokens, hardware)": daily_capacity_mtokens,
        "Max tokens per request (K)": m["Context window"],
        "Est. value generated per day (USD, 70% capacity)": value_per_day_str,
    }
    suggestion = f"With DeepSeek‑V3‑0324‑AWQ (MoE 671B) on 8×H100 80GB, you can support approximately <b>{max_concurrent_users} concurrent users</b> (hardware bound) at {TOKENS_PER_USER_STREAM} tokens/sec per user."
    model_params = {
        "Model": m["Model"],
        "Slug": m["Slug"],
        "Parameters (B)": m["Parameters (B)"],
        "Max tokens per request (K)": m["Context window"],
        "Precision": m["Precision"],
        "Typical GPU": m["Typical GPU"],
        "Input $/M": m["Input $/M"],
        "Output $/M": m["Output $/M"],
    }
    return templates.TemplateResponse("calculator.html", {
        "request": request,
        "models": models,
        "selected_model": model,
        "tokens_per_request": tpr,
        "model_params": model_params,
        "throughput": throughput,
        "suggestion": suggestion,
        "vllm_params": VLLM_PARAMS,
        "vllm_command": VLLM_COMMAND,
        "warning": warning,
        "token_note": "For most use cases, 512–4096 tokens per request is recommended. The maximum allowed is determined by the model's context window."
    })

if __name__ == "__main__":
    uvicorn.run("llm_valuation:app", host="0.0.0.0", port=8000, reload=True)
