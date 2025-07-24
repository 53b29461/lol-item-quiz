// ゲームエンジンクラス
class GameEngine {
    constructor() {
        this.gameState = {
            currentQuestion: 0,
            totalQuestions: 10,
            correctAnswers: 0,
            problems: [],
            startTime: null,
            endTime: null,
            isGameActive: false,
            difficulty: 'normal' // 'normal' or 'hard'
        };
        
        this.currentProblem = null;
    }

    // ゲーム開始
    startGame(difficulty = 'normal') {
        this.gameState = {
            currentQuestion: 1, // 1から開始
            totalQuestions: 10,
            correctAnswers: 0,
            problems: [],
            startTime: Date.now(),
            endTime: null,
            isGameActive: true,
            difficulty: difficulty
        };
        
        // 最初の問題を生成（currentQuestionを増加させない）
        this.currentProblem = this.generateProblem();
    }

    // 問題生成
    generateProblem() {
        if (this.gameState.difficulty === 'hard') {
            return this.generateHardProblem();
        } else {
            return this.generateNormalProblem();
        }
    }

    // ノーマル問題生成
    generateNormalProblem() {
        const operationType = Math.floor(Math.random() * 3); // 0: 加算, 1: 減算, 2: 乗算
        let num1, num2, answer, expression;
        
        switch (operationType) {
            case 0: // 加算: 2桁 + 2桁
                num1 = Math.floor(Math.random() * 90) + 10; // 10-99
                num2 = Math.floor(Math.random() * 90) + 10; // 10-99
                answer = num1 + num2;
                expression = `${num1} + ${num2}`;
                break;
                
            case 1: // 減算: 3桁 - 2桁
                num1 = Math.floor(Math.random() * 900) + 100; // 100-999
                num2 = Math.floor(Math.random() * 90) + 10; // 10-99
                // 結果が正の数になるように調整
                if (num2 > num1) {
                    num1 = num2 + Math.floor(Math.random() * 100) + 1;
                }
                answer = num1 - num2;
                expression = `${num1} - ${num2}`;
                break;
                
            case 2: // 乗算: 2桁 × 1桁
                num1 = Math.floor(Math.random() * 90) + 10; // 10-99
                num2 = Math.floor(Math.random() * 9) + 1; // 1-9
                answer = num1 * num2;
                expression = `${num1} × ${num2}`;
                break;
        }
        
        return this.createProblemObject(expression, answer);
    }

    // ハード問題生成
    generateHardProblem() {
        const operationType = Math.floor(Math.random() * 4); // 0: 加算, 1: 減算, 2: 乗算, 3: 除算
        let num1, num2, answer, expression;
        
        switch (operationType) {
            case 0: // 加算: 3桁 + 1-4桁
                num1 = Math.floor(Math.random() * 900) + 100; // 100-999
                const digitCount = Math.floor(Math.random() * 4) + 1; // 1-4桁
                if (digitCount === 1) {
                    num2 = Math.floor(Math.random() * 9) + 1; // 1-9
                } else if (digitCount === 2) {
                    num2 = Math.floor(Math.random() * 90) + 10; // 10-99
                } else if (digitCount === 3) {
                    num2 = Math.floor(Math.random() * 900) + 100; // 100-999
                } else {
                    num2 = Math.floor(Math.random() * 9000) + 1000; // 1000-9999
                }
                answer = num1 + num2;
                expression = `${num1} + ${num2}`;
                break;
                
            case 1: // 減算: 3-4桁 - n桁
                const minuendDigits = Math.floor(Math.random() * 2) + 3; // 3-4桁
                if (minuendDigits === 3) {
                    num1 = Math.floor(Math.random() * 900) + 100; // 100-999
                } else {
                    num1 = Math.floor(Math.random() * 9000) + 1000; // 1000-9999
                }
                
                // 引く数は被引数より小さく
                const maxSubtrahend = Math.min(num1 - 1, 9999);
                num2 = Math.floor(Math.random() * maxSubtrahend) + 1;
                answer = num1 - num2;
                expression = `${num1} - ${num2}`;
                break;
                
            case 2: // 乗算: 2桁 × 2桁
                num1 = Math.floor(Math.random() * 90) + 10; // 10-99
                num2 = Math.floor(Math.random() * 90) + 10; // 10-99
                answer = num1 * num2;
                expression = `${num1} × ${num2}`;
                break;
                
            case 3: // 除算: 3-4桁 ÷ n桁 (割り切れる)
                const quotientDigits = Math.floor(Math.random() * 2) + 3; // 3-4桁
                let dividend, divisor;
                
                if (quotientDigits === 3) {
                    dividend = Math.floor(Math.random() * 900) + 100; // 100-999
                } else {
                    dividend = Math.floor(Math.random() * 9000) + 1000; // 1000-9999
                }
                
                // 割り切れる除数を見つける
                const divisors = [];
                for (let i = 2; i <= Math.min(dividend, 999); i++) {
                    if (dividend % i === 0) {
                        divisors.push(i);
                    }
                }
                
                if (divisors.length === 0) {
                    return this.generateHardProblem(); // 再生成
                }
                
                divisor = divisors[Math.floor(Math.random() * divisors.length)];
                answer = dividend / divisor;
                expression = `${dividend} ÷ ${divisor}`;
                break;
        }
        
        return this.createProblemObject(expression, answer);
    }

