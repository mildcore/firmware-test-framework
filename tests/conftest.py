"""
pytest共享fixture定义

关键：包含自动执行的冒烟测试，失败则停止所有测试
"""

import pytest
from src.firmware import SSDFirmware
from src.protocol import NVMeProtocol, SATAProtocol
from src.utils import generate_random_data

SMOKE_TEST_FAILURE = False  # 控制冒烟测试结果，True表示失败，False表示通过


@pytest.fixture(autouse=True, scope="session")
def smoke_check():
    """
    冒烟测试 - 自动执行，验证基础环境

    autouse=True: 自动应用于所有测试
    scope="session": 整个测试会话只执行一次

    如果冒烟测试失败，后续测试不会执行
    """
    print("\n=== 执行冒烟测试 ===")

    if SMOKE_TEST_FAILURE:
        pytest.fail("冒烟测试失败 - 基础环境异常")

    # 测试1: 固件基础功能
    try:
        fw = SSDFirmware(device_id="SMOKE_TEST")
        result = fw.initialize()
        assert result["success"] is True

        # 测试读写
        write_result = fw.write(lba=0, data=b"smoke test data")
        assert write_result["success"] is True

        read_result = fw.read(lba=0, size=512)
        assert read_result["success"] is True

        print("✓ 固件基础功能正常")
    except Exception as e:
        pytest.fail(f"冒烟测试失败 - 固件功能异常: {e}")

    # 测试2: NVMe协议
    try:
        nvme = NVMeProtocol()
        result = nvme.identify(cns=0x01)
        assert result["success"] is True
        assert "mn" in result
        print("✓ NVMe协议正常")
    except Exception as e:
        pytest.fail(f"冒烟测试失败 - NVMe协议异常: {e}")

    # 测试3: SATA协议
    try:
        sata = SATAProtocol()
        result = sata.identify_device()
        assert result["success"] is True
        assert "model" in result
        print("✓ SATA协议正常")
    except Exception as e:
        pytest.fail(f"冒烟测试失败 - SATA协议异常: {e}")

    print("=== 冒烟测试通过 ===\n")
    yield


@pytest.fixture
def firmware():
    """创建基础固件实例"""
    fw = SSDFirmware(device_id="TEST_SSD_001")
    yield fw
    fw.reset()


@pytest.fixture
def initialized_firmware():
    """创建已初始化的固件实例"""
    fw = SSDFirmware(device_id="TEST_SSD_002")
    fw.initialize()
    yield fw
    fw.reset()


@pytest.fixture
def nvme_protocol():
    """创建NVMe协议实例"""
    return NVMeProtocol(device_id="TEST_NVMe_001")


@pytest.fixture
def sata_protocol():
    """创建SATA协议实例"""
    return SATAProtocol(device_id="TEST_SATA_001")


@pytest.fixture
def sample_data():
    """
    提供测试数据（512字节）
    """
    return generate_random_data(size=512, seed=50)
