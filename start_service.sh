#!/bin/bash

# LoL Item Quiz 常時起動スクリプト
cd /home/user/.pg/development-projects/lol-item-quiz

# 既存のプロセスがあれば停止
pkill -f "python app.py"

# 少し待つ
sleep 2

# 仮想環境をアクティベートしてアプリを起動
source venv/bin/activate
nohup python app.py > app.log 2>&1 &

echo "LoL Item Quiz started in background"
echo "PID: $(pgrep -f 'python app.py')"