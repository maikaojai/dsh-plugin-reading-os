# 📚 ReadingOS for DeepSeek Harness

> **个人阅读与认知操作系统 · DeepSeek Harness 官方标准插件**  
> 告别繁琐的邮件导出，直连 macOS 原生图书（Apple Books）本地底层数据库与下载书库，为 DeepSeek 赋予你的专属阅读外脑。

---

## ✨ 核心特性

- **⚡️ 零摩擦本地直连**：无需点击邮件导出，毫秒级读取 macOS Apple Books 本地 SQLite，实时获取全部藏书、划线高亮与阅读进度。
- **📥 电子书库资产盘点**：自动扫描本机的电子书下载目录（如 Z-Library 下载的书籍），计算藏书总量、近 30 天入库率与沉睡积读率（Tsundoku）。
- **🎨 Claude 纸感极简看版**：优雅的 Bento 网格布局，365 天阅读足迹热力图、分类维度权重进度条、精读书目抽屉与双模式（米黄暖纸 / 暗夜深色）切换。
- **🌐 跨书主题网络 (Concept Clusters)**：打破单本书的边界，对跨越数十本书的「放下与破执」、「风险与期权」、「本质与底层」、「规律与辩证」等高频命题进行网状碰撞。
- **✨ 看板与 DeepSeek 原生联动**：在看版的任意划线卡片轻点「✨ 联动 DSH 探讨」，直接在 DeepSeek Harness 中开启新会话并自动填入深度研读 Prompt。
- **🤖 内置 4 项智能体工具**：模型在日常对话中可自主调用划线搜索、主题网络与书目档案，用你认同的思维语料辅助决策。
- **🔄 一键实时同步**：看版顶部常驻「🔄 同步」按钮，阅读完新章节或下载新书后，点击即刻热更新大盘。
- **🔒 100% 本地隐私**：无任何外部服务器依赖，纯本地 Python + Node 运行，数据不出你的 Mac。

---

## 🚀 在 DeepSeek Harness 中安装使用

本插件完全符合 DeepSeek Harness 官方插件规范。

### 方式一：GitHub 一键安装（开源发布后）
1. 打开 DeepSeek Harness 客户端；
2. 点击左侧栏 **「🧩 插件」 ➔ 「添加插件」**；
3. 在弹窗输入框中直接填入本 GitHub 仓库地址：
   ```text
   https://github.com/your-username/dsh-plugin-reading-os
   ```
4. 点击 **“安装”**，左侧栏立即点亮 **`📖 ReadingOS 读书`**。

### 方式二：本地目录安装（开发者与抢先体验）
1. Clone 或下载本仓库至本机目录（例如 `~/Downloads/reading-os/dsh-plugin-reading-os`）；
2. 在 DeepSeek Harness 的「添加插件」弹窗中，填入该文件夹的绝对路径；
3. 点击 **“安装”** 即可。

---

## 🛠️ 智能体工具列表 (Tools for Agent)

安装后，DeepSeek 模型在与你对话时可自主使用以下工具：

| 工具名称 | 功能描述 |
| :--- | :--- |
| `reading_search_highlights` | 全文检索全库 4,400+ 条划线批注，寻找观点共鸣 |
| `reading_get_concept_network` | 调取跨书核心概念（放下、本质、风险等）的多书对照 |
| `reading_get_overview` | 查询个人阅读大盘数据（藏书量、四大维度权重、转化率） |
| `reading_get_book_highlights` | 查询指定单本书籍的所有划线与精读进度 |

---

## 📂 插件架构

```text
dsh-plugin-reading-os/
├── package.json         # DSH 插件清单与组合包声明
├── cordis.patch.yml     # DSH 宿主服务自动挂载配置
├── lib/
│   ├── client.js        # 客户端半边：侧栏图标、主面板 iframe、postMessage 通信
│   ├── index.js         # 宿主半边：/reading-os/ 路由挂载与 /api/sync 实时刷新
│   └── tools.js         # 注册给 DeepSeek 模型的 4 个原生认知工具
├── dashboard/
│   └── index.html       # 极简 Claude 纸感交互看版（响应式流布局）
└── scripts/
    ├── data_fetcher.py  # 零依赖动态 SQLite & Downloads 数据抓取引擎
    ├── core.py          # 核心分析器
    └── mcp_server.py    # MCP 标准服务
```

---

## 📄 License

[MIT License](LICENSE) © 2026
