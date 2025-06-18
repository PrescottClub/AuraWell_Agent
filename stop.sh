#!/bin/bash
# AuraWell 便捷停止脚本
# 调用 scripts 目录中的完整停止脚本

exec ./scripts/stop_services.sh "$@"
