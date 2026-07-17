// api.js — API 调用封装

const API_BASE = '/api/game';

const Api = {
    /**
     * 创建新游戏
     */
    async newGame() {
        const res = await fetch(`${API_BASE}/new`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        });
        if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
        }
        return res.json();
    },

    /**
     * 提交猜测
     */
    async guess(sessionId, word) {
        const res = await fetch(`${API_BASE}/${sessionId}/guess`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ word }),
        });
        if (!res.ok) {
            // 4xx/5xx 也尝试解析 JSON 错误响应
            const body = await res.json().catch(() => null);
            throw new ApiError(res.status, body);
        }
        return res.json();
    },

    /**
     * 获取猜测历史
     */
    async getHistory(sessionId) {
        const res = await fetch(`${API_BASE}/${sessionId}/history`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
    },

    /**
     * 放弃游戏
     */
    async giveUp(sessionId) {
        const res = await fetch(`${API_BASE}/${sessionId}/giveup`, {
            method: 'POST',
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
    },
};

class ApiError extends Error {
    constructor(status, body) {
        super(`HTTP ${status}`);
        this.status = status;
        this.body = body;
    }
}