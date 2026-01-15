```markdown
# 🚀 Huawei-WiFi3-Speed-Tester

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Network](https://img.shields.io/badge/Focus-Network%20Security-red.svg)

**Huawei-WiFi3-Speed-Tester** 是一个专为华为随身 WiFi 3 开发的自动化频段扫描与网速分析工具。它通过调用设备后台 API，实现自动切换 LTE 频段并进行多维度的网络质量测试。

## 🌟 核心功能
- **自动化切换**: 自动遍历 B1/B3/B5/B8/B39/B40/B41 等主流 LTE 频段。
- **多维度测试**: 集成 `speedtest-cli`，获取下载速度、上传速度及 Ping 延迟。
- **数据可视化**: 自动生成格式化的终端报表（Tabulate）及对比柱状图（Matplotlib）。
- **健壮性**: 内置重试机制与网络稳定性等待时间，确保测试数据真实有效。

## 📊 测试报表展示
测试完成后，你将获得如下直观的数据对比：

| 频段 | 下载 (Mbps) | 上传 (Mbps) | Ping (ms) | 状态 |
| :---: | :---: | :---: | :---: | :---: |
| B1 (2100) | 45.20 | 12.50 | 25 | Success |
| B3 (1800) | 68.95 | 20.10 | 18 | Success |
| ... | ... | ... | ... | ... |

## 🛠️ 快速上手

### 1. 环境准备
确保你的电脑已连接到华为随身 WiFi，并安装了 Python 3。

### 2. 安装依赖
```bash
pip install -r requirements.txt

```

### 3. 运行配置

编辑 `cesu.py` 中的 `BASE_URL`：

```python
BASE_URL = "[http://192.168.8.1](http://192.168.8.1)" # 请根据你设备的实际网关地址修改

```

### 4. 启动执行

```bash
python cesu.py

```

## 📂 项目结构

* `cesu.py`: 主程序源码，包含 API 交互逻辑与测速算法。
* `requirements.txt`: 项目所需的第三方库清单。
* `.gitignore`: 忽略配置文件与虚拟环境，保持仓库整洁。

## ⚠️ 免责声明 (Disclaimer)

1. 本工具仅用于**个人网络环境优化**与**通信协议学习**。
2. 频繁切换频段可能触发基站频率限制或导致设备发热重启，请谨慎使用。
3. 请在法律法规允许的范围内使用本工具，作者不对任何误用导致的后果负责。

## 🤝 贡献与交流

如果你发现了新的 API 接口或有更好的优化建议，欢迎提交 **Pull Request** 或 **Issue**。

---

⭐ 如果这个工具帮到了你，请给一个 Star！

```
