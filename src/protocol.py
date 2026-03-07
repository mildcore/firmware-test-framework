"""
协议模拟模块
模拟SATA/NVMe协议命令处理
"""

from enum import Enum
from typing import Dict


class ProtocolType(Enum):
    """协议类型枚举"""

    SATA = "SATA"
    NVMe = "NVMe"


class ProtocolError(Exception):
    """协议错误异常"""

    pass


class NVMeProtocol:
    """NVMe协议模拟类"""

    def __init__(self, device_id: str = "NVMe001", namespace_id: int = 1):
        self.device_id = device_id
        self.namespace_id = namespace_id
        self._device_info = {
            "vendor_id": "0x1E4B",
            "model_number": "MAP1602 NVMe SSD 512GB",
            "serial_number": f"SN{device_id}",
            "firmware_revision": "1.0.0",
            "capacity_gb": 512,
        }

    def identify(self, cns: int = 1) -> Dict:
        """Identify命令"""
        if cns == 0x01:  # Controller
            return {
                "success": True,
                "vid": self._device_info["vendor_id"],
                "mn": self._device_info["model_number"],
                "sn": self._device_info["serial_number"],
                "fr": self._device_info["firmware_revision"],
            }
        elif cns == 0x00:  # Namespace
            return {
                "success": True,
                "nsze": 0x3B9ACA00,  # Namespace Size (逻辑块数)
                "ncap": 0x3B9ACA00,  # Namespace Capacity
            }
        else:
            raise ProtocolError(f"不支持的CNS值: {cns}")

    def read_command(self, namespace_id: int, lba: int, block_count: int) -> Dict:
        """Read命令"""
        if namespace_id != self.namespace_id:
            raise ProtocolError(f"无效的Namespace ID: {namespace_id}")

        return {
            "success": True,
            "namespace_id": namespace_id,
            "lba": lba,
            "block_count": block_count,
            "data_transfer_size": block_count * 512,
        }

    def write_command(self, namespace_id: int, lba: int, data: bytes) -> Dict:
        """Write命令"""
        if namespace_id != self.namespace_id:
            raise ProtocolError(f"无效的Namespace ID: {namespace_id}")

        return {
            "success": True,
            "namespace_id": namespace_id,
            "lba": lba,
            "blocks_written": (len(data) + 511) // 512,
        }

    def flush_command(self, namespace_id: int) -> Dict:
        """Flush命令"""
        return {"success": True, "namespace_id": namespace_id, "status": "Data flushed"}


class SATAProtocol:
    """SATA协议模拟类"""

    def __init__(self, device_id: str = "SATA001"):
        self.device_id = device_id
        self.link_speed = "6Gb/s"

    def identify_device(self) -> Dict:
        """Identify Device命令"""
        return {
            "success": True,
            "model": "MAP1202 SATA SSD 512GB",
            "serial": f"SN{self.device_id}",
            "firmware": "1.0.0",
            "capacity_lba": 1000215216,
            "link_speed": self.link_speed,
        }

    def read_dma(self, lba: int, count: int) -> Dict:
        """Read DMA命令"""
        return {"success": True, "lba": lba, "count": count, "mode": "DMA"}
