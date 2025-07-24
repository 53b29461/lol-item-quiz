// メインアプリケーション
class MathGameApp {
    constructor() {
        this.gameEngine = new GameEngine();
        this.timer = new Timer();
        this.uiController = new UIController();
        this.inputHandler = null;
        this.lastDifficulty = 'normal'; // 前回の難易度を保存
        
        this.init();
    }

    // 初期化
    init() {
        // タイマーの表示要素を設定
        this.timer.setDisplayElement(document.getElementById('timer'));
        
        // 入力ハンドラーの初期化
        this.inputHandler = new InputHandler((digit) => {
            this.handleUserInput(digit);
        });
        this.inputHandler.init();
        
        // イベントリスナーの設定
        this.setupEventListeners();
        
        // 開始画面を表示
        this.uiController.showScreen('start');
    }

    // イベントリスナーの設定
    setupEventListeners() {
        // 難易度選択ボタン
        const startButton = document.getElementById('startButton');
        startButton.addEventListener('click', () => {
            this.uiController.showScreen('difficulty');
        });
        
        // ノーマルモードボタン
        const normalButton = document.getElementById('normalButton');
        normalButton.addEventListener('click', () => {
            this.startGame('normal');
        });
        
        // ハードモードボタン
        const hardButton = document.getElementById('hardButton');
        hardButton.addEventListener('click', () => {
            this.startGame('hard');
        });
        
        // 戻るボタン
        const backButton = document.getElementById('backButton');
        backButton.addEventListener('click', () => {
            this.uiController.showScreen('start');
        });
        
        // もう一度プレイボタン
        const playAgainButton = document.getElementById('playAgainButton');
        playAgainButton.addEventListener('click', () => {
            this.resetGame();
        });
        
        // キーボードイベント（結果画面でEnterキー対応）
        document.addEventListener('keydown', (event) => {
            // 結果画面が表示中かつEnterキーが押された場合
            const resultScreen = document.getElementById('resultScreen');
            if (resultScreen.style.display !== 'none' && event.key === 'Enter') {
                event.preventDefault();
                this.resetGame();
            }
        });
    }

    // ゲーム開始
    startGame(difficulty = 'normal') {
        // 難易度を保存
        this.lastDifficulty = difficulty;
        
        // UIリセット
        this.uiController.resetUI();
        
        // ゲーム画面に切り替え
        this.uiController.showScreen('game');
        
        // ゲームエンジン開始
        this.gameEngine.startGame(difficulty);
        
        // タイマー開始
        this.timer.reset();
        this.timer.start();
        
        // 最初の問題を表示
        this.displayCurrentProblem();
        
        // 入力を有効化
        this.inputHandler.enableInput();
    }

    // 現在の問題を表示
    displayCurrentProblem() {
        const problem = this.gameEngine.getCurrentProblem();
        const questionNumber = this.gameEngine.getCurrentQuestionNumber();
        
        if (problem) {
            this.uiController.displayProblem(problem);
            this.uiController.updateQuestionCounter(questionNumber, 10);
        }
    }

    // ユーザー入力処理
    handleUserInput(digit) {
        if (!this.gameEngine.isActive()) return;
        
        // 入力を一時的に無効化（連続入力防止）
        this.inputHandler.disableInput();
        
        // 答えをチェック
        const isCorrect = this.gameEngine.checkAnswer(digit);
        const correctAnswer = this.gameEngine.getCurrentProblem().correctDigit;
        
        // 結果を表示
        this.uiController.displayResult(isCorrect, correctAnswer);
        
        // 次の問題への遷移
        setTimeout(() => {
            this.nextQuestion();
        }, 400); // 0.4秒後に次の問題へ
    }

    // 次の問題へ
    nextQuestion() {
        const nextProblem = this.gameEngine.nextProblem();
        
        if (nextProblem) {
            // 次の問題を表示
            this.displayCurrentProblem();
            this.inputHandler.enableInput();
        } else {
            // ゲーム終了
            this.endGame();
        }
    }

    // ゲーム終了
    endGame() {
        // タイマー停止
        this.timer.stop();
        
        // 入力を無効化
        this.inputHandler.disableInput();
        
        // ゲーム統計を取得
        const stats = this.gameEngine.getGameStats();
        
        // 結果画面を表示
        setTimeout(() => {
            this.uiController.showGameEndScreen(stats);
        }, 1000);
    }

    // ゲームリセット（前回と同じ難易度で即座に開始）
    resetGame() {
        // 前回と同じ難易度でゲーム開始
        this.startGame(this.lastDifficulty);
    }
}

// ページ読み込み完了後にアプリケーションを開始
document.addEventListener('DOMContentLoaded', () => {
    const app = new MathGameApp();
});