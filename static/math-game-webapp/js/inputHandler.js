// 入力ハンドラークラス
class InputHandler {
    constructor(onInputCallback) {
        this.onInputCallback = onInputCallback;
        this.isInputEnabled = true;
        this.softKeyboardButtons = [];
    }

    // ソフトキーボードのセットアップ
    setupSoftKeyboard() {
        // すべてのキーボタンを取得
        this.softKeyboardButtons = document.querySelectorAll('.key');
        
        // 各ボタンにクリックイベントを追加
        this.softKeyboardButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                if (!this.isInputEnabled) return;
                
                const digit = e.target.getAttribute('data-digit');
                this.processInput(digit);
            });
        });
    }

    // 物理キーボードのセットアップ
    setupPhysicalKeyboard() {
        document.addEventListener('keydown', (e) => {
            if (!this.isInputEnabled) return;
            
            // 数字キー（0-9）のみ受け付け
            if (e.key >= '0' && e.key <= '9') {
                e.preventDefault(); // デフォルトの動作を防止
                this.processInput(e.key);
            }
            
            // テンキーの数字も受け付け
            if (e.code.startsWith('Numpad') && e.key >= '0' && e.key <= '9') {
                e.preventDefault();
                this.processInput(e.key);
            }
        });
    }

    // 入力処理
    processInput(digit) {
        if (!this.validateInput(digit)) return;
        
        // 視覚的フィードバック
        this.provideVisualFeedback(digit);
        
        // コールバック実行
        if (this.onInputCallback) {
            this.onInputCallback(digit);
        }
    }

    // 入力検証
    validateInput(input) {
        // 数字（0-9）のみ許可
        return input >= '0' && input <= '9';
    }

    // 視覚的フィードバック
    provideVisualFeedback(digit) {
        // ソフトキーボードのボタンを一時的にハイライト
        const button = document.querySelector(`.key[data-digit="${digit}"]`);
        if (button) {
            button.classList.add('active');
            setTimeout(() => {
                button.classList.remove('active');
            }, 200);
        }
    }

    // 入力の有効/無効切り替え
    enableInput() {
        this.isInputEnabled = true;
        this.updateKeyboardState();
    }

    disableInput() {
        this.isInputEnabled = false;
        this.updateKeyboardState();
    }

    // キーボードの状態更新
    updateKeyboardState() {
        this.softKeyboardButtons.forEach(button => {
            if (this.isInputEnabled) {
                button.removeAttribute('disabled');
                button.style.opacity = '1';
                button.style.cursor = 'pointer';
            } else {
                button.setAttribute('disabled', 'true');
                button.style.opacity = '0.5';
                button.style.cursor = 'not-allowed';
            }
        });
    }

    // 初期化
    init() {
        this.setupSoftKeyboard();
        this.setupPhysicalKeyboard();
    }

    // クリーンアップ
    destroy() {
        // イベントリスナーの削除が必要な場合はここで行う
        this.softKeyboardButtons = [];
    }
}

// CSSに追加するアクティブスタイル
const style = document.createElement('style');
style.textContent = `
    .key.active {
        background-color: #3498db !important;
        color: white !important;
        transform: scale(0.95);
    }
`;
document.head.appendChild(style);