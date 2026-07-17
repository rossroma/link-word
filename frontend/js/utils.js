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
     * 根据分数返回一条随机俏皮反馈语
     */
    getFeedback(score) {
        const pools = {
            '80-99': [
                '就差临门一脚了！🔥',
                '已经闻到答案的味道了 👃',
                '脑电波已接通，就差一毫米 ⚡',
                '太近了！目标词在向你招手 👋',
                '这个方向太对了，继续冲！🚀',
                '你的直觉今天开光了 ✨',
                '几乎要亲到答案了 💋',
                '这个热度，快把服务器烧了 🔥',
                '八九不离十，就差一丢丢 🤏',
                '你是不是偷偷看了答案？👀',
            ],
            '51-79': [
                '方向对了，但还不够味儿 🤔',
                '有点意思，但别太得意 😏',
                '语义雷达在哔哔响了 📡',
                '不错不错，继续摸鱼…啊不，继续猜词 🐟',
                '中规中矩，你的词汇量在发光 ✨',
                '及格线以上，继续保持 💪',
                '有点感觉了，但感觉不太多 🧐',
                '爬到半山腰了，别停！⛰️',
                '这个方向暖起来了 🌤️',
                'AI 点了点头，但没完全点 🤖',
            ],
            '21-50': [
                '不能说毫无关系，只能说毫不相干 🫠',
                '方向偏了，但偏着偏着可能就对了 🧭',
                '你的想象力很丰富，就是不太对 🎨',
                '至少不是 0 分，对吧？对吧？😬',
                '语义上…还有点距离，物理上也是 🏃',
                '这个脑回路，AI 需要消化一下 🌀',
                '有点偏，但偏得很有创意 🎪',
                '你在试探，AI 在叹气 💨',
                '不算太离谱，但离靠谱也有距离 📏',
                '加油，你已经成功引起了 AI 的注意 👀',
            ],
            '0-20': [
                'AI 看了都沉默了 🤖💤',
                '冷得我穿上了羽绒服 🧊',
                '你是来活跃气氛的吧？成功了 😂',
                '这……你是随机打字吗？🎲',
                '恭喜获得「反向指标」称号 🏆',
                '这个方向，不能说错，只能说全错 🧱',
                '负分其实也是天赋…但这不是负分 😅',
                '你的勇气值得表扬，但方向… 🫣',
                'AI 的 CPU 被你干烧了 🔥💻',
                '大海捞针第一式：先捞个锤子 🔨',
            ],
        };

        let bucket;
        if (score >= 80) bucket = '80-99';
        else if (score >= 51) bucket = '51-79';
        else if (score >= 21) bucket = '21-50';
        else bucket = '0-20';

        const messages = pools[bucket];
        return messages[Math.floor(Math.random() * messages.length)];
    },

    /**
     * 获取反馈横幅的 CSS 类名
     */
    feedbackClass(score) {
        if (score >= 80) return 'fb-80-99';
        if (score >= 51) return 'fb-51-79';
        if (score >= 21) return 'fb-21-50';
        return 'fb-0-20';
    },

    /**
     * 禁用/启用文本选择（用于动画期间）
     */
    setUserSelect(enable) {
        document.body.style.userSelect = enable ? '' : 'none';
        document.body.style.webkitUserSelect = enable ? '' : 'none';
    },
};