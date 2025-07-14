# Installing DeepSeek V3 0324 on 8×H100 80GB

This guide explains how to deploy DeepSeek V3 0324 (685B MoE) on a server with 8×H100 80GB GPUs using vLLM for high-throughput inference.

## Prerequisites
- Ubuntu 20.04+ (or similar Linux)
- 8×NVIDIA H100 80GB GPUs (NVLink recommended)
- CUDA 12.1+ and cuDNN installed
- Python 3.10+
- At least 1TB free NVMe SSD for model weights
- Internet access for model download
- (Optional) Docker for containerized deployment

## 1. System Preparation
Update drivers and install dependencies:
```bash
sudo apt update && sudo apt upgrade -y
# Install NVIDIA driver (if not already installed)
sudo apt install -y nvidia-driver-535
# Install CUDA toolkit (if not already installed)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/3bf863cc.pub
sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /"
sudo apt update
sudo apt install -y cuda-toolkit-12-1
# Reboot if you updated drivers or CUDA
```

## 2. Create Python Environment
```bash
python3 -m venv vllm_env
source vllm_env/bin/activate
pip install --upgrade pip
```

## 3. Install vLLM (latest, with CUDA 12+ support)
```bash
pip install "vllm[triton]"  # or build from source for latest features
```

## 4. Download DeepSeek V3 0324 Model Weights
- Visit: https://huggingface.co/deepseek-ai/deepseek-chat-v3-0324
- Accept the license and use `git lfs` to download:

```bash
pip install git-lfs
export HF_HOME=/data/huggingface  # (optional, for large storage)
git lfs install
git clone https://huggingface.co/deepseek-ai/deepseek-chat-v3-0324
```

## 5. Launch vLLM Inference Server
**Do NOT use `--enable-fp8`, `--enable-moe`, or `--enable-mla` flags. These are NOT valid vLLM CLI arguments.**

vLLM will automatically enable FP8, MoE, and MLA features for DeepSeek V3 0324 (671B) on H100 GPUs if you use a recent version (≥0.3.2.dev0) and the correct model.

Recommended parameters for 8×H100 80GB:

```bash
python -m vllm.entrypoints.openai.api_server \
  --model /path/to/deepseek-chat-v3-0324 \
  --tensor-parallel-size 8 \
  --max-num-seqs 64 \
  --max-num-batched-tokens 16384 \
  --max-model-len 128000 \
  --dtype auto \
  --gpu-memory-utilization 0.90 \
  --enable-flash-attn
```
- `--dtype auto` lets vLLM select the best precision (FP8 on H100).
- Do **not** add `--enable-fp8`, `--enable-moe`, or `--enable-mla` (they will cause an error).
- Adjust `--max-model-len` and `--max-num-batched-tokens` for your workload.
- For best performance, use `float16`, `bfloat16`, or `auto` if supported.

## 6. Confirm FP8, MoE, and MLA Are Enabled
On server startup, check the logs for lines like:

```
[INFO] Using FP8 inference kernels on NVIDIA H100
[INFO] Mixture of Experts (MoE) enabled: ...
[INFO] Multi-head Latent Attention (MLA) kernel initialized
```
If you do **not** see these, upgrade vLLM to the latest version:
```bash
pip install --upgrade --pre vllm
```

## 7. Test the API
```bash
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-chat-v3-0324", "prompt": "Hello, world!", "max_tokens": 128}'
```

## 8. Troubleshooting
- **error: unrecognized arguments: --enable-fp8 --enable-moe --enable-mla**
  - Remove these flags; vLLM does not support them as CLI arguments.
- **FP8, MoE, or MLA not enabled:**
  - Ensure you are using H100 GPUs, the correct model, and the latest vLLM.
  - Check logs for confirmation lines (see above).
- **Out of memory:** Lower `--max-num-seqs` or `--max-num-batched-tokens`.
- **Slow throughput:** Ensure NVLink is enabled, use latest vLLM, and check GPU utilization.
- **Model not found:** Verify model path and permissions.
- **API errors:** Check vLLM logs for stack traces.

## References
- [DeepSeek V3 0324 on HuggingFace](https://huggingface.co/deepseek-ai/deepseek-chat-v3-0324)
- [vLLM Documentation](https://vllm.readthedocs.io/en/latest/)
- [NVIDIA H100 Specs](https://www.nvidia.com/en-us/data-center/h100/)

---
For advanced tuning, see the vLLM docs and DeepSeek model card for more options. 