// UIコントローラークラス
class UIController {
    constructor() {
        // スクリーン要素
        this.startScreen = document.getElementById('startScreen');
        this.difficultyScreen = document.getElementById('difficultyScreen');
        this.gameScreen = document.getElementById('gameScreen');
        this.resultScreen = document.getElementById('resultScreen');
        
        // ゲーム要素
        this.currentQuestionElement = document.getElementById('currentQuestion');
        this.expressionElement = document.getElementById('expression');
        this.answerDisplayElement = document.getElementById('answerDisplay');
        this.instructionElement = document.getElementById('instruction');
        this.feedbackElement = document.getElementById('feedback');
        
        // 結果要素
        this.correctCountElement = document.getElementById('correctCount');
        this.accuracyElement = document.getElementById('accuracy');
        this.totalTimeElement = document.getElementById('totalTime');
        this.avgTimeElement = document.getElementById('avgTime');
    }

    // 画面切り替え
    showScreen(screenName) {
        // すべての画面を非表示
        this.startScreen.style.display = 'none';
        this.difficultyScreen.style.display = 'none';
        this.gameScreen.style.display = 'none';
        this.resultScreen.style.display = 'none';
        
        // 指定された画面を表示
        switch (screenName) {
            case 'start':
                this.startScreen.style.display = 'block';
                break;
            case 'difficulty':
                this.difficultyScreen.style.display = 'block';
                break;
            case 'game':
                this.gameScreen.style.display = 'block';
                break;
            case 'result':
                this.resultScreen.style.display = 'block';
                break;
        }
    }

    // 問題表示
    displayProblem(problem) {
        if (!problem) return;
        
        // 式を表示
        this.expressionElement.textContent = problem.expression;
        
        // 答えの表示（空欄付き）
        this.answerDisplayElement.textContent = problem.displayText.split(' = ')[1];
        
        // 指示文を表示
        const digitText = problem.targetDigit === 'tens' ? '十の位' : '一の位';
        this.instructionElement.textContent = `${digitText}の数字を入力してください`;
        
        // フィードバックをクリア
        this.clearFeedback();
    }

    // 問題番号更新
    updateQuestionCounter(current, total) {
        this.currentQuestionElement.textContent = current;
    }

    // 結果表示（正解/不正解）
    displayResult(isCorrect, correctAnswer) {
        this.feedbackElement.classList.remove('correct', 'incorrect');
        
        if (isCorrect) {
            this.feedbackElement.textContent = '正解！';
            this.feedbackElement.classList.add('correct');
        } else {
            this.feedbackElement.textContent = `不正解... 正解は ${correctAnswer} でした`;
            this.feedbackElement.classList.add('incorrect');
        }
    }

    // フィードバッククリア
    clearFeedback() {
        this.feedbackElement.textContent = '';
        this.feedbackElement.classList.remove('correct', 'incorrect');
    }

    // ゲーム終了画面表示
    showGameEndScreen(stats) {
        // 結果を表示
        this.correctCountElement.textContent = `${stats.correctAnswers}/10`;
        this.accuracyElement.textContent = `${stats.accuracy}%`;
        this.totalTimeElement.textContent = stats.totalTimeFormatted;
        this.avgTimeElement.textContent = stats.averageTimePerQuestion;
        
        // 結果画面を表示
        this.showScreen('result');
    }

    // UI初期化
    resetUI() {
        this.clearFeedback();
        this.currentQuestionElement.textContent = '1';
        this.expressionElement.textContent = '';
        this.answerDisplayElement.textContent = '';
        this.instructionElement.textContent = '';
    }

    // ソフトキーボード表示
    showSoftKeyboard() {
        const keyboard = document.querySelector('.soft-keyboard');
        if (keyboard) {
            keyboard.style.display = 'flex';
        }
    }

    // ソフトキーボード非表示
    hideSoftKeyboard() {
        const keyboard = document.querySelector('.soft-keyboard');
        if (keyboard) {
            keyboard.style.display = 'none';
        }
    }

    // ローディング表示（必要に応じて）
    showLoading() {
        // 実装は必要に応じて
    }

    hideLoading() {
        // 実装は必要に応じて
    }

    // エラー表示（必要に応じて）
    showError(message) {
        console.error(message);
        // 実装は必要に応じて
    }
}