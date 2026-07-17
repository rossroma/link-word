// app.js — 主应用逻辑

const App = {
    sessionId: null,
    status: null,
    guesses: [],

    async init() {
        this._bindEvents();
        await this._startNewGame();
    },

    _bindEvents() {
        const input = document.getElementById('guess-input');
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this._submitGuess();
            }
        });

        document.getElementById('giveup-btn').addEventListener('click', () => {
            this._giveUp();
        });

        document.getElementById('target-result-btn').addEventListener('click', () => {
            this._startNewGame();
        });

        if (window.visualViewport) {
            window.visualViewport.addEventListener('resize', () => {
                const keyboardHeight = window.innerHeight - window.visualViewport.height;
                if (keyboardHeight > 100) {
                    setTimeout(() => {
                        document.getElementById('guess-input').scrollIntoView({
                            behavior: 'smooth',
                            block: 'center',
                        });
                    }, 300);
                }
            });
        }
    },

    async _startNewGame() {
        try {
            Components.setLoading(true);

            const data = await Api.newGame();
            this.sessionId = data.session_id;
            this.status = 'playing';
            this.guesses = [];

            Components.resetTarget();
            Components.clearHistory();
            Components.clearAndFocusInput();
            Components.setInputEnabled(true);
            Components.setLoading(false);
        } catch (err) {
            Components.setLoading(false);
            Components.showError('创建游戏失败，请检查网络连接');
            console.error('New game error:', err);
        }
    },

    async _submitGuess() {
        if (this.status !== 'playing') return;

        const input = document.getElementById('guess-input');
        const word = input.value.trim();
        if (!word) return;

        try {
            Components.setLoading(true);

            const data = await Api.guess(this.sessionId, word);

            if (data.type === 'error') {
                Components.showError(Utils.formatError(data.error_code));
                Components.setLoading(false);
                Components.setInputEnabled(true);
                Components.clearAndFocusInput();
                return;
            }

            if (data.type === 'guess_result') {
                this.guesses.push({
                    word: word,
                    score: data.score,
                    guess_number: data.guess_count,
                });

                Components.refreshHistory(this.guesses);
                Components.clearAndFocusInput();
                Components.updateGiveupButton(data.guess_count);

                this.status = data.status;

                if (data.status === 'won' || data.status === 'lost') {
                    // 在目标卡片内展示结果
                    Components.revealTarget(data.target_word, data.status, data.guess_count);
                    Components.setInputEnabled(false);
                }
            }

            Components.setLoading(false);
            if (this.status === 'playing') {
                Components.setInputEnabled(true);
            }
        } catch (err) {
            Components.setLoading(false);
            if (this.status === 'playing') {
                Components.setInputEnabled(true);
            }

            if (err instanceof ApiError) {
                const code = err.body?.error_code;
                Components.showError(Utils.formatError(code));
            } else {
                Components.showError('网络错误，请重试');
            }
            console.error('Guess error:', err);
        }
    },

    async _giveUp() {
        if (this.status !== 'playing') return;

        try {
            const data = await Api.giveUp(this.sessionId);
            this.status = data.status;

            Components.revealTarget(data.target_word, 'abandoned', data.guess_count);
            Components.setInputEnabled(false);
        } catch (err) {
            Components.showError('操作失败，请重试');
            console.error('Give up error:', err);
        }
    },
};

document.addEventListener('DOMContentLoaded', () => {
    App.init();
});