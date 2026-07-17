import random
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from app.config import config

logger = logging.getLogger(__name__)


class WordPicker:
    """
    智能选词器：加权随机 + 冷却机制 + 类别轮转。
    确保词的选择具有多样性和随机性，避免短期重复。
    """

    def __init__(self, word_bank: list[dict]):
        self.word_bank = [
            w for w in word_bank
            if 1 <= len(w["word"]) <= 4  # 确保长度符合规则
        ]
        self.global_cooldown: dict[str, datetime] = {}
        self.player_history: dict[str, list[str]] = defaultdict(list)
        self.last_category: str | None = None

        # 按类别预分组
        self.words_by_category: dict[str, list[dict]] = defaultdict(list)
        for w in self.word_bank:
            cat = w.get("category", "other")
            self.words_by_category[cat].append(w)

        logger.info(
            f"WordPicker initialized: {len(self.word_bank)} words, "
            f"{len(self.words_by_category)} categories"
        )

    def pick(self, player_id: str | None = None) -> dict:
        """选词主流程。"""
        now = datetime.now()

        # Step 1: 全局冷却过滤
        candidates = [
            w for w in self.word_bank
            if self._global_cooldown_ok(w["word"], now)
        ]

        # Step 2: 玩家历史过滤
        if player_id and len(candidates) > 10:
            recent = set(self.player_history[player_id][-config.PLAYER_AVOID_RECENT:])
            filtered = [w for w in candidates if w["word"] not in recent]
            if filtered:
                candidates = filtered

        # Step 3: 类别轮转
        if self.last_category and len(candidates) > 5:
            different = [w for w in candidates if w.get("category") != self.last_category]
            if different and random.random() < 0.8:
                candidates = different

        # Step 4: 加权随机
        chosen = self._weighted_choice(candidates, now)

        # Step 5: 更新状态
        self.global_cooldown[chosen["word"]] = now
        self.last_category = chosen.get("category")
        if player_id:
            self.player_history[player_id].append(chosen["word"])
            if len(self.player_history[player_id]) > 100:
                self.player_history[player_id] = self.player_history[player_id][-100:]

        logger.debug(f"Picked: {chosen['word']} (category={chosen.get('category')})")
        return chosen

    def _global_cooldown_ok(self, word: str, now: datetime) -> bool:
        last_used = self.global_cooldown.get(word)
        if last_used is None:
            return True
        return (now - last_used) > timedelta(minutes=config.WORD_COOLDOWN_MINUTES)

    def _weighted_choice(self, candidates: list[dict], now: datetime) -> dict:
        weights = []
        for w in candidates:
            base = 1.0
            last_used = self.global_cooldown.get(w["word"])
            if last_used:
                hours = (now - last_used).total_seconds() / 3600
                cooldown_weight = min(hours / 24, 5.0)
            else:
                cooldown_weight = 2.0  # 从未被选过的词有额外权重
            weights.append(base * cooldown_weight)

        total = sum(weights)
        r = random.uniform(0, total)
        cumulative = 0.0
        for w, weight in zip(candidates, weights):
            cumulative += weight
            if r <= cumulative:
                return w
        return candidates[-1]