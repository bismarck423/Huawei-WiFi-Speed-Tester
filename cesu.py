import requests
import time
import xml.etree.ElementTree as ET
import speedtest
from tabulate import tabulate
import matplotlib.pyplot as plt

# --- 配置区域 ---
BASE_URL = "your_http"
# 切换频段后等待网络稳定的时间（秒），如果信号不好建议适当延长
WAIT_TIME = 20

# 华为常见单频段 Hex 代码映射表
# 注意：不同型号或固件版本可能略有差异。如果某个频段切换失败，可能需要抓包确认。
BAND_HEX_MAP = {
    "Auto (自动)": "3FFFFFFF",  # 这是一个常见的全频段组合掩码
    "B1 (2100)": "1",
    "B3 (1800)": "4",
    "B5 (850)": "10",
    "B7 (2600)": "40",
    "B8 (900)": "80",
    # TDD 频段 (移动/联通/电信部分)
    "B34 (2000)": "200000000",
    "B38 (2600)": "4000000000",
    "B39 (1900)": "8000000000",
    "B40 (2300)": "10000000000",
    "B41 (2500)": "20000000000",
}
# 你可以在这里注释掉不想测试的频段，或者调整顺序
BANDS_TO_TEST = [
    "B1 (2100)", "B3 (1800)", "B5 (850)", "B8 (900)",
    "B39 (1900)", "B40 (2300)", "B41 (2500)",
    "Auto (自动)"
]


# --- 华为 API 功能函数 ---
def get_tokens():
    """获取华为 API 的鉴权 Token"""
    try:
        r = requests.get(f"{BASE_URL}/api/webserver/SesTokInfo", timeout=5)
        root = ET.fromstring(r.content)
        return root.find('SesInfo').text, root.find('TokInfo').text
    except Exception as e:
        print(f"获取 Token 失败: {e}，请检查设备是否连接。")
        return None, None


def switch_lte_band(band_name, band_hex):
    """发送切换频段指令"""
    print(f"\n[切换] 正在尝试切换到频段: 【{band_name}】...")
    session, token = get_tokens()
    if not session or not token:
        return False

    headers = {
        "Cookie": session,
        "__RequestVerificationToken": token,
        "Content-Type": "application/xml"
    }

    # 核心 XML 数据体
    xml_data = f"""<request>
        <NetworkMode>03</NetworkMode> 
        <NetworkBand>3FFFFFFF</NetworkBand>
        <LTEBand>{band_hex}</LTEBand>
    </request>"""
    # 注: NetworkMode 03 通常指只用 4G LTE，不同设备可能不同，不行试改 00

    try:
        response = requests.post(f"{BASE_URL}/api/net/net-mode", data=xml_data, headers=headers, timeout=10)
        if "OK" in response.text or response.status_code == 200:
            print(f"[成功] 切换指令已发送。等待 {WAIT_TIME} 秒让设备重新搜索网络...")
            time.sleep(WAIT_TIME)
            return True
        else:
            print(f"[失败] 切换失败，设备返回: {response.text}")
            return False
    except Exception as e:
        print(f"[出错] 发送指令时出错: {e}")
        return False


# --- 测速功能函数 ---
def run_speedtest_safe(band_name):
    """执行测速，包含错误处理（防止无信号时卡死）"""
    print(f"[测速] 开始测试 【{band_name}】 的速度，请耐心等待...")
    try:
        st = speedtest.Speedtest()
        # 增加一个简单的连接检查
        st.get_best_server()

        print(" -> 找到服务器，正在下载测试...")
        dl_speed = st.download() / 1_000_000  # Mbps
        print(" -> 正在上传测试...")
        ul_speed = st.upload() / 1_000_000  # Mbps
        ping = st.results.ping
        print(f"[完成] 下行: {dl_speed:.2f} M | 上行: {ul_speed:.2f} M | Ping: {ping} ms")
        return {"band": band_name, "dl": dl_speed, "ul": ul_speed, "ping": ping, "status": "Success"}

    except speedtest.ConfigRetrievalError:
        print("[失败] 无法连接到测速服务器。当前频段可能无信号或无法上网。")
        return {"band": band_name, "dl": 0, "ul": 0, "ping": 999, "status": "No Signal/Net"}
    except Exception as e:
        print(f"[出错] 测速过程中发生未知错误: {e}")
        return {"band": band_name, "dl": 0, "ul": 0, "ping": 999, "status": "Error"}


# --- 可视化功能函数 ---
def visualize_results(results):
    """生成表格和图表"""
    if not results:
        print("没有有效的数据可展示。")
        return

    # 1. 打印表格
    print("\n" + "=" * 30 + " 最终测试报告 " + "=" * 30)
    table_data = []
    for r in results:
        table_data.append([
            r['band'],
            f"{r['dl']:.2f}" if r['status'] == 'Success' else '-',
            f"{r['ul']:.2f}" if r['status'] == 'Success' else '-',
            f"{r['ping']:.0f}" if r['status'] == 'Success' else '-',
            r['status']
        ])

    headers = ["频段", "下载(Mbps)", "上传(Mbps)", "Ping(ms)", "状态"]
    print(tabulate(table_data, headers=headers, tablefmt="grid", stralign="center"))
    print("=" * 72)
    print("注: Ping 值越低越稳定；下载/上传越高越快。")

    # 2. 生成图表 (仅展示成功的测试)
    success_results = [r for r in results if r['status'] == 'Success']
    if not success_results:
        print("没有成功的测速数据，无法绘图。")
        return

    bands = [r['band'] for r in success_results]
    dls = [r['dl'] for r in success_results]
    uls = [r['ul'] for r in success_results]

    x = range(len(bands))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width / 2, dls, width, label='下载 (Mbps)', color='#1f77b4')
    rects2 = ax.bar(x + width / 2, uls, width, label='上传 (Mbps)', color='#ff7f0e')

    ax.set_ylabel('速度 (Mbps)')
    ax.set_title('不同频段网速对比测试结果')
    ax.set_xticks(x)
    ax.set_xticklabels(bands, rotation=45, ha="right")
    ax.legend()

    ax.bar_label(rects1, padding=3, fmt='%.1f')
    ax.bar_label(rects2, padding=3, fmt='%.1f')

    fig.tight_layout()
    print("\n正在生成对比图表窗口...")
    plt.show()


# --- 主程序 ---
if __name__ == "__main__":
    print("=== 华为随身 WiFi 全自动频段测速工具启动 ===")
    print(f"即将测试的频段列表: {', '.join(BANDS_TO_TEST)}")
    print("请确保电脑已连接到随身 WiFi，且期间不要断开。")
    input("按回车键开始测试...")

    final_results = []

    for band_name in BANDS_TO_TEST:
        band_hex = BAND_HEX_MAP.get(band_name)
        if not band_hex:
            print(f"跳过未知频段: {band_name}")
            continue

        # 1. 切换频段
        if switch_lte_band(band_name, band_hex):
            # 2. 如果切换命令成功，执行测速
            # 稍微再多等几秒确保网络完全可用
            time.sleep(5)
            result = run_speedtest_safe(band_name)
            final_results.append(result)
        else:
            # 切换失败也要记录
            final_results.append({"band": band_name, "dl": 0, "ul": 0, "ping": 0, "status": "Switch Failed"})
            print("由于切换失败，跳过本轮测速。")

    # 所有循环结束后，进行可视化
    visualize_results(final_results)