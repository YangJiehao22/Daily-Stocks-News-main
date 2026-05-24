# Daily NVIDIA AI Server Supply Chain News

该仓库自动每天收集关于英伟达AI服务器供应链的新闻,特别是在大陆有交易的上市公司的相关资讯,并将汇总的20条新闻发送到您的个人邮箱。

## 📋 功能特性

- **自动化收集**: 每日自动从多个新闻源收集NVIDIA AI服务器相关新闻
- **智能过滤**: 只收集与以下相关的内容:
  - NVIDIA、GPU、AI、芯片等关键词
  - 在大陆上市的相关供应链公司
- **邮件推送**: 每日自动将最新20条新闻发送到您的邮箱
- **新闻存档**: 自动保存每日新闻到 `archive/` 目录

## 🏢 覆盖的上市公司

### 半导体与芯片
- 中芯国际 (SMIC) - 集成电路制造
- 安集微电子 (AMEC) - 半导体材料
- 晶方科技 - 晶圆级封装
- 长川科技 - 测试设备
- 华峰测控 - 半导体测试
- 兆易创新 (GigaDevice) - 微控制器与存储
- 韦尔股份 (Wylie) - 半导体元器件

### 散热与冷却
- 九州风神 (DEEPCOOL) - 散热解决方案
- 法拉电子 - 电容器

### 封装与材料
- 生益科技 - PCB材料
- 金安国纪 - PCB相关

### 晶圆
- 上海新昇 - 半导体晶圆

### AI计算平台
- 浪潮信息 (INSPUR) - 云服务器
- 中科曙光 (Sugon) - 高性能计算
- 商汤科技 (SenseTime) - AI平台

## 🚀 快速开始

### 1. 配置GitHub Secrets

在您的仓库设置中添加以下 Secrets:

| Secret 名称 | 描述 | 示例 |
|-----------|------|------|
| `RECIPIENT_EMAIL` | 接收新闻的邮箱地址 | `your-email@example.com` |
| `SENDER_EMAIL` | 发送邮件的邮箱地址 | `your-gmail@gmail.com` |
| `SENDER_PASSWORD` | 发送邮件账户的密码/应用密码 | (Gmail使用应用密码) |
| `SMTP_SERVER` | SMTP服务器地址 | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP端口 | `587` |

### 2. 配置SMTP (以Gmail为例)

**使用Gmail时的步骤:**
1. 启用两步验证: https://myaccount.google.com/security
2. 生成应用密码: https://myaccount.google.com/apppasswords
3. 使用应用密码作为 `SENDER_PASSWORD`
4. SMTP服务器: `smtp.gmail.com`
5. 端口: `587`

### 3. 本地测试

```bash
# 安装依赖
pip install -r requirements.txt

# 运行新闻获取
python news_fetcher.py

# 运行邮件发送
export RECIPIENT_EMAIL="your-email@example.com"
export SENDER_EMAIL="your-gmail@gmail.com"
export SENDER_PASSWORD="your-app-password"
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"

python email_sender.py
```

## 📅 工作流程

工作流自动运行时间表:
- **默认**: 每天 UTC 09:00 (北京时间 17:00)
- **自定义**: 可在 `.github/workflows/daily-news.yml` 中修改 `cron` 表达式

## 🔧 自定义配置

### 修改运行时间

编辑 `.github/workflows/daily-news.yml`:

```yaml
schedule:
  - cron: '0 9 * * *'  # UTC时间,格式: 分 小时 日 月 星期
```

常用示例:
- 每天北京时间下午6点: `cron: '0 10 * * *'` (UTC+8时)
- 每天早上9点北京时间: `cron: '0 1 * * *'` (UTC+8时)

### 添加新闻源

编辑 `news_fetcher.py` 中的 `NEWS_SOURCES` 列表,添加RSS源:

```python
NEWS_SOURCES = [
    {
        "name": "新闻源名称",
        "url": "RSS_FEED_URL",
        "type": "rss"
    },
]
```

### 修改过滤规则

编辑 `news_fetcher.py` 中的:
- `CHINA_STOCKS_KEYWORDS`: 添加/删除要跟踪的公司
- `is_relevant_news()`: 自定义新闻相关性判断逻辑

## 📊 输出文件

- `daily_news.json`: 当日收集的新闻JSON文件
- `archive/news-YYYY-MM-DD.json`: 历史新闻存档

## ��� 邮件示例

邮件包含:
- 发送日期时间
- 新闻条数统计
- 每条新闻的标题、来源、摘要和链接
- 快速跳转链接

## 🛠️ 技术栈

- Python 3.11
- feedparser - RSS解析
- requests - HTTP请求
- GitHub Actions - 工作流自动化

## ⚠️ 注意事项

1. **密码安全**: 永远不要在代码中暴露SMTP密码,使用GitHub Secrets
2. **应用密码**: Gmail账户建议使用应用密码而不是账户密码
3. **速率限制**: 某些RSS源可能有访问限制
4. **邮件配额**: 确保您的SMTP服务提供商支持日常邮件发送

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目!

## 📝 许可证

MIT License

---

**📞 需要帮助?**

- 检查GitHub Actions日志: 在Actions选项卡中查看工作流运行日志
- 确认所有Secrets都已正确设置
- 测试SMTP连接设置是否正确
