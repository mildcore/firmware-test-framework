# SSD固件自动化测试框架

[![codecov](https://codecov.io/github/mildcore/firmware-test-framework/branch/main/graph/badge.svg?token=ZLRTF3OY93)](https://codecov.io/github/mildcore/firmware-test-framework)

## 运行测试

```bash
python -m venv .venv
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 安装依赖
python -m pip install --upgrade pip
pip install pip-tools
pip-compile requirements.in
pip-sync

#升级
#pip-compile --upgrade requirements.in
#pip-sync

# 运行所有测试
pytest

# 运行并生成HTML报告
pytest --html=report.html --self-contained-html

# 运行并生成覆盖率报告
pytest --cov=src --cov-report=html

# 只运行性能测试
pytest tests/test_performance.py

# 排除慢测试
pytest -m "not slow"
```

## 项目目标

搭建一个**SSD固件自动化测试框架**，用于：
1. 模拟SSD固件的基本操作（初始化、读写、电源管理）
2. 模拟存储协议命令（SATA/NVMe）
3. 编写自动化测试用例验证功能正确性
4. 生成测试报告，集成CI/CD


## 总体架构图
```
┌──────────────────────────────────────────────────────────────────────┐
│                    固件自动化测试框架架构                              │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────────────────────────────────────────────────────────┐   │
│   │                      测试层 (tests/)                          │   │
│   │  ┌────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │  │
│   │  │   冒烟测试  │ │   功能测试  │ │   协议测试   │ │  性能测试  │ │  │
│   │  │smoke_check │ │test_firmware│ │test_protocol│ │test_perf..│ │  │
│   │  └────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │  │
│   │                                                               │  │
│   │  ┌────────────────────────────────────────────────────────┐   │  │
│   │  │            Fixture层 (conftest.py)                      │  │  │
│   │  │  • 固件实例 (firmware) 测试数据（sample_data）            │  │  │
│   │  │  • 已初始化固件 (initialized_firmware)                   │  │  │
│   │  │  • 协议实例 (nvme_protocol, sata_protocol)               │  │  │
│   │  │  • 冒烟测试fixture (smoke_check)                         │  │  │
│   │  └────────────────────────────────────────────────────────┘  │   │
│   └──────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │                    被测系统层 (src/)                          │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │  │
│   │  │  SSD固件    │  │  NVMe协议   │  │      SATA协议        │  │  │
│   │  │ firmware.py │  │ protocol.py │  │    protocol.py      │  │  │
│   │  │             │  │             │  │                     │  │  │
│   │  │ • 初始化    │  │ • Identify  │  │ • Identify          │  │  │
│   │  │ • 读写      │  │ • Read      │  │ • Read DMA          │  │  │
│   │  │ • SMART     │  │ • Write     │  │                     │  │  │
│   │  │ • 电源管理  │  │ • Flush     │  │                     │  │  │
│   │  └─────────────┘  └─────────────┘  └─────────────────────┘  │  │
│   │                                                              │  │
│   │  ┌────────────────────────────────────────────────────────┐  │  │
│   │  │                 工具层 (utils.py)                       │  │  │
│   │  │  • 重试装饰器 (retry)                                    │  │  │
│   │  │  • 数据生成 (generate_random_data)                       │  │  │
│   │  │  • 校验和计算 (calculate_checksum)                       │  │  │
│   │  └────────────────────────────────────────────────────────┘  │  │
│   └──────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│                              ▼                                       │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │                         配置层                                │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │  │
│   │  │  pytest.ini │  │ requirements│  │    .github/         │  │  │
│   │  │             │  │             │  │    workflows/       │  │  │
│   │  │ • 测试发现  │  │ • 依赖包    │  │ • CI/CD配置         │  │  │
│   │  │ • 标记定义  │  │             │  │                     │  │  │
│   │  └─────────────┘  └─────────────┘  └─────────────────────┘  │  │
│   └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

## 模块职责说明

| 模块 | 文件 | 职责 |
|------|------|------|
| **固件模拟** | `src/firmware.py` | 模拟SSD固件的状态机、读写操作、SMART数据、电源管理 |
| **协议模拟** | `src/protocol.py` | 模拟NVMe和SATA协议命令（Identify、Read、Write等） |
| **工具函数** | `src/utils.py` | 提供重试机制、数据生成、校验和计算等通用功能 |
| **功能测试** | `tests/test_firmware.py` | 固件功能测试 |
| **协议测试** | `tests/test_protocol.py` | 协议命令测试 |
| **性能测试** | `tests/test_performance.py` | 性能测试 |
| **Fixture** | `tests/conftest.py` | 定义共享的测试资源和依赖注入、冒烟测试 |
| **配置** | `pytest.ini` | pytest的配置文件 |
| **CI/CD** | `.github/workflows/` | GitHub Actions自动化配置 |

## 模块详解

### 1. 固件模拟模块 (firmware.py)

#### 设计思路

```
SSDFirmware类模拟真实的SSD固件，包含：

1. 状态机管理
   - IDLE: 初始状态
   - INITIALIZING: 初始化中
   - READY: 就绪状态
   - ERROR: 错误状态

2. 核心功能
   - initialize(simulate_failure=False): 固件初始化，支持参数控制失败
   - read(lba, size): 从指定LBA读取数据
   - write(lba, data): 向指定LBA写入数据
   - get_smart_data(): 获取硬盘健康信息
   - power_management(mode): 电源管理

3. 统计信息
   - read_count: 读取次数统计
   - write_count: 写入次数统计
   - used_gb: 已使用容量
```

### 2. 协议模拟模块 (protocol.py)

#### 设计思路

```
NVMeProtocol类模拟NVMe协议命令处理：

1. Identify命令
   - 返回设备信息（厂商ID、型号、序列号、容量等）
   - 模拟Identify数据结构（精简版）

2. Read/Write命令
   - 接收namespace_id, lba, size等参数
   - 返回命令执行结果

3. Flush命令
   - 模拟数据刷新到非易失性存储

SATAProtocol类模拟SATA协议命令：
- Identify Device: 获取设备信息
- Read DMA: DMA方式读取
```

### 3. 工具函数模块 (utils.py)

#### 设计思路与使用场景

```
utils.py提供通用的辅助功能：

1. retry装饰器
   - 用途：自动重试可能失败的操作
   - 使用场景：固件初始化失败时重试

2. generate_random_data
   - 用途：生成指定大小的随机数据(种子伪随机)
   - 使用场景：测试写入操作时需要随机数据

3. calculate_checksum
   - 用途：计算数据的校验和
   - 使用场景：验证读写数据的一致性
```

### 4. Fixture设计 (conftest.py)

#### 设计思路

```
conftest.py定义共享的测试资源：

1. smoke_check fixture (autouse=True)
   - 自动执行的冒烟测试
   - 验证基础环境是否正常
   - 失败则停止所有测试

2. firmware fixture
   - 提供基础的固件实例
   - 每个测试函数独立

3. initialized_firmware fixture
   - 提供已初始化的固件实例
   - 依赖firmware fixture

4. nvme_protocol / sata_protocol fixtures
   - 提供协议实例
```

## CI/CD工作流

GitHub Actions：

1. 创建工作流文件
   .github/workflows/test.yml

2. 配置触发条件
   - push到main分支
   - pull request创建

3. 配置执行步骤
   - 检出代码
   - 设置Python环境
   - 安装依赖
   - 运行测试
   - 上传报告

4. 代码控制：可配置强制PR,测试通过才能合并代码


## git钩子函数

git commit → pre-commit 钩子触发 → 检查通过？→ 是：创建提交 → 否：阻止提交，显示错误 → 开发者修复 → 重新 commit

创建.pre-commit-config.yaml：
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.14

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=100']
```
执行：
```bash
pip install pre-commit
pre-commit install   # 安装钩子到 .git/hooks/
# 之后每次 git commit 自动触发

# 查看当前配置中哪些有更新
pre-commit autoupdate --dry-run

# 自动查询所有 repo 的最新版本并更新配置
pre-commit autoupdate
```
