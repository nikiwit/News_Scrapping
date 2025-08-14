#!/bin/bash
# Ollama MPS Optimization Script for macOS M2
# Source this file before running summarization: source optimize_ollama.sh

echo "🚀 Setting up Ollama MPS optimizations for macOS M2..."

# Core MPS optimizations
export OLLAMA_GPU_LAYERS=-1
export OLLAMA_KEEP_ALIVE=10m
export PYTORCH_ENABLE_MPS_FALLBACK=1
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0

# Advanced optimizations (2025)
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_KV_CACHE_TYPE=q8_0
export OLLAMA_NUM_PARALLEL=2
export OLLAMA_MAX_LOADED_MODELS=1

# Performance monitoring
export OLLAMA_DEBUG=0  # Set to 1 for debug info

echo "✅ Ollama optimizations configured!"
echo "   GPU Layers: All (-1)"
echo "   Keep Alive: 10 minutes"
echo "   Flash Attention: Enabled"
echo "   KV Cache: 8-bit quantization"
echo "   Parallel Requests: 2"
echo ""
echo "🦙 Ready for high-performance LLM summarization!"
