"""
固件功能测试
"""

import pytest
from src.firmware import FirmwareStatus, FirmwareError


class TestFirmwareInit:
    """基础功能测试"""

    def test_create_firmware(self, firmware):
        """测试创建固件实例"""
        assert firmware.device_id == "TEST_SSD_001"
        assert firmware.status == FirmwareStatus.IDLE
        assert firmware.initialized is False
        assert firmware.capacity_gb == 512
        assert firmware.sector_size == 512

    def test_initialize_success(self, firmware):
        """测试初始化成功"""
        result = firmware.initialize()
        assert result["success"] is True
        assert firmware.initialized is True

    def test_initialize_failure(self, firmware):
        """测试初始化失败（使用参数控制）"""
        with pytest.raises(FirmwareError) as exc_info:
            firmware.initialize(simulate_failure=True)
        assert "初始化失败" in str(exc_info.value)

    def test_firmware_reset(self, initialized_firmware):
        """测试固件复位功能"""
        # 先执行一些操作
        initialized_firmware.write(lba=0, data=b"test data")
        # 复位
        result = initialized_firmware.reset()
        assert result["success"] is True
        assert initialized_firmware.initialized is False
        assert initialized_firmware.status == FirmwareStatus.IDLE
        assert initialized_firmware.write_count == 0
        assert initialized_firmware.read_count == 0


class TestFirmwareReadWrite:

    def test_write(self, initialized_firmware):
        """测试写"""
        write_result = initialized_firmware.write(lba=0, data=b"hello")
        assert write_result["success"] is True

    def test_read(self, initialized_firmware):
        """测试读"""
        read_result = initialized_firmware.read(lba=0, size=512)
        assert read_result["success"] is True

    def test_read_before_init(self, firmware):
        """测试未初始化时读取应该失败"""
        with pytest.raises(FirmwareError) as exc_info:
            firmware.read(0, 512)
        assert "未初始化" in str(exc_info.value)

    def test_write_before_init(self, firmware):
        """测试未初始化时写入应该失败"""
        with pytest.raises(FirmwareError) as exc_info:
            firmware.write(0, b"test")
        assert "未初始化" in str(exc_info.value)

    def test_write_and_read_back(self, initialized_firmware, sample_data):
        """测试写入后读取（使用random_seed保证数据可重复）"""
        # 写入
        write_result = initialized_firmware.write(lba=200, data=sample_data)
        assert write_result["success"] is True
        # 读取
        read_result = initialized_firmware.read(lba=200, size=512)
        assert read_result["success"] is True
        assert read_result["data"] == sample_data

    def test_write_increases_write_count(self, initialized_firmware):
        """测试写入增加写入计数"""
        initial_count = initialized_firmware.write_count

        initialized_firmware.write(lba=0, data=b"X" * 512)
        assert initialized_firmware.write_count == initial_count + 1

        initialized_firmware.write(lba=1, data=b"Y" * 512)
        assert initialized_firmware.write_count == initial_count + 2

    def test_read_increases_read_count(self, initialized_firmware):
        """测试读取增加读取计数"""
        initial_count = initialized_firmware.read_count

        initialized_firmware.read(lba=0, size=512)
        assert initialized_firmware.read_count == initial_count + 1


class TestFirmwareSMART:
    """SMART数据测试"""

    def test_get_smart(self, initialized_firmware):
        """测试获取SMART数据"""
        smart = initialized_firmware.get_smart_data()
        assert "write_count" in smart
        assert "health" in smart

    def test_get_smart_data_before_init(self, firmware):
        """测试未初始化时获取SMART应该失败"""
        with pytest.raises(FirmwareError) as exc_info:
            firmware.get_smart_data()
        assert "未初始化" in str(exc_info.value)


class TestFirmwarePower:
    """电源管理测试"""

    @pytest.mark.parametrize(
        "mode,expected_power",
        [
            ("active", 5000),
            ("idle", 1000),
            ("sleep", 100),
        ],
    )
    def test_power_management_modes(self, mode, expected_power, initialized_firmware):
        """测试电源模式"""
        result = initialized_firmware.power_management(mode)
        assert result["success"] is True
        assert result["mode"] == mode
        assert result["power_consumption_mw"] == expected_power

    def test_power_management_invalid_mode(self, initialized_firmware):
        """测试无效电源模式"""
        with pytest.raises(FirmwareError) as exc_info:
            initialized_firmware.power_management("invalid_mode")

        assert "无效的电源模式" in str(exc_info.value)
