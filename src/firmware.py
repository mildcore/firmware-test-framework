"""
固件模拟模块
模拟SSD固件的基本操作和状态机
"""

import time
from enum import Enum
from typing import Dict, Tuple
from src.utils import retry, generate_random_data, calculate_checksum


class FirmwareStatus(Enum):
    """固件状态枚举"""

    IDLE = "idle"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"


class FirmwareError(Exception):
    """固件错误异常"""

    pass


class SSDFirmware:
    """
    SSD固件模拟类

    模拟SSD固件的核心功能：
    - 状态机管理（IDLE -> INITIALIZING -> READY）
    - 数据读写操作
    - SMART数据获取
    - 电源管理
    """

    def __init__(self, device_id: str = "SSD001", capacity_gb: int = 512):
        """
        初始化固件实例

        Args:
            device_id: 设备ID
            capacity_gb: 容量（GB）
        """
        self.device_id = device_id
        self.capacity_gb = capacity_gb
        self.sector_size = 512

        # 状态
        self.status = FirmwareStatus.IDLE
        self.initialized = False

        # 统计数据
        self.write_count = 0
        self.read_count = 0
        self.used_gb = 0.0

        # 模拟数据存储（LBA -> data）
        self._data_store: Dict[int, Tuple[bytes, int]] = {}

    @retry()
    def initialize(self, simulate_failure: bool = False) -> Dict:
        """
        初始化固件

        Args:
            simulate_failure: 是否模拟初始化失败（用于测试）

        Returns:
            Dict: 初始化结果
        """
        self.status = FirmwareStatus.INITIALIZING

        # 模拟初始化延迟
        time.sleep(0.05)

        # 参数控制失败（便于测试复现）
        if simulate_failure:
            self.status = FirmwareStatus.ERROR
            raise FirmwareError(f"固件 {self.device_id} 初始化失败（模拟）")

        self.status = FirmwareStatus.READY
        self.initialized = True

        return {
            "success": True,
            "device_id": self.device_id,
            "capacity_gb": self.capacity_gb,
            "status": self.status.value,
        }

    def read(self, lba: int, size: int = 512) -> Dict:
        """
        从指定LBA读取数据

        Args:
            lba: 逻辑块地址
            size: 读取大小（字节）
        """
        if not self.initialized:
            raise FirmwareError("固件未初始化")

        if self.status != FirmwareStatus.READY:
            raise FirmwareError(f"固件状态异常: {self.status.value}")

        # 模拟读取延迟
        time.sleep(0.001)

        self.read_count += 1

        # 获取数据或生成随机数据
        if lba in self._data_store:
            stored_data, checksum = self._data_store[lba]
            data = (
                stored_data[:size]
                if len(stored_data) >= size
                else stored_data + b"\x00" * (size - len(stored_data))
            )
        else:
            data = generate_random_data(size, 52)
            checksum = calculate_checksum(data)

        return {
            "success": True,
            "lba": lba,
            "size": size,
            "data": data,
            "checksum": checksum,
        }

    def write(self, lba: int, data: bytes) -> Dict:
        """
        向指定LBA写入数据

        Args:
            lba: 逻辑块地址
            data: 要写入的数据
        """
        if not self.initialized:
            raise FirmwareError("固件未初始化")

        if self.status != FirmwareStatus.READY:
            raise FirmwareError(f"固件状态异常: {self.status.value}")

        # 模拟写入延迟
        time.sleep(0.002)

        self.write_count += 1
        self.used_gb += len(data) / (1024**3)

        # 计算校验和并存储
        checksum = calculate_checksum(data)
        self._data_store[lba] = (data, checksum)

        return {"success": True, "lba": lba, "size": len(data), "checksum": checksum}

    def get_smart_data(self) -> Dict:
        """获取SMART数据"""
        if not self.initialized:
            raise FirmwareError("固件未初始化")

        return {
            "device_id": self.device_id,
            "write_count": self.write_count,
            "read_count": self.read_count,
            "used_gb": round(self.used_gb, 2),
            "health": "Good",
        }

    def power_management(self, mode: str) -> Dict:
        """电源管理"""
        valid_modes = ["active", "idle", "sleep"]
        if mode not in valid_modes:
            raise FirmwareError(f"无效的电源模式: {mode}")

        power_map = {"active": 5000, "idle": 1000, "sleep": 100}

        return {"success": True, "mode": mode, "power_consumption_mw": power_map[mode]}

    def reset(self) -> Dict:
        """复位固件"""
        self.status = FirmwareStatus.IDLE
        self.initialized = False
        self.write_count = 0
        self.read_count = 0
        self.used_gb = 0.0
        self._data_store.clear()

        return {"success": True, "message": "固件已复位"}
