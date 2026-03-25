# Polymarket BTC 15分钟套利机器人 - 使用指南

## 一、项目简介

本项目是一个针对 Polymarket 平台上 **BTC 15分钟涨跌预测市场** 的自动套利机器人。

### 套利原理

在 Polymarket 的二元市场中，每个市场有两个结果：UP（涨）和 DOWN（跌）。市场结算时，赢的一方每股支付 $1.00，输的一方归零。

如果在某一时刻：
- 买入 UP 的价格为 $0.48
- 买入 DOWN 的价格为 $0.50
- **总成本 = $0.98 < $1.00**

无论 BTC 涨还是跌，赢的一方结算拿回 $1.00，锁定 **$0.02/股** 的无风险利润。

### 工作流程

```
自动发现市场 -> 获取价格/订单簿 -> 判断套利机会 -> 批量下单 -> 等待结算 -> 寻找下一个市场
```

1. 爬取 Polymarket 页面，找到当前活跃的 `btc-updown-15m-*` 市场
2. 通过 CLOB API 获取 UP/DOWN 最新成交价和卖单深度
3. 检查总成本是否低于阈值，同时验证流动性和价差
4. 预签名后批量提交 UP 和 DOWN 买单
5. 市场关闭后自动寻找下一个 15 分钟市场，循环运行

---

## 二、项目结构

```
polymarket-arb/
├── .env.example          # 环境变量模板
├── .gitignore
├── README.md
├── requirements.txt      # Python 依赖
├── run.sh                # 一键启动脚本
├── docs/
│   └── GUIDE.md          # 本文档
└── src/
    ├── __init__.py
    ├── config.py          # 配置加载（从 .env 读取）
    ├── api_key_util.py    # 从私钥派生 API 凭证
    ├── market_lookup.py   # 从 Polymarket 页面解析市场/代币 ID
    ├── trading_client.py  # 交易客户端（下单、查余额、查持仓）
    └── strategy_bot.py    # 主程序：套利策略 + 监控循环
```

---

## 三、环境准备

### 3.1 系统要求

- Python 3.8+
- pip
- 网络可访问 Polymarket API（https://clob.polymarket.com）

### 3.2 安装步骤

```bash
# 克隆项目
git clone https://github.com/JLBcode-code/polymarket-arb.git
cd polymarket-arb

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# .\venv\Scripts\activate       # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3.3 依赖说明

| 依赖包 | 用途 |
|---|---|
| `py-clob-client` | Polymarket CLOB API 官方客户端 |
| `httpx` | HTTP 请求，用于市场发现和价格获取 |
| `python-dotenv` | 从 `.env` 文件加载环境变量 |

---

## 四、配置说明

将 `.env.example` 复制为 `.env`，然后根据需要填写：

```bash
cp .env.example .env
```

### 4.1 必填配置

| 变量 | 说明 | 示例 |
|---|---|---|
| `POLYMARKET_PRIVATE_KEY` | 钱包私钥，用于签名交易 | `0xabc123...` |
| `POLYMARKET_FUNDER` | 资金方钱包地址，用于查询持仓 | `0xdef456...` |
| `POLYMARKET_SIGNATURE_TYPE` | 签名类型：`1`=Magic/Email 账户，`2`=浏览器钱包 | `2` |

> **安全提醒**：私钥极其敏感，切勿泄露、提交到 Git 或分享给他人。

### 4.2 策略配置

| 变量 | 默认值 | 说明 |
|---|---|---|
| `TARGET_PAIR_COST` | `0.99` | UP+DOWN 总成本低于此值才触发套利（越低越保守） |
| `ORDER_SIZE` | `50` | 每边买入的股数 |
| `DRY_RUN` | `false` | `true`=模拟模式（不实际下单），`false`=真实交易 |
| `MAX_TRADES_PER_MARKET` | `0` | 每个 15 分钟市场最大交易次数，`0`=不限制 |
| `MIN_TIME_REMAINING_MINUTES` | `0` | 市场剩余时间低于此值（分钟）则跳过交易 |

### 4.3 可选配置

| 变量 | 默认值 | 说明 |
|---|---|---|
| `POLYMARKET_MARKET_SLUG` | 空 | 手动指定市场 slug，留空则自动发现 |
| `COOLDOWN_SECONDS` | `10` | 每次扫描间的冷却时间（秒） |
| `VERBOSE` | `false` | 是否输出详细日志 |
| `YES_BUY_THRESHOLD` | `0.45` | UP 价格阈值 |
| `NO_BUY_THRESHOLD` | `0.45` | DOWN 价格阈值 |

---

## 五、运行方式

### 5.1 生成 API 凭证（首次）

首次使用时，先填写 `POLYMARKET_PRIVATE_KEY`，然后运行：

```bash
python src/api_key_util.py
```

会输出 API Key、Secret、Passphrase，可选择保存到 `.env` 中（非必须，机器人启动时会自动派生）。

### 5.2 启动机器人

```bash
# 方式一：使用启动脚本（推荐）
./run.sh

# 方式二：直接运行
python -m src.strategy_bot

# 方式三
python src/strategy_bot.py
```

### 5.3 建议的首次运行流程

1. 设置 `DRY_RUN=true`，先模拟观察
2. 确认能正常发现市场、获取价格后，设为 `false` 进行真实交易
3. 初始建议设置 `ORDER_SIZE=5`、`MAX_TRADES_PER_MARKET=1`，小额试水

### 5.4 停止机器人

按 `Ctrl+C` 即可安全停止，机器人会输出最终统计摘要。

---

## 六、运行日志说明

机器人运行时会输出以下关键信息：

| 日志标记 | 含义 |
|---|---|
| `正在搜索当前活跃的 BTC 15分钟市场...` | 自动发现市场中 |
| `找到市场: btc-updown-15m-XXXXXX` | 成功定位到活跃市场 |
| `无套利机会: UP=$X.XX + DOWN=$X.XX = $X.XX` | 当前无利可图 |
| `检测到套利机会` | 发现套利机会，显示详细的价格和利润信息 |
| `套利执行成功` | 下单成功 |
| `市场已关闭 - 最终总结` | 当前市场结束，输出本场统计 |
| `正在搜索下一个 BTC 15分钟市场...` | 自动轮转到下一场 |

---

## 七、风险提示

1. **套利空间极小**：通常利润 < 1%，需关注交易手续费对利润的侵蚀
2. **流动性风险**：订单簿深度不足时可能无法以预期价格成交
3. **执行风险**：两笔订单之间存在时间差，价格可能变动
4. **网络风险**：API 请求延迟或失败可能导致单边成交
5. **资金安全**：请确保私钥安全存储，仅在可信环境运行本程序
6. **仅供学习研究**：风险自负，不构成投资建议
