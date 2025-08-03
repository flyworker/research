# OpenRouter & DeepSeek Model Throughput Calculator

This project provides a web-based calculator for estimating the throughput, concurrent user capacity, and business value of OpenRouter and DeepSeek models (free and paid) on an 8×H100 80GB GPU server. The calculator helps you understand both hardware and API-limited performance, pricing, and optimal vLLM deployment for different model variants and request sizes.

## Features
- Select from a comprehensive list of OpenRouter/DeepSeek free and paid models
- See model context window (max tokens per request) and pricing
- Input custom tokens per request (auto-clamped to model's max context window)
- Instantly see:
  - Hardware throughput (tokens/sec, concurrent users, daily capacity)
  - API-limited throughput (OpenRouter/DeepSeek free-tier limits)
  - Daily token capacity for free and paid API tiers
  - Estimated value generated per day (USD, 70% capacity, using output price)
  - vLLM deployment recommendations for 8×H100 80GB
- Clean, interactive web UI (FastAPI + Jinja2)
- User guidance and warnings for token limits and best practices

## Setup
1. **Install dependencies:**
   ```bash
   pip install fastapi uvicorn jinja2
   ```

2. **Run the app:**
   ```bash
   python llm_valuation.py
   ```
   (from the `sample_code/lllm_perfomance/` directory)

3. **Open your browser:**
   Go to [http://localhost:8000](http://localhost:8000)

## Usage
- Select a model from the dropdown.
- Enter the number of tokens per request (e.g., 512, 2048, 4096, etc.).
- The input is automatically clamped to the model's max context window.
- Click "Calculate" to see:
  - Model parameters, context window, and pricing
  - Cluster TPS (hardware), concurrent users, daily capacity
  - API-limited throughput and daily tokens
  - **Estimated value generated per day (USD, 70% capacity)**
  - vLLM launch recommendations for 8×H100 80GB
- Warnings and usage notes are shown for clarity.

## Business Value Calculation
- **Est. value generated per day (USD, 70% capacity):**
  - Formula: `0.7 × Daily capacity (M tokens) × Output $/M`
  - This estimates the daily revenue if you run the model at 70% of its hardware token capacity, using the model's output price per million tokens.
  - For free models or those without a price, this field is shown as "-".

## vLLM Recommendations
- The calculator provides a table of recommended vLLM parameters for 8×H100 80GB, including tensor parallelism, batch size, context window, and more.
- A sample launch command is provided for quick deployment.

## Customization
- To add more models, edit the `models` list in `llm_valuation.py`.
- To change hardware assumptions, adjust the constants at the top of `llm_valuation.py`.
- The HTML template is auto-generated in a `templates/` subdirectory on first run; you can customize it for advanced UI changes.

## Notes
- This calculator is for estimation only. Real-world throughput may vary based on batch size, prompt/response length, and backend implementation.
- API limits and prices are based on OpenRouter/DeepSeek as of June 2024.
- For most use cases, 512–4096 tokens per request is recommended.

## License
MIT 