    // 問題オブジェクト作成
    createProblemObject(expression, answer) {
        // 答えが1桁の場合は再生成
        if (answer < 10) {
            return this.generateProblem();
        }
        
        // 十の位か一の位をランダムに選択
        const targetDigit = Math.random() < 0.5 ? 'tens' : 'ones';
        const tensDigit = Math.floor(answer / 10) % 10;
        const onesDigit = answer % 10;
        const correctDigit = targetDigit === 'tens' ? tensDigit : onesDigit;
        
        // 答えを文字列に変換
        const answerStr = answer.toString();
        
        // 表示用テキスト（十の位または一の位を空欄にする）
        let displayText;
        if (targetDigit === 'tens') {
            // 十の位を空欄にする
            const displayAnswer = answerStr.slice(0, -2) + '_' + answerStr.slice(-1);
            displayText = `${expression} = ${displayAnswer}`;
        } else {
            // 一の位を空欄にする
            const displayAnswer = answerStr.slice(0, -1) + '_';
            displayText = `${expression} = ${displayAnswer}`;
        }
        
        return {
            expression: expression,
            answer: answer,
            targetDigit: targetDigit,
            correctDigit: correctDigit,
            displayText: displayText,
            tensDigit: tensDigit,
            onesDigit: onesDigit
        };
    }

    // 答えをチェック
    checkAnswer(userInput) {
        if (!this.currentProblem || !this.gameState.isGameActive) {
            return false;
        }
        
        const userDigit = parseInt(userInput);
        const isCorrect = userDigit === this.currentProblem.correctDigit;
        
        if (isCorrect) {
            this.gameState.correctAnswers++;
        }
        
        // 問題を履歴に追加
        this.gameState.problems.push({
            ...this.currentProblem,
            userAnswer: userDigit,
            isCorrect: isCorrect
        });
        
        return isCorrect;
    }

    // 次の問題へ
    nextProblem() {
        if (!this.gameState.isGameActive) return;
        
        this.gameState.currentQuestion++;
        
        if (this.gameState.currentQuestion > this.gameState.totalQuestions) {
            this.endGame();
            return null;
        }
        
        this.currentProblem = this.generateProblem();
        return this.currentProblem;
    }

    // ゲーム終了
    endGame() {
        this.gameState.isGameActive = false;
        this.gameState.endTime = Date.now();
        return this.getGameStats();
    }

    // ゲーム統計取得
    getGameStats() {
        const totalTime = this.gameState.endTime - this.gameState.startTime;
        const accuracy = Math.round((this.gameState.correctAnswers / this.gameState.totalQuestions) * 100);
        const avgTimePerQuestion = Math.floor(totalTime / this.gameState.totalQuestions / 1000);
        
        return {
            totalQuestions: this.gameState.totalQuestions,
            correctAnswers: this.gameState.correctAnswers,
            incorrectAnswers: this.gameState.totalQuestions - this.gameState.correctAnswers,
            accuracy: accuracy,
            totalTime: totalTime,
            totalTimeFormatted: this.formatTime(totalTime),
            averageTimePerQuestion: `00:${String(avgTimePerQuestion).padStart(2, '0')}`,
            problems: this.gameState.problems
        };
    }

    // 時間フォーマット
    formatTime(milliseconds) {
        const totalSeconds = Math.floor(milliseconds / 1000);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }

    // 現在の問題を取得
    getCurrentProblem() {
        return this.currentProblem;
    }

    // 現在の問題番号を取得
    getCurrentQuestionNumber() {
        return this.gameState.currentQuestion;
    }

    // ゲームがアクティブかどうか
    isActive() {
        return this.gameState.isGameActive;
    }
}