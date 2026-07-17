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

        card.classList.remove('hidden', 'won', 'lost');

        if (status === 'won') {
            icon.textContent = '🎉';
            card.classList.add('won');
            stats.textContent = `你用了 ${guessCount} 次猜测，太棒了！`;
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

        // 结果态：隐藏历史列表和输入框
        document.getElementById('history-section').style.display = 'none';
        document.getElementById('welcome-section').style.display = 'none';
        this.hideFooter();
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

        wordEl.innerHTML = '<i class="fa-solid fa-circle-question target-question-icon"></i>';
        wordEl.classList.remove('revealed');
        hint.textContent = '目标词隐藏中';
        icon.textContent = '🎯';
        card.classList.remove('won', 'lost');
        card.classList.add('hidden'); // 欢迎态默认隐藏，等 clearHistory 时再显示
        result.style.display = 'none';

        // 隐藏重试按钮
        document.getElementById('giveup-btn').style.display = 'none';
    },

    /**
     * 根据猜测次数决定是否显示重试按钮（≥3 次才显示）
     */
    updateGiveupButton(guessCount) {
        const btn = document.getElementById('giveup-btn');
        btn.style.display = guessCount >= 3 ? 'flex' : 'none';
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
            document.getElementById('history-count').textContent = '0 次';
            return;
        }

        const sorted = [...guesses].sort((a, b) => b.score - a.score);
        const latestNum = Math.max(...guesses.map(g => g.guess_number));

        sorted.forEach((g) => {
            const row = document.createElement('div');
            const isLatest = g.guess_number === latestNum;
            row.className = 'history-row' + (g.score === 100 ? ' won' : '') + (isLatest ? ' latest' : '');

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

        // 自动滚动最新猜测到可视区域中间
        requestAnimationFrame(() => {
            const latestRow = list.querySelector('.history-row.latest');
            if (latestRow) {
                latestRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
    },

    /**
     * 清空猜测历史并切换到欢迎状态
     */
    clearHistory() {
        const list = document.getElementById('history-list');
        list.innerHTML = '';
        document.getElementById('history-count').textContent = '0 次';
        document.getElementById('history-section').style.display = 'none';
        document.getElementById('welcome-section').style.display = 'flex';
        // 欢迎态：显示美化后的目标卡片
        document.getElementById('target-card').classList.remove('hidden');
        this.showFooter();
    },

    /**
     * 显示猜测历史（隐藏欢迎状态）
     */
    showHistory() {
        document.getElementById('welcome-section').style.display = 'none';
        document.getElementById('history-section').style.display = 'block';
        // 进行中：隐藏目标卡片，释放空间
        document.getElementById('target-card').classList.add('hidden');
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
     * 隐藏底部输入框（结果态使用）
     */
    hideFooter() {
        document.querySelector('.footer').classList.add('hidden');
    },

    /**
     * 显示底部输入框
     */
    showFooter() {
        document.querySelector('.footer').classList.remove('hidden');
    },

    /**
     * 烟花特效（canvas-confetti）
     */
    _fireConfetti() {
        if (typeof confetti === 'undefined') return;

        const duration = 1500;
        const end = Date.now() + duration;

        const frame = () => {
            confetti({
                particleCount: 3,
                angle: 60,
                spread: 55,
                origin: { x: 0, y: 0.7 },
                colors: ['#6c5ce7', '#a29bfe', '#f1c40f', '#2ecc71'],
            });
            confetti({
                particleCount: 3,
                angle: 120,
                spread: 55,
                origin: { x: 1, y: 0.7 },
                colors: ['#6c5ce7', '#a29bfe', '#f1c40f', '#2ecc71'],
            });

            if (Date.now() < end) {
                requestAnimationFrame(frame);
            }
        };

        // 初始爆发
        confetti({
            particleCount: 80,
            spread: 80,
            origin: { y: 0.6 },
            colors: ['#6c5ce7', '#a29bfe', '#f1c40f', '#2ecc71', '#2ecc71'],
        });

        setTimeout(() => frame(), 300);
    },

    _escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },
};