#!/bin/bash

# LoL Item Quiz 監視・自動再起動スクリプト
PROJECT_DIR="/home/user/.pg/development-projects/lol-item-quiz"
LOGFILE="$PROJECT_DIR/monitor.log"

cd $PROJECT_DIR

while true; do
    # プロセスが動いているかチェック
    if ! pgrep -f "python app.py" > /dev/null; then
        echo "$(date): LoL Item Quiz process not found, restarting..." >> $LOGFILE
        ./start_service.sh >> $LOGFILE 2>&1
    fi
    
    # サイトにアクセスできるかチェック
    if ! curl -s --max-time 5 http://localhost:5000 > /dev/null; then
        echo "$(date): LoL Item Quiz not responding, restarting..." >> $LOGFILE
        pkill -f "python app.py"
        sleep 3
        ./start_service.sh >> $LOGFILE 2>&1
    fi
    
    # 30秒待機
    sleep 30
done