import re
from app.models.schemas import ErrorCode


class ValidationError(Exception):
    """输入校验失败。"""
    def __init__(self, error_code: ErrorCode):
        self.error_code = error_code
        super().__init__(error_code.value)


# 中文 Unicode 范围
_CJK_RE = re.compile(r'^[一-鿿㐀-䶿]+$')

# 最大输入长度（字）
MAX_LENGTH = 4


def validate_guess(word: str) -> str:
    """
    校验并清洗用户输入。

    设计原则：
    - 仅使用结构性约束（长度、字符集），不使用关键词匹配过滤内容
    - 关键词匹配会误杀合法词汇（如词库中的"扮演"、"告诉"等）
    - 真正的安全来自架构：评分用 Embedding 数学计算，不用 LLM
    """
    word = word.strip()

    # 1. 空输入
    if len(word) == 0:
        raise ValidationError(ErrorCode.EMPTY_INPUT)

    # 2. 长度限制：词库中所有词均为 1-4 字
    if len(word) > MAX_LENGTH:
        raise ValidationError(ErrorCode.TOO_LONG)

    # 3. 字符白名单：仅允许中文字符
    if not _CJK_RE.match(word):
        raise ValidationError(ErrorCode.INVALID_CHARS)

    return word