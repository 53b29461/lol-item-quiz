# League of Legends Item Quiz - CLAUDE.md

このファイルは、lol-item-quizプロジェクトでClaude Codeが作業する際の専用指示書です。

## 🎮 プロジェクト概要

- **URL**: https://lol-item-quiz.com
- **目的**: League of Legendsのアイテムクイズ学習アプリケーション
- **技術スタック**: Flask, Python, HTML/CSS/JavaScript
- **場所**: `/home/user/.pg/development-projects/lol-item-quiz`

## 🚀 重要な運用ルール

### 自動デプロイの実行
**ファイル変更後は必ず自動的にデプロイまで実行すること**

1. ファイル編集
2. Gitコミット
3. GitHubプッシュ
4. Flaskアプリ再起動

### デプロイコマンド
```bash
# 1. 変更をコミット
git add . && git commit -m "変更内容の説明"

# 2. GitHubにプッシュ
git push origin master

# 3. アプリケーション再起動
pkill -f "python.*app.py"
source venv/bin/activate && nohup python app.py > /dev/null 2>&1 &
```

## 📁 プロジェクト構造

```
lol-item-quiz/
├── app.py                  # メインアプリケーション
├── venv/                   # Python仮想環境
├── templates/              # HTMLテンプレート
│   ├── index.html         # トップページ
│   ├── quiz_a.html        # クイズA
│   ├── quiz_b.html        # クイズB
│   ├── etc.html           # その他ページ
│   └── math_game.html     # 数学ゲーム
├── static/                 # 静的ファイル
│   ├── styles.css         # スタイルシート
│   ├── items/             # アイテム画像
│   └── math-game-webapp/  # 数学ゲームアセット
├── flask_session/          # セッションファイル
└── CLAUDE.md              # この指示書

## 🌐 本番環境情報

- **Nginx設定**: `/etc/nginx/sites-enabled/lol-item-quiz.com`
- **SSL証明書**: Let's Encrypt (自動更新設定済み)
- **ポート**: 5000 (Flask) → 80/443 (Nginx)
- **プロセス管理**: 手動起動（systemd未設定）

## 🔧 開発時の注意事項

1. **ブランディング**: "LoLAnki"という旧名称は使用しない
2. **著作権表記**: "© 2024 LoL Item Quiz. All rights reserved."
3. **言語**: 日本語でのUI/UX
4. **デバッグ**: 本番環境ではdebug=Falseにすること（現在はTrue）

## 📋 よく使うコマンド

```bash
# 開発環境で起動
cd /home/user/.pg/development-projects/lol-item-quiz
source venv/bin/activate
python app.py

# ログ確認
tail -f /var/log/nginx/lol-item-quiz.error.log
tail -f /var/log/nginx/lol-item-quiz.access.log

# プロセス確認
ps aux | grep app.py

# 依存関係インストール
source venv/bin/activate
pip install -r requirements.txt
```

## 🚨 トラブルシューティング

### 502 Bad Gateway エラー
1. Flaskアプリが起動していない
2. 上記のデプロイコマンドでアプリを再起動

### ポート5000が使用中
```bash
lsof -ti:5000 | xargs kill -9
```

## 📝 変更履歴

- 2024-07-17: プロジェクト専用CLAUDE.md作成
- 2024-07-17: 自動デプロイルール追加
- 2024-07-17: フッター文言をLoL Item Quizに変更