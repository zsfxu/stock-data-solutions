import sys
import subprocess
import importlib.util
import time

"""本脚本用于修复和验证OpenBB的安装，解决版本不匹配问题"""


def check_python_version():
    """检查Python版本是否符合OpenBB的要求"""
    major, minor, patch = sys.version_info[:3]
    print(f"Python版本: {major}.{minor}.{patch}")
    
    # OpenBB 4.x 需要Python 3.9或更高版本
    if major < 3 or (major == 3 and minor < 9):
        print("警告: OpenBB 4.x 推荐使用Python 3.9或更高版本")
    
    return major >= 3 and (major == 3 and minor >= 8)  # 至少需要Python 3.8


def check_installed_packages():
    """检查已安装的OpenBB相关包"""
    print("\n检查已安装的OpenBB相关包...")
    
    # 所有可能的OpenBB包
    packages = [
        'openbb', 'openbb-core', 'openbb-equity', 'openbb-yfinance',
        'openbb-charting', 'openbb-crypto'
    ]
    
    installed = {}
    
    # 使用pip show检查每个包
    for pkg in packages:
        try:
            # 获取包信息
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', pkg],
                capture_output=True, text=True, check=False
            )
            
            if result.returncode == 0:
                # 解析版本信息
                version_line = next((line for line in result.stdout.split('\n') 
                                     if line.startswith('Version: ')), None)
                if version_line:
                    version = version_line.split('Version: ')[1].strip()
                    installed[pkg] = version
        except Exception as e:
            print(f"检查{pkg}时出错: {e}")
    
    # 显示已安装的包
    if installed:
        print("已安装的OpenBB相关包:")
        for pkg, ver in installed.items():
            print(f"  - {pkg} ({ver})")
    else:
        print("未检测到已安装的OpenBB包")
    
    # 检查版本一致性
    if 'openbb' in installed:
        core_version = installed.get('openbb-core', '未知')
        print(f"\n版本一致性检查:")
        print(f"  openbb版本: {installed['openbb']}")
        print(f"  openbb-core版本: {core_version}")
        
        # 检查版本是否匹配 (openbb=4.x 应该搭配 openbb-core=1.x)
        if installed['openbb'].startswith('4.') and not core_version.startswith('1.'):
            print("  警告: 版本不匹配! openbb 4.x 应该搭配 openbb-core 1.x")
            return False, installed
    
    return True, installed


def reinstall_openbb():
    """完全卸载并重新安装OpenBB"""
    print("\n准备完全卸载并重新安装OpenBB...")
    
    # 1. 卸载所有OpenBB相关包
    print("1. 卸载所有OpenBB相关包...")
    
    # 定义要卸载的包列表
    openbb_packages = [
        'openbb', 'openbb-core', 'openbb-equity', 'openbb-yfinance',
        'openbb-charting', 'openbb-crypto', 'openbb-economy',
        'openbb-forecast', 'openbb-index', 'openbb-macro',
        'openbb-news', 'openbb-options', 'openbb-patterns',
        'openbb-politics', 'openbb-portfolio', 'openbb-screener',
        'openbb-sectors', 'openbb-stocks', 'openbb-surveillance',
        'openbb-terms', 'openbb-time', 'openbb-treasury',
        'openbb-vendor', 'openbb-world'
    ]
    
    # 执行卸载
    for pkg in openbb_packages:
        try:
            print(f"  正在卸载: {pkg}")
            # 使用-y参数自动确认卸载
            subprocess.run(
                [sys.executable, '-m', 'pip', 'uninstall', '-y', pkg],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except Exception as e:
            print(f"  卸载{pkg}时出错: {e}")
    
    # 2. 安装匹配版本的完整OpenBB包
    print("\n2. 安装匹配版本的OpenBB (4.4.0)...")
    try:
        # 使用--no-cache-dir参数避免使用缓存
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--no-cache-dir', 'openbb[all]==4.4.0'],
            check=True
        )
        print("  成功安装openbb[all]==4.4.0")
        return True
    except Exception as e:
        print(f"  安装OpenBB失败: {e}")
        return False


def verify_openbb_installation():
    """验证OpenBB安装是否成功"""
    print("\n验证OpenBB安装...")
    
    try:
        # 尝试导入openbb
        import openbb
        print(f"成功导入openbb，版本: {getattr(openbb, '__version__', '未知')}")
        
        # 尝试导入obb对象
        from openbb import obb
        print("成功导入obb对象")
        
        # 检查可用的提供商
        try:
            providers = obb.equity.price.historical.providers
            print(f"可用的股票历史数据提供商: {providers}")
        except Exception as e:
            print(f"获取提供商列表时出错: {e}")
            print("注意: 即使出现此错误，OpenBB可能仍然部分可用")
        
        # 提示用户重启Python环境
        print("\n重要提示: 安装完成后，请重启Python环境再使用OpenBB")
        return True
        
    except ImportError as e:
        print(f"导入OpenBB失败: {e}")
        return False
    except Exception as e:
        print(f"验证OpenBB安装时出现意外错误: {e}")
        return False


def main():
    """主函数"""
    print("=== OpenBB安装修复与验证工具 ===")
    
    # 1. 检查Python版本
    if not check_python_version():
        print("错误: Python版本过低，无法运行OpenBB")
        return 1
    
    # 2. 检查已安装的包
    version_ok, installed_packages = check_installed_packages()
    
    # 3. 根据检查结果询问用户是否需要重新安装
    if not version_ok or 'openbb' not in installed_packages:
        prompt = "\n检测到OpenBB版本不匹配或未安装，是否要重新安装? (y/n): "
        choice = input(prompt).lower()
        
        if choice == 'y':
            if reinstall_openbb():
                print("\n重新安装完成！请重启Python环境后使用。")
            else:
                print("\n重新安装失败，请检查错误信息并尝试手动安装。")
                return 1
        else:
            print("\n跳过重新安装。")
    
    # 4. 验证安装
    print("\n请重启Python环境后再运行此脚本来验证安装是否成功！")
    
    # 如果用户选择不重启而直接验证，也可以尝试
    verify_now = input("\n是否要现在尝试验证安装？(注意：这可能不准确，建议先重启Python环境) (y/n): ").lower()
    if verify_now == 'y':
        # 强制重新加载模块
        import importlib
        importlib.reload(sys.modules.get('openbb', None))
        verify_openbb_installation()
    
    print("\n操作完成。")
    return 0


if __name__ == "__main__":
    sys.exit(main())