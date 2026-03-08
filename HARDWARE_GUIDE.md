# Hardware Tuning Guide

This guide helps you configure vLLM for different GPU hardware. **Always start with conservative settings** and increase after verifying stability.

## Quick Start: Which Settings Do I Need?

Check your GPU with `nvidia-smi`, then use the matching profile below.

## Recommended Profiles

### NVIDIA A6000 (48 GB) — School Server

This is the reference hardware. Can run the full 8B model with large context.

Add to `src/.env`:
```bash
MODEL=Qwen/Qwen3-VL-8B-Instruct
VLLM_MAX_MODEL_LEN=32768
VLLM_GPU_MEM=0.90
VLLM_MAX_LORAS=4
```

### NVIDIA A5500 (24 GB) — Development Machine

Half the VRAM of the A6000. Must reduce context length significantly.

**Start conservative** — add to `src/.env`:
```bash
MODEL=Qwen/Qwen3-VL-8B-Instruct
VLLM_MAX_MODEL_LEN=8192
VLLM_GPU_MEM=0.85
VLLM_MAX_LORAS=1
```

**If stable, try increasing:**
```bash
VLLM_MAX_MODEL_LEN=16384
VLLM_GPU_MEM=0.90
VLLM_MAX_LORAS=2
```

**If OOM persists, use a smaller model:**
```bash
MODEL=Qwen/Qwen2.5-3B-Instruct
VLLM_MAX_MODEL_LEN=16384
VLLM_GPU_MEM=0.90
VLLM_MAX_LORAS=2
```

### NVIDIA RTX 3090 / 4090 (24 GB)

Similar to A5500. Use the same conservative profile above.

### NVIDIA RTX 3080 / 4070 Ti (12-16 GB)

Very constrained. Must use a smaller model.

```bash
MODEL=Qwen/Qwen2.5-3B-Instruct
VLLM_MAX_MODEL_LEN=4096
VLLM_GPU_MEM=0.85
VLLM_MAX_LORAS=1
```

## All Configurable Variables

Set these in `src/.env` — the vLLM scripts read them automatically.

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL` | (required) | HuggingFace model name |
| `VLLM_MAX_MODEL_LEN` | `8192` | Max context window (tokens). Larger = more VRAM |
| `VLLM_GPU_MEM` | `0.85` | Fraction of GPU memory vLLM can use (0.0-1.0) |
| `VLLM_MAX_LORAS` | `2` | Max LoRA adapters loaded simultaneously |
| `VLLM_MAX_LORA_RANK` | `64` | Max LoRA rank supported |
| `VLLM_DTYPE` | `auto` | Model precision (`auto`, `float16`, `bfloat16`) |
| `VLLM_PORT` | `8000` | Port for the inference API |
| `HF_TOKEN` | (required) | HuggingFace access token |

## VRAM Usage Estimates (8B model, float16)

| Context Length | Model Weights | KV Cache (approx) | Total |
|---------------|--------------|-------------------|-------|
| 4096 | ~16 GB | ~2 GB | ~18 GB |
| 8192 | ~16 GB | ~4 GB | ~20 GB |
| 16384 | ~16 GB | ~8 GB | ~24 GB |
| 32768 | ~16 GB | ~12 GB | ~28 GB |

*KV cache varies by model architecture. These are rough estimates for planning.*

## Troubleshooting

### OOM (Out of Memory) on startup
1. Reduce `VLLM_MAX_MODEL_LEN` (biggest impact)
2. Reduce `VLLM_GPU_MEM` to 0.80
3. Check `nvidia-smi` — another process may be using VRAM
4. Switch to a smaller model (3B instead of 8B)

### OOM during inference (after startup)
- Long conversations exceed the KV cache. Reduce `VLLM_MAX_MODEL_LEN`
- Multiple concurrent users compound memory usage

### Slow generation
- `VLLM_GPU_MEM` too low — vLLM can't batch efficiently
- Try increasing to 0.90 or 0.95 if VRAM allows

### Model won't load
- Check `HF_TOKEN` is set and has access to the model
- Try `VLLM_DTYPE=float16` if `auto` fails
- Ensure Docker has GPU access: `docker run --gpus all nvidia/cuda:12.0-base nvidia-smi`

## Fine-Tuning VRAM Requirements

Fine-tuning uses Unsloth with QLoRA (4-bit), which is much more memory-efficient than inference:

| Model | QLoRA Training | Full Fine-Tune |
|-------|---------------|----------------|
| 3B | ~6 GB | ~24 GB |
| 7-8B | ~10 GB | ~48 GB |

Both the A6000 and A5500 can fine-tune the 7B model with QLoRA. Adjust `finetune/config.yaml`:
- Reduce `batch_size` to 1 if OOM during training
- Reduce `max_seq_length` from 2048 to 1024
