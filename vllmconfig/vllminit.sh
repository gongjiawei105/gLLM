#!/bin/bash
#
# Start vLLM inference server (base model, no LoRA).
#
# All settings can be overridden via environment variables or src/.env.
# Start with conservative settings and increase after verifying stability.
#
# Usage:
#   ./vllminit.sh
#
# See HARDWARE_GUIDE.md for recommended settings per GPU.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load env vars
if [ -f "$SCRIPT_DIR/../src/.env" ]; then
    source "$SCRIPT_DIR/../src/.env"
fi

# --- Configurable via .env or environment ---
PORT="${VLLM_PORT:-8000}"
GPU_MEMORY_UTILIZATION="${VLLM_GPU_MEM:-0.85}"
MAX_MODEL_LEN="${VLLM_MAX_MODEL_LEN:-8192}"
DTYPE="${VLLM_DTYPE:-auto}"
LOG_FILE="$SCRIPT_DIR/vllm-logs/vllm.log"

mkdir -p "$SCRIPT_DIR/vllm-logs"

echo "========================================"
echo "  vLLM Inference Server"
echo "========================================"
echo "Model:        $MODEL"
echo "Port:         $PORT"
echo "Max context:  $MAX_MODEL_LEN tokens"
echo "GPU mem util: $GPU_MEMORY_UTILIZATION"
echo "Dtype:        $DTYPE"
echo ""
echo "Tip: If you get OOM errors, reduce VLLM_MAX_MODEL_LEN or VLLM_GPU_MEM in .env"
echo "========================================"
echo ""

sudo docker run --runtime nvidia --gpus all \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  --env "HUGGING_FACE_HUB_TOKEN=$HF_TOKEN" \
  -p $PORT:8000 \
  --ipc=host \
  vllm/vllm-openai:latest \
  --model $MODEL \
  --host 0.0.0.0 \
  --trust-remote-code \
  --served-model-name $MODEL \
  --swap-space 0 \
  --dtype $DTYPE \
  --gpu-memory-utilization $GPU_MEMORY_UTILIZATION \
  --max-model-len $MAX_MODEL_LEN \
  2>&1 | tee "$LOG_FILE"
