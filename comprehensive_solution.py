import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import time
import importlib.util
import subprocess

class SimpleStockDataTool:
    """简易股票数据工具，提供数据获取、分析和可视化功能"""
    
    def __init__(self):
        # 配置matplotlib以支持中文显示
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        self.yf = None
        self._check_yfinance()
    
    def _check_yfinance(self):
        """检查并尝试导入yfinance库"""
        try:
            import yfinance as yf
            self.yf = yf
            print("成功导入yfinance库")
        except ImportError:
            print("yfinance库未安装。正在尝试安装...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'yfinance'])
                import yfinance as yf
                self.yf = yf
                print("成功安装并导入yfinance库")
            except Exception as e:
                print(f"安装yfinance库失败: {e}")
                self.yf = None
    
    def fetch_data(self, symbol, start_date="2024-01-01", end_date="2024-01-31", retries=3, max_delay=10):
        """尝试从yfinance获取数据，带指数退避重试机制"""
        if self.yf is None:
            print("yfinance库不可用，无法自动获取数据")
            return None
        
        print(f"尝试获取{symbol}的数据（{start_date}至{end_date}）...")
        
        for attempt in range(retries):
            try:
                # 设置请求头以模拟浏览器
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
                }
                
                # 临时修改yfinance的请求头
                original_get = self.yf.utils.get
                def custom_get(*args, **kwargs):
                    if 'headers' not in kwargs:
                        kwargs['headers'] = headers
                    return original_get(*args, **kwargs)
                
                self.yf.utils.get = custom_get
                
                # 获取数据
                data = self.yf.download(
                    symbol,
                    start=start_date,
                    end=end_date,
                    progress=False
                )
                
                # 恢复原始函数
                self.yf.utils.get = original_get
                
                if not data.empty:
                    print(f"成功获取{symbol}的数据，共{len(data)}条记录")
                    return data
                else:
                    print(f"获取到空数据")
                    return None
                    
            except Exception as e:
                print(f"第{attempt+1}次尝试失败: {e}")
                if attempt < retries - 1:
                    # 指数退避策略
                    delay = min(2 ** attempt, max_delay)
                    print(f"等待{delay}秒后重试...")
                    time.sleep(delay)
                else:
                    print(f"所有{retries}次尝试均失败")
                    return None
    
    def manual_import(self, file_path):
        """手动导入CSV格式的股票数据"""
        try:
            if not os.path.exists(file_path):
                print(f"文件{file_path}不存在")
                return None
            
            # 尝试读取CSV文件，假设第一列是日期，使用索引列
            data = pd.read_csv(file_path, index_col=0, parse_dates=True)
            print(f"成功从{file_path}导入数据，共{len(data)}条记录")
            return data
        except Exception as e:
            print(f"导入数据失败: {e}")
            # 尝试使用不同的格式
            try:
                data = pd.read_csv(file_path, parse_dates=['Date'])
                if 'Date' in data.columns:
                    data.set_index('Date', inplace=True)
                print(f"使用备用格式成功导入数据，共{len(data)}条记录")
                return data
            except Exception as e2:
                print(f"使用备用格式导入也失败: {e2}")
                return None
    
    def basic_analysis(self, data):
        """进行基本的数据分析"""
        if data is None or data.empty:
            print("没有数据可供分析")
            return
        
        print("\n=== 基本数据分析 ===")
        
        # 检查是否有必要的列
        required_columns = ['Close', 'Volume']
        available_columns = [col for col in required_columns if col in data.columns]
        
        # 计算基本统计信息
        if 'Close' in available_columns:
            print(f"起始价格: {data['Close'].iloc[0]:.2f}")
            print(f"结束价格: {data['Close'].iloc[-1]:.2f}")
            print(f"最高价: {data['Close'].max():.2f}")
            print(f"最低价: {data['Close'].min():.2f}")
            print(f"平均价格: {data['Close'].mean():.2f}")
            print(f"价格波动: {data['Close'].pct_change().std():.4f}")
            
            # 计算收益率
            returns = data['Close'].pct_change()
            total_return = (data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100
            print(f"总收益率: {total_return:.2f}%")
        
        if 'Volume' in available_columns:
            print(f"总交易量: {data['Volume'].sum():,}")
            print(f"平均日交易量: {data['Volume'].mean():,.2f}")
    
    def plot_price(self, data, symbol="股票"):
        """绘制价格走势图并保存为图片"""
        if data is None or data.empty:
            print("没有数据可供绘图")
            return
        
        try:
            plt.figure(figsize=(10, 6))
            
            # 尝试绘制收盘价
            if 'Close' in data.columns:
                plt.plot(data.index, data['Close'], label='收盘价')
            elif 'Adj Close' in data.columns:
                plt.plot(data.index, data['Adj Close'], label='调整后收盘价')
            
            plt.title(f'{symbol} 价格走势')
            plt.xlabel('日期')
            plt.ylabel('价格')
            plt.grid(True)
            plt.legend()
            
            # 保存图片
            save_path = f'{symbol}_price_chart.png'
            plt.tight_layout()
            plt.savefig(save_path)
            plt.close()
            
            print(f"价格走势图已保存至: {save_path}")
        except Exception as e:
            print(f"绘制价格走势图失败: {e}")


def clean_install_openbb():
    """完全清理并重新安装OpenBB"""
    print("正在准备清理并重新安装OpenBB...")
    
    # 1. 卸载所有现有的OpenBB相关包
    packages_to_uninstall = [
        'openbb', 'openbb-core', 'openbb-equity', 'openbb-yfinance',
        'openbb-charting', 'openbb-crypto', 'openbb-economy',
        'openbb-forecast', 'openbb-index', 'openbb-macro',
        'openbb-news', 'openbb-options', 'openbb-patterns',
        'openbb-politics', 'openbb-portfolio', 'openbb-screener',
        'openbb-sectors', 'openbb-stocks', 'openbb-surveillance',
        'openbb-terms', 'openbb-time', 'openbb-treasury',
        'openbb-vendor', 'openbb-world'
    ]
    
    print("\n1. 卸载现有OpenBB包...")
    for package in packages_to_uninstall:
        try:
            print(f"  正在卸载: {package}")
            subprocess.run([sys.executable, '-m', 'pip', 'uninstall', '-y', package],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"  卸载{package}失败: {e}")
    
    # 2. 安装匹配版本的OpenBB
    print("\n2. 安装匹配版本的OpenBB (4.4.0)...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'openbb[all]==4.4.0'],
                      check=True)
        print("  成功安装openbb[all]==4.4.0")
    except Exception as e:
        print(f"  安装OpenBB失败: {e}")
        return False
    
    print("\nOpenBB清理并重新安装完成！请重启Python环境后使用。")
    return True


if __name__ == "__main__":
    """主函数，提供交互式使用体验"""
    print("=== 简易股票数据工具 ===")
    
    # 创建工具实例
    tool = SimpleStockDataTool()
    
    # 询问用户是否需要获取数据
    action = input("\n请选择操作:\n1. 获取股票数据\n2. 手动导入数据\n3. 清理并重新安装OpenBB\n请输入数字: ")
    
    if action == '1':
        symbol = input("请输入股票代码 (例如: AAPL): ")
        start_date = input("请输入开始日期 (默认为 2024-01-01): ") or "2024-01-01"
        end_date = input("请输入结束日期 (默认为 2024-01-31): ") or "2024-01-31"
        
        data = tool.fetch_data(symbol, start_date, end_date)
        
        if data is not None:
            # 进行分析和绘图
            tool.basic_analysis(data)
            tool.plot_price(data, symbol)
        else:
            print("获取数据失败，您可以尝试手动导入数据")
            
    elif action == '2':
        file_path = input("请输入CSV文件路径: ")
        data = tool.manual_import(file_path)
        
        if data is not None:
            # 进行分析和绘图
            symbol = input("请输入股票代码 (用于图表标题): ") or "股票"
            tool.basic_analysis(data)
            tool.plot_price(data, symbol)
    
    elif action == '3':
        confirm = input("警告: 这将卸载所有现有的OpenBB包并重新安装。是否继续? (y/n): ")
        if confirm.lower() == 'y':
            clean_install_openbb()
    
    else:
        print("无效的选择")
        
    print("\n程序已结束")