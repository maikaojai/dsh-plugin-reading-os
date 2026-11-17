<p align="center">
  <img src="assets/apple-books-logo.png" width="76" height="76" alt="ReadingOS Logo" style="border-radius: 18px; box-shadow: 0 4px 16px rgba(0,0,0,0.08);" />
</p>

<h1 align="center">ReadingOS for DeepSeek Harness</h1>

<p align="center">
  <strong>让散落在 macOS 苹果图书中的划线与触动，在日常深度思考中重获新生。</strong>
  <br />
  <em>纯本地优先（Local-First）· 零配置自动同步 · 跨书主题共鸣 · 辩证思辨探讨 · 一键知识导出</em>
</p>

<p align="center">
  <a href="https://github.com/maikaojai/dsh-plugin-reading-os/releases/tag/v2.1.0"><img src="https://img.shields.io/badge/Release-v2.1.0-CC785C?style=flat-square" alt="Version 2.1.0"></a>
  <a href="https://github.com/deepseek-ai/deepseek-harness"><img src="https://img.shields.io/badge/Host-DeepSeek%20Harness-blue?style=flat-square" alt="DeepSeek Harness"></a>
  <a href="#-本地优先与隐私保障"><img src="https://img.shields.io/badge/Privacy-100%25%20Local--First-green?style=flat-square" alt="Local First"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-gray?style=flat-square" alt="MIT License"></a>
  <a href="#-环境与前置要求"><img src="https://img.shields.io/badge/Platform-macOS-lightgrey?style=flat-square&logo=apple" alt="macOS Only"></a>
</p>

---

## 📽️ 全景动态演示 (Hero Demo)

> 💡 **无需安装、零配置体验**：本项目内置独立的经典公版书演示页面 [`dashboard/demo.html`](dashboard/demo.html)，无需本地存在苹果图书数据，在任意浏览器中即可直接打开交互。

<p align="center">
  <img src="assets/00-reading-os-demo.gif" width="100%" alt="ReadingOS v2.1 动态交互演示" style="border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.12);" />
</p>

---

## 💡 为什么做 ReadingOS？

在日常阅读中，很多人习惯在 Mac、iPhone 或 iPad 原生的「图书（Apple Books）」中翻阅电子书。遇到心弦一动的句子，随手划上一道线。那些高亮不仅是文字，更是你在某个时间节点最真实的思想触动。

然而，传统的原生阅读体验长期存在四大断裂：

| 痛点场景 | 传统苹果图书现状 | ReadingOS 闭环解决方案 |
| :--- | :--- | :--- |
| **划线沉睡沉没** | 划线封闭在 macOS 底层 SQLite 中，合上书即成数字灰尘 | **365天足迹看板 + 灵光书签偶遇**，让往昔思考重新活在当下 |
| **导出极其折磨** | 必须逐条通过“邮件分享”发给自己，再手动复制粘贴整理 | **纯本地直读数据库，一键生成结构化 Markdown** / 复制剪贴板 |
| **AI 探讨高摩擦** | 手动选中文本、跨窗口切换粘贴；AI 容易顺从迎合，陷入信息茧房 | **单击「联动 DSH 探讨」**，自动注入三维辩证审视骨架，打破思维局限 |
| **收尾缺乏交付** | 读完几十本书，划线成百上千条，却提炼不出核心见解与现实产出 | **「💡 选题与现实思考」**，从全书划线中提炼痛点、正反辩证与创作骨架 |

**ReadingOS 的使命，就是在你的侧边栏构筑一个连接「输入（原生划线）➔ 思考（三维辩证研读）➔ 输出（选题孵化与复盘报告）」的认知操作系统。**

---

## 🌟 核心功能特性

### 1. 自动同步，足迹尽览 (Reading Bento & Heatmap)
- **原生零配置读取**：无需导出或第三方账户，后台自动直连 macOS 苹果图书底层数据库与本地下载书架（`~/Downloads`）；
- **365 天阅读热力图**：真实还原每日划线密度与阅读律动，鼠标悬浮即可洞察当日标记细节；
- **藏书资产与转化维度**：动态统计总藏书、转化率、沉睡积读率，以及四大知识领域的划线沉淀深度；
- **最近入库即时轮播**：按入库时间展示近期添加的书目卡片，支持轻量翻页预览。

<p align="center">
  <img src="assets/01-hero-bento.png" width="95%" alt="近一年阅读足迹与藏书资产看板" style="border-radius: 10px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

### 2. 动态聚焦与经典伴读 (Spotlight & Companions)
- **精准感知最近打开**：动态提取你在 Apple Books 中最后一次翻阅或划线的书籍，呈现实时原生百分比进度条与最近高亮金句；
- **无缝伴读卡片**：智能联动书架中的深度研读书籍，直观展示批注体量与关键思想；
- **沉浸式抽屉交互**：点击任意一本书即可从右侧顺畅滑出专属划线流；再次点击卡片即可直接收起，交互轻盈无压力。

<p align="center">
  <img src="assets/02-spotlight-and-companions.png" width="95%" alt="动态聚焦与经典伴读" style="border-radius: 10px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

### 3. 跨书主题共鸣网络 (Cross-Book Theme Network)
- **打破书本孤岛**：将散落在不同书籍、不同作者中的划线，按照核心哲学与方法论主题（如「知行合一」、「心性宁静」、「见微知著」等）横向串联；
- **3 本对比渐进披露**：点击「展开 3 本对比」，即可并排横向研读不同先贤与作者针对同一命题的洞见碰撞；
- **直击 DSH 辩证对话**：每个主题对比卡片均配备「✨ 联动 DSH 探讨」，一键将多视角观点送入模型进行高阶辩证。

