<div align="center">
  <img src="cvm.jpg" alt="CVM-colorBot Logo" width="200"/>
  
  # CVM-colorBot
  
  [![Discord](https://img.shields.io/badge/Discord-加入服务器-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/pJ8JkSBnMB)
</div>

CVM-colorBot 是一款基于计算机视觉的鼠标瞄准系统，使用 HSV 颜色检测。支持多种视频采集源（NDI、UDP、采集卡、GStreamer、MSS）与多种鼠标控制后端（Serial/MAKCU、Arduino、SendInput、Net、KmboxA、MakV2、DHZ、Ferrum）。可自定义灵敏度、平滑度、FOV 与反烟雾过滤，适用于双 PC 或单 PC 的精确瞄准工作流程。

## 功能特性

### 核心模块
- **Aimbot（自瞄）**：智能瞄准系统，支持多种模式（头部/身体/最近目标）
- **Triggerbot（扳机）**：自动扳机，支持连发和冷却管理
- **RCS（后坐力控制系统）**：自动后坐力补偿
- **反烟雾检测**：高级过滤功能，避免瞄准烟雾中的目标

### 视频采集支持

多种采集后端，适配双 PC 或单 PC 方案：

| 后端 | 说明 | 典型用途 |
|--------|-------------|-------------|
| **NDI** | 网络设备接口，通过局域网从 NDI 源（如 OBS、NDI Tools）低延迟获取视频。 | 双 PC：游戏 PC 发送 NDI，瞄准 PC 接收。 |
| **UDP** | 兼容 OBS 的 UDP 视频流，可配置 IP 与端口。 | 双 PC：OBS 或其他编码器发送 UDP 流。 |
| **采集卡** | 通过 DirectShow/Media Foundation 从采集卡直接采集。 | 双 PC：游戏 PC HDMI 接入瞄准 PC 的采集卡。 |
| **采集卡 (GStreamer)** | 可选采集卡后端，需安装 [GStreamer](docs/shared-guides/zh-CN/GStreamer-install.md)。 | DirectShow/Media Foundation 不适用时使用。 |
| **MSS** | 内置屏幕采集（Multiple Screen Shot），无需额外硬件。 | 单 PC 或测试；采集本机画面。 |

- **统一接口**：一个采集服务可在 NDI、UDP、采集卡、GStreamer、MSS 之间切换。
- **分辨率与 FPS**：在支持的后端上可配置。

### 硬件集成

鼠标控制支持多种后端，请在 Config 标签页选择「Mouse API」。

| 后端 | 连接方式 | 备注 |
|--------|------------|--------|
| **Serial** | USB 串口（MAKCU 或兼容适配器） | MAKCU (1A86:55D3)、CH343、CH340、CH347、CP2102，波特率最高 4 Mbps。 |
| **Arduino** | USB 串口（Arduino 兼容） | 可配置端口与波特率（默认 115200）。 |
| **SendInput** | Windows API | 无需额外硬件，使用 Windows SendInput 控制鼠标/键盘。 |
| **Net** | 网络（TCP + DLL） | 通过网络远程鼠标控制，需 KMNet DLL 与网络端设备。 |
| **KmboxA** | USB（VID/PID） | KmboxA 设备，在配置中设置 VID/PID。 |
| **MakV2** / **MakV2Binary** | USB 串口 | MakV2 系列，可配置端口与波特率（如 4Mbps）。 |
| **DHZ** | 网络（IP + 端口） | DHZ 设备经网络连接，IP、端口及可选随机偏移。 |
| **Ferrum** | 串口（设备路径） | Ferrum 设备，串口连接。 |

- **自动连接**：可选在启动时连接所选 Mouse API。
- **按键遮罩与移动锁定**：在 Serial、MakV2、MakV2Binary 等后端上支持（视后端而定）。
- **键盘输出**：Serial、SendInput、Net、KmboxA、MakV2、MakV2Binary、DHZ、Ferrum 支持（具体以界面为准）。

### 自定义选项
- 可调节的灵敏度和平滑度
- 可配置的 FOV（视野）设置
- 精细的显示和叠加控制
- 实时性能监控

## 系统要求

### 硬件
- **MAKCU USB 设备**（或兼容的串口适配器：CH343、CH340、CH347、CP2102）
- Windows 10/11
- USB 端口用于连接 MAKCU

### 软件
- **Python 3.11 ～ 3.13.x**（例如 3.11.x、3.12.x、3.13.7）。已测试至 3.13.7；**不支持 Python 3.14**。（依賴如 NumPy 2.2.x 官方支援 3.10～3.13，建議使用 3.11+。）
- Windows 操作系统（10/11）

## 安装

### 方法 1：快速安装（推荐）

1. **克隆仓库**
   ```bash
   git clone https://github.com/asenyeroao-ct/CVM-colorBot.git
   cd CVM-colorBot
   ```

2. **运行安装脚本**
   ```bash
   setup.bat
   ```
   这将自动：
   - 检查 Python 安装
   - 创建虚拟环境
   - 安装所有依赖项

3. **运行应用程序**
   ```bash
   run.bat
   ```

### 方法 2：手动安装

1. **克隆仓库**
   ```bash
   git clone https://github.com/asenyeroao-ct/CVM-colorBot.git
   cd CVM-colorBot
   ```

2. **创建虚拟环境**（推荐）
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **安装依赖项**
   ```bash
   pip install -r requirements.txt
   ```

4. **运行应用程序**
   ```bash
   python main.py
   ```
   
   或使用提供的批处理文件：
   ```bash
   run.bat
   ```

## 使用说明

### 初始设置

1. **连接 MAKCU 设备**
   - 插入您的 MAKCU USB 设备
   - 应用程序将自动检测并连接

2. **配置视频源**
   - 选择采集方式：NDI、UDP、采集卡、GStreamer 或 MSS
   - 根据所选方式配置连接参数
   - 点击 "CONNECT" 建立连接

3. **调整设置**
   - 浏览各个标签页：General、Aimbot、Sec Aimbot、Trigger、RCS、Config
   - 配置灵敏度、平滑度、FOV 和其他参数
   - 设置会自动保存到 `config.json`

### 配置标签页

- **General（常规）**：采集控制、灵敏度、操作模式、目标颜色
- **Aimbot（自瞄）**：主要瞄准设置、灵敏度、FOV、偏移量、瞄准模式
- **Sec Aimbot（次要自瞄）**：次要自瞄配置
- **Trigger（扳机）**：扳机设置、延迟、保持时间、连发控制
- **RCS**：后坐力控制系统参数
- **Config（配置）**：保存/加载配置档

## 项目结构

```
CVM-colorBot/
├── main.py                 # 主应用程序入口
├── requirements.txt        # Python 依赖
├── config.json            # 应用配置
├── run.bat                # Windows 启动脚本
├── setup.bat              # 安装脚本
├── src/
│   ├── ui.py              # GUI 界面（CustomTkinter）
│   ├── aim_system/        # 瞄准系统模块
│   │   ├── normal.py      # 普通模式自瞄
│   │   ├── silent.py      # 静默模式自瞄
│   │   ├── Triggerbot.py  # 扳机逻辑
│   │   ├── RCS.py         # 后坐力控制系统
│   │   └── anti_smoke_detector.py
│   ├── capture/           # 视频采集模块
│   │   ├── capture_service.py   # 统一采集服务
│   │   ├── ndi.py               # NDI 采集
│   │   ├── OBS_UDP.py           # UDP 流（兼容 OBS）
│   │   ├── CaptureCard.py       # 采集卡（DirectShow/Media Foundation）
│   │   ├── CaptureCardGStreamer.py  # 采集卡（GStreamer，可选）
│   │   └── mss_capture.py       # MSS 屏幕采集
│   └── utils/             # 工具模块
│       ├── config.py      # 配置管理
│       ├── detection.py   # HSV 颜色检测
│       ├── mouse_input.py
│       └── mouse/         # 鼠标控制后端（Serial、Arduino、SendInput、Net、KmboxA、MakV2、DHZ、Ferrum）
├── configs/               # 配置档
└── themes/                # UI 主题
```

## 配置

配置存储在 `config.json` 中，可以通过 GUI 或手动编辑进行管理。主要设置包括：

- **采集设置**：视频源、分辨率、FPS
- **自瞄设置**：灵敏度、平滑度、FOV、瞄准模式
- **扳机设置**：延迟、保持时间、连发次数、冷却时间
- **RCS 设置**：拉枪速度、激活延迟、快速点击阈值
- **显示设置**：OpenCV 窗口、叠加元素

## 支持的设备

### 鼠标 / 控制后端
- **Serial**：MAKCU (1A86:55D3)、CH343 (1A86:5523)、CH340 (1A86:7523)、CH347 (1A86:5740)、CP2102 (10C4:EA60)
- **Arduino**：Arduino 兼容板通过 USB 串口
- **SendInput**：Windows 内置（无需设备）
- **Net**：配合 KMNet DLL 的网络设备
- **KmboxA**：KmboxA USB 设备（可配置 VID/PID）
- **MakV2 / MakV2Binary**：MakV2 系列通过串口
- **DHZ**：DHZ 设备经网络（IP/端口）
- **Ferrum**：Ferrum 设备经串口

### 视频采集源
- **NDI**：网络上任意 NDI 源（如 NDI Tools、带 NDI 输出的 OBS）
- **UDP**：任意 UDP 视频流（如 OBS UDP 推流）
- **采集卡**：兼容 DirectShow/Media Foundation 的采集卡
- **采集卡 (GStreamer)**：同一硬件配合 GStreamer 管线（可选）
- **MSS**：本机屏幕采集（无需采集卡）

## 技术细节

- **颜色检测**：基于 HSV 颜色空间的目标识别
- **鼠标控制**：支持多种后端（Serial/MAKCU、SendInput、Net 等），Serial 下可经 MAKCU 等设备高速串口通信
- **视频处理**：使用 OpenCV 进行实时帧处理
- **GUI 框架**：使用 CustomTkinter 构建现代化、可自定义的界面
- **多线程**：异步处理以确保流畅性能

## 许可证

版权所有 (c) 2025 asenyeroao-ct。保留所有权利。

本项目采用自定义许可证。详情请参阅 [LICENSE](LICENSE) 文件。

**要点：**
- 允许个人、非商业用途
- 允许修改和重新分发，但需正确署名
- 未经书面许可禁止商业用途
- 所有分发版本必须标注原作者 **asenyeroao-ct**

## 免责声明

本項目僅供學習和測試用途，本程式僅供雙機位使用。對於因使用本程式而導致的任何遊戲帳號封禁、處罰或其他後果，本人概不負責，不會提供任何賠償。請自行承擔使用風險，並了解可能的後果。用戶需自行確保遵守相關法律法規以及使用本工具的任何軟件或遊戲的服務條款。

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 支持

- **Discord**：加入我们的 [Discord 服务器](https://discord.gg/pJ8JkSBnMB) 获取社区支持、讨论和更新
- **GitHub Issues**：如需报告错误、提问或功能请求，请在 [GitHub](https://github.com/asenyeroao-ct/CVM-colorBot/issues) 上提交 issue

