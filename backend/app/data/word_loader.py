import json
import logging
from pathlib import Path
from app.config import config

logger = logging.getLogger(__name__)

# 内存缓存
_word_bank: list[dict] | None = None


def load_word_bank() -> list[dict]:
    """加载词库到内存。"""
    global _word_bank
    if _word_bank is not None:
        return _word_bank

    path = Path(config.WORD_BANK_PATH)
    if not path.exists():
        logger.warning(f"Word bank not found at {path}, using fallback")
        _word_bank = _fallback_word_bank()
        return _word_bank

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 如果是列表直接使用，如果是字典取 words 字段
    if isinstance(data, list):
        _word_bank = data
    elif isinstance(data, dict):
        _word_bank = data.get("words", [])
    else:
        _word_bank = []

    logger.info(f"Loaded {len(_word_bank)} words from word bank")
    return _word_bank


def _fallback_word_bank() -> list[dict]:
    """内置回退词库（词库文件缺失时使用）。"""
    words = [
        # 食物
        {"word": "苹果", "category": "food", "difficulty": "easy"},
        {"word": "香蕉", "category": "food", "difficulty": "easy"},
        {"word": "西瓜", "category": "food", "difficulty": "easy"},
        {"word": "火锅", "category": "food", "difficulty": "easy"},
        {"word": "饺子", "category": "food", "difficulty": "easy"},
        {"word": "蛋糕", "category": "food", "difficulty": "easy"},
        {"word": "面包", "category": "food", "difficulty": "easy"},
        {"word": "巧克力", "category": "food", "difficulty": "easy"},
        {"word": "冰淇淋", "category": "food", "difficulty": "easy"},
        {"word": "葡萄", "category": "food", "difficulty": "easy"},
        {"word": "草莓", "category": "food", "difficulty": "easy"},
        {"word": "咖啡", "category": "food", "difficulty": "easy"},
        {"word": "牛奶", "category": "food", "difficulty": "easy"},
        {"word": "啤酒", "category": "food", "difficulty": "easy"},
        {"word": "米饭", "category": "food", "difficulty": "easy"},
        # 动物
        {"word": "熊猫", "category": "animals", "difficulty": "easy"},
        {"word": "老虎", "category": "animals", "difficulty": "easy"},
        {"word": "海豚", "category": "animals", "difficulty": "easy"},
        {"word": "蝴蝶", "category": "animals", "difficulty": "easy"},
        {"word": "大象", "category": "animals", "difficulty": "easy"},
        {"word": "狮子", "category": "animals", "difficulty": "easy"},
        {"word": "长颈鹿", "category": "animals", "difficulty": "easy"},
        {"word": "企鹅", "category": "animals", "difficulty": "easy"},
        {"word": "孔雀", "category": "animals", "difficulty": "easy"},
        {"word": "猫", "category": "animals", "difficulty": "easy"},
        {"word": "狗", "category": "animals", "difficulty": "easy"},
        {"word": "兔子", "category": "animals", "difficulty": "easy"},
        {"word": "鱼", "category": "animals", "difficulty": "easy"},
        {"word": "鸟", "category": "animals", "difficulty": "easy"},
        {"word": "蛇", "category": "animals", "difficulty": "easy"},
        # 自然
        {"word": "太阳", "category": "nature", "difficulty": "easy"},
        {"word": "月亮", "category": "nature", "difficulty": "easy"},
        {"word": "彩虹", "category": "nature", "difficulty": "easy"},
        {"word": "火山", "category": "nature", "difficulty": "easy"},
        {"word": "海洋", "category": "nature", "difficulty": "easy"},
        {"word": "森林", "category": "nature", "difficulty": "easy"},
        {"word": "沙漠", "category": "nature", "difficulty": "easy"},
        {"word": "闪电", "category": "nature", "difficulty": "easy"},
        {"word": "雪花", "category": "nature", "difficulty": "easy"},
        {"word": "星星", "category": "nature", "difficulty": "easy"},
        # 物品
        {"word": "手机", "category": "objects", "difficulty": "easy"},
        {"word": "电脑", "category": "objects", "difficulty": "easy"},
        {"word": "钥匙", "category": "objects", "difficulty": "easy"},
        {"word": "书包", "category": "objects", "difficulty": "easy"},
        {"word": "眼镜", "category": "objects", "difficulty": "easy"},
        {"word": "雨伞", "category": "objects", "difficulty": "easy"},
        {"word": "镜子", "category": "objects", "difficulty": "easy"},
        {"word": "蜡烛", "category": "objects", "difficulty": "easy"},
        {"word": "时钟", "category": "objects", "difficulty": "easy"},
        {"word": "剪刀", "category": "objects", "difficulty": "easy"},
        # 地点
        {"word": "学校", "category": "places", "difficulty": "easy"},
        {"word": "医院", "category": "places", "difficulty": "easy"},
        {"word": "公园", "category": "places", "difficulty": "easy"},
        {"word": "超市", "category": "places", "difficulty": "easy"},
        {"word": "机场", "category": "places", "difficulty": "easy"},
        {"word": "图书馆", "category": "places", "difficulty": "easy"},
        {"word": "电影院", "category": "places", "difficulty": "easy"},
        {"word": "博物馆", "category": "places", "difficulty": "easy"},
        {"word": "海滩", "category": "places", "difficulty": "easy"},
        {"word": "厨房", "category": "places", "difficulty": "easy"},
        # 职业
        {"word": "医生", "category": "professions", "difficulty": "easy"},
        {"word": "教师", "category": "professions", "difficulty": "easy"},
        {"word": "厨师", "category": "professions", "difficulty": "easy"},
        {"word": "警察", "category": "professions", "difficulty": "easy"},
        {"word": "司机", "category": "professions", "difficulty": "easy"},
        {"word": "歌手", "category": "professions", "difficulty": "easy"},
        {"word": "画家", "category": "professions", "difficulty": "easy"},
        {"word": "演员", "category": "professions", "difficulty": "easy"},
        {"word": "宇航员", "category": "professions", "difficulty": "easy"},
        {"word": "科学家", "category": "professions", "difficulty": "easy"},
        # 情感
        {"word": "快乐", "category": "emotions", "difficulty": "medium"},
        {"word": "悲伤", "category": "emotions", "difficulty": "medium"},
        {"word": "愤怒", "category": "emotions", "difficulty": "medium"},
        {"word": "恐惧", "category": "emotions", "difficulty": "medium"},
        {"word": "惊讶", "category": "emotions", "difficulty": "medium"},
        {"word": "爱情", "category": "emotions", "difficulty": "medium"},
        {"word": "孤独", "category": "emotions", "difficulty": "medium"},
        {"word": "希望", "category": "emotions", "difficulty": "medium"},
        {"word": "焦虑", "category": "emotions", "difficulty": "medium"},
        {"word": "骄傲", "category": "emotions", "difficulty": "medium"},
        # 动作
        {"word": "跑步", "category": "actions", "difficulty": "medium"},
        {"word": "游泳", "category": "actions", "difficulty": "medium"},
        {"word": "飞翔", "category": "actions", "difficulty": "medium"},
        {"word": "跳舞", "category": "actions", "difficulty": "medium"},
        {"word": "唱歌", "category": "actions", "difficulty": "medium"},
        {"word": "画画", "category": "actions", "difficulty": "medium"},
        {"word": "读书", "category": "actions", "difficulty": "medium"},
        {"word": "写字", "category": "actions", "difficulty": "medium"},
        {"word": "睡觉", "category": "actions", "difficulty": "medium"},
        {"word": "旅行", "category": "actions", "difficulty": "medium"},
        # 抽象
        {"word": "自由", "category": "abstract", "difficulty": "hard"},
        {"word": "梦想", "category": "abstract", "difficulty": "hard"},
        {"word": "时间", "category": "abstract", "difficulty": "hard"},
        {"word": "智慧", "category": "abstract", "difficulty": "hard"},
        {"word": "勇气", "category": "abstract", "difficulty": "hard"},
        {"word": "和平", "category": "abstract", "difficulty": "hard"},
        {"word": "真理", "category": "abstract", "difficulty": "hard"},
        {"word": "命运", "category": "abstract", "difficulty": "hard"},
        {"word": "记忆", "category": "abstract", "difficulty": "hard"},
        {"word": "灵魂", "category": "abstract", "difficulty": "hard"},
        # 文化
        {"word": "春节", "category": "culture", "difficulty": "medium"},
        {"word": "京剧", "category": "culture", "difficulty": "medium"},
        {"word": "功夫", "category": "culture", "difficulty": "medium"},
        {"word": "龙", "category": "culture", "difficulty": "medium"},
        {"word": "长城", "category": "culture", "difficulty": "medium"},
        {"word": "书法", "category": "culture", "difficulty": "medium"},
        {"word": "茶道", "category": "culture", "difficulty": "medium"},
        {"word": "太极", "category": "culture", "difficulty": "medium"},
        {"word": "瓷器", "category": "culture", "difficulty": "medium"},
        {"word": "丝绸", "category": "culture", "difficulty": "medium"},
    ]
    return words