<p align="center">
  <img src="assets/03-theme-network.png" width="95%" alt="跨书主题网络与 3 本对比" style="border-radius: 10px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

### 4. 单书划线流与深度思辨抽屉 (Highlight Stream Drawer)
- **全量划线时间流**：以清晰的序号、原句引用与批注笔记陈列，完全保留划线时的真实语境；
- **💡 选题与现实思考**：自动聚合本书划线，结合当下真实的社会热点与工作生活痛点，自动提炼 2~3 个现实创作议题与反常识思辨点；
- **📑 Markdown 报告导出**：支持导出包含全量批注的整洁 Markdown 文档，或一键拷贝至剪贴板，平滑接入 Obsidian、Logseq、Notion 等知识库。

<p align="center">
  <img src="assets/05-reading-drawer-stream.png" width="95%" alt="单书划线流抽屉与选题孵化" style="border-radius: 10px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

### 5. 轻盈灵光与沉睡积读唤醒 (Daily Spark & Tsundoku Awakening)
- **灵光书签 · 今日偶遇**：轻量级淡入淡出动画，点击卡片任意区域即可随机邂逅往昔一条深刻划线，碎片时间随时激发顿悟；
- **沉睡之书 · 待唤醒**：扫描库中下载已久却尚未标记的书籍，提供「✨ 唤醒研读」、「📖 速览10分」与「已读过」动作，消解“买书如山倒、读书如抽丝”的积读焦虑。

<p align="center">
  <img src="assets/04-dual-practical-cards.png" width="95%" alt="每日灵光书签与沉睡书籍唤醒" style="border-radius: 10px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

## 🎯 先验适用指南 (Fit & Non-Fit)

为了避免安装后因使用习惯差异产生“页面没有数据”的困惑，请先阅读以下适配说明：

| 维度 | ✅ 绝佳适配场景 | ❌ 暂不适用或数据为空场景 |
| :--- | :--- | :--- |
| **操作系统** | **macOS**（深度利用系统级 Apple Books SQLite 架构） | Windows、Linux 系统 |
| **阅读软件** | **macOS 自带「图书（Apple Books）」**，在 Mac、iPad 或 iPhone 上阅读 EPUB/PDF 并有划线习惯（通过 iCloud 自动同步） | 主要使用微信读书、Kindle、得到、网易蜗牛、MarginNote 等第三方闭源平台 |
| **划线习惯** | 阅读时习惯划线高亮或添加批注 | 习惯通读但从不划线（无高亮记录时热力图与划线流将无法呈现） |
| **书籍位置** | 电子书存放于 `~/Downloads`（或通过环境变量自定义） | 纯在线云端阅读且未下载任何本地书目 |

---

## 🔒 本地优先与隐私保障 (Local-First Guarantee)

- 🛡️ **绝对本地运行**：ReadingOS 没有任何外部遥测（Telemetry）、不加载任何远程第三方脚本、不连接任何未经你授权的外部服务器；
- 💾 **直接读取只读镜像**：插件通过只读模式查询本地 Apple Books 数据库，绝不修改、覆盖或破坏你的原始阅读记录；
- 🌐 **独立公开演示模式**：仓库自带独立的 [`dashboard/demo.html`](dashboard/demo.html)，全部采用公版古典著作（《沉思录》、《传习录》、《道德经》等），演示与测试过程中绝不触碰任何用户隐私划线。

---

## 🚀 快速开始与安装

### 方式一：在 DeepSeek Harness 中在线一键安装（推荐）

1. 打开 **DeepSeek Harness** 桌面客户端；
2. 点击左侧工具栏底部的 **「🧩 插件」 ➔ 「添加插件」**；
3. 在地址输入框中填入本仓库地址：
   ```text
   https://github.com/maikaojai/dsh-plugin-reading-os
   ```
4. 点击 **“安装”**，左侧栏即可出现 **`📖 ReadingOS 读书`** 图标；
5. 点击图标，即可即时阅览你的个人阅读空间。

---

### 方式二：本地软链接开发与体验

如果你希望微调样式或参与贡献：

```bash
# 1. 克隆代码仓库到本地
git clone https://github.com/maikaojai/dsh-plugin-reading-os.git
cd dsh-plugin-reading-os

# 2. 在浏览器中直接预览公开演示版（无需 DSH 与 Apple Books）
open dashboard/demo.html

# 3. 或在 DeepSeek Harness 中将本目录路径作为本地插件添加
```

本地修改 `dashboard/index.html` 后，在 DSH 窗口中按快捷键 **`Command + R`** 即可瞬间刷新热更。

---

## 🤖 智能体工具矩阵 (Agent Tools)

安装后，DeepSeek 在主对话框中可根据你的指令自主调用以下工具协助你复盘：

| 工具名称 | 描述说明 | 典型对话示例 |
| :--- | :--- | :--- |
| `reading_search_highlights` | 按关键词或概念跨全书库全文检索划线与批注 | *"帮我查查在所有读过的书里，关于'边际'的划线有哪些？"* |
| `reading_get_book_highlights` | 获取指定书籍的所有完整高亮流与读者批注 | *"提取《沉思录》里的全部划线，帮我做一份斯多葛核心要点摘要。"* |
| `reading_get_concept_network` | 提取跨书共鸣主题网络与交叉概念集群 | *"看看我的书库里关于'知行合一'有哪些书形成了思想共鸣？"* |
| `reading_get_overview` | 统计阅读资产总量、转化率与知识维度分布 | *"总结一下我最近 30 天的阅读量与沉淀偏好。"* |

---

## 📄 开源协议 (License)

本项目遵循 [MIT License](LICENSE) 开源协议，欢迎 Star、Fork、提交 Issue 或发起 PR。
