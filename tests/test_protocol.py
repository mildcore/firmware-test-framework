"""
协议命令测试
"""

import pytest
from src.protocol import ProtocolError


class TestNVMe:
    """NVMe协议测试"""

    def test_identify_controller(self, nvme_protocol):
        """测试Identify Controller"""
        result = nvme_protocol.identify(cns=0x01)
        assert result["success"] is True
        assert "mn" in result

    def test_identify_namespace(self, nvme_protocol):
        """测试Identify Namespace"""
        result = nvme_protocol.identify(cns=0x00)
        assert result["success"] is True
        assert "nsze" in result

    def test_read_command(self, nvme_protocol):
        """测试Read命令"""
        result = nvme_protocol.read_command(1, 0, 8)
        assert result["success"] is True
        assert result["block_count"] == 8

    def test_write_command(self, nvme_protocol):
        """测试Write命令"""
        result = nvme_protocol.write_command(1, 100, b"test")
        assert result["success"] is True

    def test_flush_command(self, nvme_protocol):
        """测试NVMe Flush命令"""
        result = nvme_protocol.flush_command(namespace_id=1)
        assert result["success"] is True
        assert "flushed" in result["status"]

    def test_invalid_namespace(self, nvme_protocol):
        """测试无效Namespace"""
        with pytest.raises(ProtocolError):
            nvme_protocol.read_command(99, 0, 1)


class TestSATA:
    """SATA协议测试"""

    def test_identify(self, sata_protocol):
        """测试Identify Device"""
        result = sata_protocol.identify_device()
        assert result["success"] is True
        assert result["link_speed"] == "6Gb/s"

    def test_read_dma(self, sata_protocol):
        """测试Read DMA"""
        result = sata_protocol.read_dma(0, 16)
        assert result["success"] is True
        assert result["mode"] == "DMA"
