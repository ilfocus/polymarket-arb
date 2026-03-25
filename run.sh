#!/usr/bin/env bash
#
# Polymarket BTC 15分钟套利机器人 - 启动脚本
#
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
ENV_FILE="$PROJECT_DIR/.env"

# ---------- 检查 .env 文件 ----------
if [ ! -f "$ENV_FILE" ]; then
    echo "[ERROR] 未找到 .env 文件"
    echo "请先复制模板并填写配置："
    echo "  cp .env.example .env"
    exit 1
fi

# 检查必填字段
if ! grep -q 'POLYMARKET_PRIVATE_KEY=.\+' "$ENV_FILE"; then
    echo "[ERROR] .env 中未配置 POLYMARKET_PRIVATE_KEY"
    echo "请编辑 .env 文件填写钱包私钥"
    exit 1
fi

# ---------- 检查 / 创建虚拟环境 ----------
if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] 虚拟环境不存在，正在创建..."
    python3 -m venv "$VENV_DIR"
    echo "[INFO] 虚拟环境创建完成"
fi

# 激活虚拟环境
source "$VENV_DIR/bin/activate"

# ---------- 安装依赖 ----------
echo "[INFO] 检查依赖..."
pip install -q -r "$PROJECT_DIR/requirements.txt"

# ---------- 显示配置摘要 ----------
echo ""
echo "======================================"
echo " Polymarket 套利机器人"
echo "======================================"

# 从 .env 读取关键配置（不暴露敏感信息）
DRY_RUN=$(grep -E '^DRY_RUN=' "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 || echo "false")
ORDER_SIZE=$(grep -E '^ORDER_SIZE=' "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 || echo "50")
TARGET_PAIR_COST=$(grep -E '^TARGET_PAIR_COST=' "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 || echo "0.99")
MAX_TRADES=$(grep -E '^MAX_TRADES_PER_MARKET=' "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 || echo "0")

if [ "$DRY_RUN" = "true" ]; then
    echo " 模式:       模拟（不实际下单）"
else
    echo " 模式:       真实交易"
fi
echo " 订单数量:   $ORDER_SIZE 股/边"
echo " 成本阈值:   \$$TARGET_PAIR_COST"
if [ "$MAX_TRADES" = "0" ]; then
    echo " 交易限制:   无限制"
else
    echo " 交易限制:   $MAX_TRADES 次/场"
fi
echo "======================================"
echo ""

# ---------- 启动机器人 ----------
echo "[INFO] 启动机器人..."
cd "$PROJECT_DIR"
python -m src.strategy_bot
