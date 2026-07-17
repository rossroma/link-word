// components.js — UI 组件（DOM 操作）

const Components = {
    /**
     * 显示目标词 + 游戏结果（直接在目标卡片内展示）
     */
    revealTarget(word, status, guessCount) {
        const card = document.getElementById('target-card');
        const wordEl = document.getElementById('target-word');
        const hint = document.getElementById('target-hint');
        const icon = document.getElementById('target-icon');
        const result = document.getElementById('target-result');
        const stats = document.getElementById('target-result-stats');

        wordEl.textContent = word;
        wordEl.classList.add('revealed');
        hint.textContent = '答案揭晓';

        card.classList.remove('won', 'lost');

        if (status === 'won') {
            icon.textContent = '🎉';
            card.classList.add('won');
            stats.textContent = `你用了 ${guessCount} 次猜测`;
            result.style.display = 'block';
            Utils.vibrate();
            this._fireConfetti();
        } else if (status === 'lost') {
            icon.textContent = '😢';
            card.classList.add('lost');
            stats.textContent = `共猜测了 ${guessCount} 次`;
            result.style.display = 'block';
        } else {
            // abandoned
            icon.textContent = '👋';
            card.classList.add('lost');
            stats.textContent = `共猜测了 ${guessCount} 次`;
            result.style.display = 'block';
        }
    },

    /**
     * 重置目标词卡片
     */
    resetTarget() {
        const card = document.getElementById('target-card');
        const wordEl = document.getElementById('target-word');
        const hint = document.getElementById('target-hint');
        const icon = document.getElementById('target-icon');
        const result = document.getElementById('target-result');

        wordEl.textContent = '?';
        wordEl.classList.remove('revealed');
        hint.textContent = '目标词隐藏中';
        icon.textContent = '🎯';
        card.classList.remove('won', 'lost');
        result.style.display = 'none';

        // 隐藏重试按钮
        document.getElementById('giveup-btn').style.display = 'none';
    },

    /**
     * 根据猜测次数决定是否显示重试按钮（≥10 次才显示）
     */
    updateGiveupButton(guessCount) {
        const btn = document.getElementById('giveup-btn');
        btn.style.display = guessCount >= 10 ? 'flex' : 'none';
    },

    /**
     * 显示错误提示
     */
    showError(message) {
        const toast = document.getElementById('error-toast');
        toast.textContent = message;
        toast.style.display = 'block';

        clearTimeout(this._errorTimer);
        this._errorTimer = setTimeout(() => {
            toast.style.display = 'none';
        }, 2500);
    },

    /**
     * 刷新整个猜测历史列表（按分数从高到低排序）
     */
    refreshHistory(guesses) {
        const list = document.getElementById('history-list');
        list.innerHTML = '';

        if (!guesses || guesses.length === 0) {
            list.innerHTML = '<div class="history-empty">输入词汇开始猜测吧！</div>';
            document.getElementById('history-count').textContent = '0 次';
            return;
        }

        const sorted = [...guesses].sort((a, b) => b.score - a.score);

        sorted.forEach((g) => {
            const row = document.createElement('div');
            row.className = 'history-row' + (g.score === 100 ? ' won' : '');

            const scoreClass = Utils.scoreColorClass(g.score);
            const barClass = Utils.scoreBarClass(g.score);

            row.innerHTML = `
                <span class="history-num">#${g.guess_number}</span>
                <span class="history-word">${this._escapeHtml(g.word)}</span>
                <span class="history-score ${scoreClass}">${g.score}</span>
                <div class="history-bar-wrap">
                    <div class="history-bar ${barClass}" style="width: ${g.score}%;"></div>
                </div>
            `;

            list.appendChild(row);
        });

        document.getElementById('history-count').textContent = `${guesses.length} 次`;
    },

    /**
     * 清空猜测历史
     */
    clearHistory() {
        const list = document.getElementById('history-list');
        list.innerHTML = '<div class="history-empty">输入词汇开始猜测吧！</div>';
        document.getElementById('history-count').textContent = '0 次';
    },

    /**
     * 设置输入框启用/禁用
     */
    setInputEnabled(enabled) {
        const input = document.getElementById('guess-input');
        input.disabled = !enabled;
        if (enabled) {
            input.classList.remove('loading');
        }
    },

    /**
     * 清空输入框并聚焦
     */
    clearAndFocusInput() {
        const input = document.getElementById('guess-input');
        input.value = '';
        input.focus();
    },

    /**
     * 设置加载状态
     */
    setLoading(loading) {
        const input = document.getElementById('guess-input');
        if (loading) {
            input.classList.add('loading');
            input.disabled = true;
        } else {
            input.classList.remove('loading');
            input.disabled = false;
        }
    },

    /**
     * 烟花特效（canvas-confetti）
     */
    _fireConfetti() {
        if (typeof confetti === 'undefined') return;

        confetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.6 },
        });

        setTimeout(() => {
            confetti({
                particleCount: 50,
                angle: 60,
                spread: 55,
                origin: { x: 0 },
            });
            confetti({
                particleCount: 50,
                angle: 120,
                spread: 55,
                origin: { x: 1 },
            });
        }, 200);
    },

    _escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },
};