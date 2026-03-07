"""
工具函数模块
"""

import time
import random
from typing import Callable, Any, Optional
from functools import wraps


def retry(max_attempts: int = 3, delay: float = 0.5):
    """重试装饰器"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    time.sleep(delay)
            return None

        return wrapper

    return decorator


def generate_random_data(size: int, seed: Optional[int] = None) -> bytes:
    """生成随机数据"""
    if seed is not None:
        state = random.getstate()
        random.seed(seed)
        try:
            data = bytes(random.randint(0, 255) for _ in range(size))
        finally:
            random.setstate(state)
    else:
        data = bytes(random.randint(0, 255) for _ in range(size))
    return data


def calculate_checksum(data: bytes) -> int:
    """计算校验和"""
    if not data:
        return 0
    return sum(data) % 256
