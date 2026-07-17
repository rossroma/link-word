// utils.js — 工具函数

const Utils = {
    /**
     * 获取分数对应的颜色 CSS 类名
     */
    scoreColorClass(score) {
        if (score === 100) return 'score-100';
        if (score >= 80) return 'score-80-99';
        if (score >= 51) return 'score-51-79';
        if (score >= 21) return 'score-21-50';
        return 'score-0-20';
    },

    /**
     * 获取分数进度条的颜色 CSS 类名
     */
    scoreBarClass(score) {
        if (score === 100) return 'bar-100';
        if (score >= 80) return 'bar-80-99';
        if (score >= 51) return 'bar-51-79';
        if (score >= 21) return 'bar-21-50';
        return 'bar-0-20';
    },

    /**
     * 格式化错误信息（用户可读）
     */
    formatError(errorCode) {
        const messages = {
            EMPTY_INPUT: '输入不能为空',
            TOO_LONG: '请输入 1-4 个字的中文词汇',
            INVALID_CHARS: '请输入中文词汇',
            SESSION_NOT_FOUND: '游戏会话已过期',
            GAME_ALREADY_ENDED: '游戏已结束',
            RATE_LIMITED: '操作太快，请稍后再试',
            INTERNAL_ERROR: '服务器错误，请重试',
        };
        return messages[errorCode] || '未知错误';
    },

    /**
     * 是否是游戏结束状态
     */
    isGameOver(status) {
        return status === 'won' || status === 'lost' || status === 'abandoned';
    },

    /**
     * 触发振动反馈（移动端）
     */
    vibrate() {
        if (navigator.vibrate) {
            navigator.vibrate(200);
        }
    },

    /**
     * 禁用/启用文本选择（用于动画期间）
     */
    setUserSelect(enable) {
        document.body.style.userSelect = enable ? '' : 'none';
        document.body.style.webkitUserSelect = enable ? '' : 'none';
    },
};