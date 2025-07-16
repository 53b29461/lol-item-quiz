// タイマークラス
class Timer {
    constructor() {
        this.startTime = null;
        this.endTime = null;
        this.intervalId = null;
        this.displayElement = null;
    }

    // タイマー開始
    start() {
        this.startTime = Date.now();
        this.endTime = null;
        
        // 表示更新を開始
        this.intervalId = setInterval(() => {
            this.displayTime();
        }, 100); // 100msごとに更新
    }

    // タイマー停止
    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        this.endTime = Date.now();
        return this.getElapsedTime();
    }

    // タイマーリセット
    reset() {
        this.stop();
        this.startTime = null;
        this.endTime = null;
        if (this.displayElement) {
            this.displayElement.textContent = '00:00';
        }
    }

    // 経過時間取得（ミリ秒）
    getElapsedTime() {
        if (!this.startTime) return 0;
        
        const end = this.endTime || Date.now();
        return end - this.startTime;
    }

    // 経過時間を文字列形式で取得
    getFormattedTime() {
        const elapsed = this.getElapsedTime();
        const totalSeconds = Math.floor(elapsed / 1000);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        
        return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }

    // 表示要素を設定
    setDisplayElement(element) {
        this.displayElement = element;
    }

    // タイマー表示更新
    displayTime() {
        if (this.displayElement) {
            this.displayElement.textContent = this.getFormattedTime();
        }
    }

    // 平均時間計算（ミリ秒→秒）
    static calculateAverageTime(totalTime, count) {
        if (count === 0) return '00:00';
        
        const avgSeconds = Math.floor((totalTime / count) / 1000);
        const minutes = Math.floor(avgSeconds / 60);
        const seconds = avgSeconds % 60;
        
        return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }
}