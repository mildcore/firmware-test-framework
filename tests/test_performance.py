"""
性能测试
测试固件性能指标
"""

import time

import pytest
from src.firmware import SSDFirmware


@pytest.mark.slow
class TestFirmwarePerformance:
    """测试固件性能"""

    def test_read_latency(self, initialized_firmware: SSDFirmware):
        """测试读取延迟"""
        latencies = []

        for _ in range(100):
            start = time.perf_counter()
            initialized_firmware.read(lba=0, size=512)
            end = time.perf_counter()
            latencies.append((end - start) * 1000)  # 转换为ms

        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)

        # 断言平均延迟小于5ms
        assert avg_latency < 5.0, f"平均延迟 {avg_latency}ms 超过阈值"
        # 断言最大延迟小于20ms
        assert max_latency < 20.0, f"最大延迟 {max_latency}ms 超过阈值"

    def test_write_latency(self, initialized_firmware: SSDFirmware, sample_data):
        """测试写入延迟 (使用 fixture 准备数据)"""
        latencies = []

        # Act: 执行100次写入，测量延迟
        for _ in range(100):
            start = time.perf_counter()
            initialized_firmware.write(lba=0, data=sample_data)
            end = time.perf_counter()
            latencies.append((end - start) * 1000)

        avg_latency = sum(latencies) / len(latencies)

        # 断言平均延迟小于10ms
        assert avg_latency < 10.0, f"平均写入延迟 {avg_latency}ms 超过阈值"

    def test_consecutive_reads(self, initialized_firmware: SSDFirmware):
        """测试连续读取性能"""
        start = time.perf_counter()

        for i in range(1000):
            initialized_firmware.read(lba=i, size=512)

        end = time.perf_counter()
        total_time = end - start

        # 1000次读取应该在5秒内完成
        assert total_time < 5.0, f"1000次读取耗时 {total_time}s 超过阈值"

    def test_iops_performance(self, initialized_firmware: SSDFirmware):
        """测试IOPS性能"""
        duration = 2  # 测试2秒
        count = 0
        start = time.perf_counter()
        end = start + duration

        while time.perf_counter() < end:
            initialized_firmware.read(lba=count, size=512)
            count += 1
        count = count // duration  # 计算每秒IOPS

        # IOPS应该大于300
        assert count > 300, f"IOPS {count} 低于阈值"
