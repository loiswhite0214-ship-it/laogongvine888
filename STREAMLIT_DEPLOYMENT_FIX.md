# Streamlit Cloud 部署修复指南

## 问题描述
Streamlit Cloud 部署失败，主要问题：
1. Python 3.13.6 缺少 `distutils` 模块
2. `pandas-ta==0.3.14b0` 在 PyPI 上不可用
3. numpy/pandas 需要从源码编译但失败

## 解决方案

### 方案A：强制使用Python 3.11（推荐）
如果 Streamlit Cloud 仍然忽略 `runtime.txt`，请手动在 Streamlit Cloud 设置中：
1. 进入应用设置
2. 在 "Python version" 中选择 **Python 3.11**
3. 使用当前的 `requirements.txt`

### 方案B：兼容Python 3.13
如果必须使用 Python 3.13，请重命名文件：
```bash
# 重命名文件以使用Python 3.13兼容版本
mv requirements.txt requirements-py311.txt
mv requirements-py313.txt requirements.txt
```

### 方案C：简化依赖（最稳定）
创建一个最小化的 requirements 文件：
```bash
# 创建简化版本
echo "streamlit==1.40.1
ccxt==4.4.48
numpy>=1.26.0
pandas>=2.1.0
git+https://github.com/twopirllc/pandas-ta@main#egg=pandas-ta" > requirements-minimal.txt
mv requirements-minimal.txt requirements.txt
```

## 当前文件状态

### runtime.txt
```
python-3.11.10
```

### requirements.txt（当前）
```
streamlit==1.40.1
ccxt==4.4.48
numpy==1.26.4
pandas==2.1.4
git+https://github.com/twopirllc/pandas-ta@main#egg=pandas-ta
```

### requirements-py313.txt（备用）
```
streamlit==1.40.1
ccxt==4.4.48
numpy>=1.26.0
pandas>=2.1.0
git+https://github.com/twopirllc/pandas-ta@main#egg=pandas-ta
```

## 部署步骤

1. **推送代码到GitHub**
2. **在Streamlit Cloud中重新部署**
3. **如果仍然失败，尝试方案B或C**

## 验证
部署成功后，pandas-ta 导入方式不变：
```python
import pandas_ta as ta
```

## 注意事项
- Git源安装可能较慢，但更稳定
- 如果Git源失败，可以尝试：
  ```
  git+https://github.com/twopirllc/pandas-ta@0.3.14b0#egg=pandas-ta
  ```



