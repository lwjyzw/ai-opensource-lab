#!/usr/bin/env bash
# n8n 一键启动（Git Bash）— Node 与数据目录均在 D 盘
export PATH="/d/tools/node/node-v22.21.1-win-x64:/d/tools/npm-global:$PATH"
export N8N_USER_FOLDER="D:/projects/Zcode_project/n8n-data"
n8n start
