# 📖 ReadingOS for DeepSeek Harness

> **macOS 本地图书划线与阅读记录插件 · DeepSeek Harness**  
> 直接读取 macOS 自带「图书」App 的划线高亮与本地下载的书籍，在 DeepSeek Harness 里随时查看阅读足迹，并可一键把划线内容发给 DeepSeek 展开探讨。

---

## 📸 界面预览 (Preview)

### 1. 阅读看板 (Dashboard)
![ReadingOS 阅读看板](assets/01-responsive-dashboard.png)
*展示近一年阅读足迹热力图、最近下载的书籍（书名、作者与简介）、藏书分类比例与阅读统计。支持自适应窗口宽度，顶部提供「🔄 同步」刷新按钮。*

### 2. 书籍划线抽屉与对话联动 (Highlights Drawer)
![书籍划线抽屉与对话联动](assets/02-book-highlights-drawer.png)
*点击任意书籍可展开全部划线内容与标记时间；轻点「✨ 联动 DSH 探讨」，直接在 DeepSeek Harness 中发起新会话，就某句划线内容展开交流。*

### 3. 划线快速检索 (Highlights Search)
![划线快速检索](assets/03-quick-search-modal.png)
*点击顶部搜索框或按快捷键 `/`，快速查找全部划线记录中的关键词（例如搜索「舍」）。*

---

## ✨ 主要功能

- 📖 **直读 macOS 自带图书**：直接读取 macOS「图书」App 的本地记录，自动提取书名、划线内容、标注时间与阅读进度，无需手动导出。
- 📁 **关联本地下载目录**：自动统计下载目录（如 `~/Downloads`）中的电子书（EPUB、PDF、MOBI 等），展示最近添加的书籍与待读情况。
- 🗓️ **阅读热力图与分类概览**：以清晰的卡片形式展示 365 天阅读足迹、各类书籍分布与阅读统计，支持随窗口自适应排版和深浅色模式。
- 💬 **一键联动 DeepSeek 探讨**：查看划线时，点击卡片上的「联动 DSH 探讨」，会自动在对话框中填入该划线内容并开启交流。
- 🔍 **划线快速检索**：支持全局搜索全部划线记录，方便快速找回某句话或某个观点。
- 🛠️ **提供 Agent 工具**：向 DeepSeek 提供划线搜索和图书信息查询工具，在普通对话中 DeepSeek 也能查阅你的读书记录。
- 🔄 **一键刷新同步**：页面右上角提供「同步」按钮，新划了线或下了新书，点一下即可刷新数据。
- 🔒 **纯本地运行**：只读取本机本地数据，不需要连接任何第三方云端服务，隐私安全。

---

## 🚀 在 DeepSeek Harness 中安装使用

本插件符合 DeepSeek Harness 插件规范。

### 方式一：GitHub 一键安装（推荐）
1. 打开 DeepSeek Harness 桌面端；
2. 点击左侧栏 **「🧩 插件」 ➔ 「添加插件」**；
3. 在弹窗输入框中填入本仓库地址：
   ```text
   https://github.com/maikaojai/dsh-plugin-reading-os
   ```
4. 点击 **“安装”**，左侧栏即可看到 **`📖 ReadingOS 读书`**。

### 方式二：本地目录安装（开发者与抢先体验）
1. Clone 或下载本仓库至本机目录（例如 `~/Downloads/reading-os/dsh-plugin-reading-os`）；
2. 在 DeepSeek Harness 的「添加插件」弹窗中，填入该文件夹的绝对路径；
3. 点击 **“安装”** 即可。

---

## 🛠️ 智能体工具列表 (Tools for Agent)

安装后，DeepSeek 模型在与你对话时可按需调用以下工具：

| 工具名称 | 功能描述 |
| :--- | :--- |
| `reading_search_highlights` | 按关键词搜索图书划线记录 |
| `reading_get_concept_network` | 查看跨书的相关主题与关联划线 |
| `reading_get_overview` | 查看藏书总量、各类别比例与阅读统计 |
| `reading_get_book_highlights` | 查询某本具体书籍的划线与笔记 |

---

## 📂 项目结构

```text
dsh-plugin-reading-os/
├── package.json         # DSH 插件清单与配置声明
├── cordis.patch.yml     # DSH 服务自动挂载配置
├── lib/
│   ├── client.js        # 客户端：侧边栏图标、主面板 iframe、postMessage 通信
│   ├── index.js         # 服务端：静态路由挂载与 /api/sync 刷新接口
│   └── tools.js         # 注册给 DeepSeek 模型的工具接口
├── dashboard/
│   └── index.html       # 响应式阅读看板页面
└── scripts/
    ├── data_fetcher.py  # 本地图书与下载目录数据提取脚本
    ├── core.py          # 核心解析逻辑
    └── mcp_server.py    # MCP 服务端
```

---

## 📄 License

[MIT License](LICENSE) © 2026 maikaojai
