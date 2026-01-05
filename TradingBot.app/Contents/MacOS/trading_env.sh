#!/bin/bash
#
# TradingBot环境配置
#

# 项目根目录
export PROJECT_ROOT="$(cd "$(dirname "${0}")/../../../.." && pwd)"

# Python路径
export PYTHON="${PROJECT_ROOT}/.venv/bin/python"

# 交易日志目录
export TRADING_LOG_DIR="${PROJECT_ROOT}/logs"
mkdir -p "${TRADING_LOG_DIR}"

# 配置文件目录
export CONFIG_DIR="${PROJECT_ROOT}/config"
