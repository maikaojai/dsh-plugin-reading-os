<p align="center">
  <img src="assets/apple-books-logo.png" width="72" height="72" alt="ReadingOS Logo" style="border-radius: 16px;" />
</p>

<h1 align="center">ReadingOS for DeepSeek Harness</h1>

<p align="center">
  让散落在 macOS 苹果图书中的划线与随想，在日常思考中重新被翻阅。
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-macOS-lightgrey?style=flat-square&logo=apple" alt="macOS Only">
  <img src="https://img.shields.io/badge/Host-DeepSeek%20Harness-blue?style=flat-square" alt="DeepSeek Harness">
  <img src="https://img.shields.io/badge/Privacy-Local--First-green?style=flat-square" alt="Local First">
  <img src="https://img.shields.io/badge/License-MIT-gray?style=flat-square" alt="MIT License">
</p>

---

### 为什么写这个插件？

平时看电子书，习惯在 Mac 或 iPad 自带的「图书（Apple Books）」里翻阅，遇到有所触动的句子，随手划上一道线。

但在日常使用中，这种习惯经常遇到几个小麻烦：

- **读完容易沉睡**：划线静静躺在系统的底层数据库里，书读完合上后，很少再去翻找查看；
- **导出步骤繁琐**：苹果图书自带的划线导出通常只能通过“邮件共享”逐条发给自己，再手动复制粘贴整理，处理整本书的长笔记比较耗时；
- **与模型探讨的摩擦**：想要针对书里的某句话和 AI 聊聊时，需要来回选中文本、切换窗口与粘贴。

**ReadingOS 是为满足这种特定习惯而写的一个小工具。**  
它运行在 DeepSeek Harness 的侧边栏，直接读取本地图书数据库，提供一个轻便、随手可翻的阅读看板与划线整理抽屉。

---

### 核心功能

#### 1. 阅读足迹与藏书概览
自动读取系统「图书」的划线记录与本地下载书架，以热力图展示过去一年的阅读与标记轨迹，直观查看划线频次与分类分布。

<p align="center">
  <img src="assets/01-hero-bento.png" width="92%" alt="阅读足迹与藏书概览" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

#### 2. 最近打开与阅读进度
动态展示最近在 Apple Books 中翻阅的书籍，透出阅读进度百分比与最近的高亮句子，方便随时接着上次的思绪继续读。

<p align="center">
  <img src="assets/02-spotlight-and-companions.png" width="92%" alt="最近打开与伴读" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

#### 3. 跨书主题整理
把散落在不同书籍中、关于同一主题（例如知行合一、底层逻辑、规律认知等）的划线聚集在一起，支持展开 3 本书横向对比，看不同作者在同一命题下的不同思考。

<p align="center">
  <img src="assets/03-theme-network.png" width="92%" alt="跨书主题整理与 3 本对比" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

#### 4. 单书划线抽屉与一键导出
点击书本卡片即可从右侧顺畅滑出划线抽屉，按时间顺序清晰列出全书笔记。支持一键导出格式整洁的 Markdown 文档或复制到剪贴板，也可以一键将句子带入对话框与 DeepSeek 进一步探讨。

<p align="center">
  <img src="assets/05-reading-drawer-stream.png" width="92%" alt="单书划线抽屉" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

#### 5. 灵光书签与沉睡书籍提醒
底部常驻两个轻量模块：**灵光书签**每次点击随机翻出一句往昔划线，适合碎片时间看一眼；**沉睡之书**则提醒很久以前下载但尚未翻开的书籍，减轻积读压力。

<p align="center">
  <img src="assets/04-dual-practical-cards.png" width="92%" alt="灵光书签与沉睡书籍提醒" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

### 适用场景说明

这个插件源于作者个人的日常阅读偏好，适用场景较为特定。安装前请留意：

| 维度 | 适合的情况 | 暂不适用的情况 |
| :--- | :--- | :--- |
| **操作系统** | **macOS**（需要读取系统自带图书数据库） | Windows、Linux |
| **阅读习惯** | 使用 **macOS 自带「图书」** 阅读 EPUB / PDF 并有划线习惯（可通过 iCloud 自动多端同步） | 主要使用微信读书、Kindle、得到等第三方平台，或读书从不划线（无划线数据时界面会为空） |
| **书籍存放** | 电子书存放在 `~/Downloads`（或设置环境变量 `READING_OS_BOOKS_DIR`） | 仅在第三方云端 App 阅读，本地无文件 |

---

### 本地优先与隐私

- **纯本地运行**：不包含任何外部埋点或遥测代码，不加载任何未经许可的远程资源；
- **只读查询**：插件仅对系统「图书」的本地数据库进行只读查询，绝不修改或写入任何原数据。

---

### 安装方法

#### 方式一：在 DeepSeek Harness 中在线安装（推荐）

1. 打开 **DeepSeek Harness** 桌面客户端；
2. 点击左侧工具栏底部的 **「🧩 插件」 ➔ 「添加插件」**；
3. 在地址输入框中填入本仓库地址：
   ```text
   https://github.com/maikaojai/dsh-plugin-reading-os
   ```
4. 点击 **“安装”**，左侧栏即可出现 **`📖 ReadingOS 读书`** 图标。

#### 方式二：本地开发安装

如果你希望参与微调或自定义样式：

```bash
# 1. 克隆仓库到本地
git clone https://github.com/maikaojai/dsh-plugin-reading-os.git

# 2. 在 DeepSeek Harness 的「添加插件」中填入本地目录绝对路径确认安装
# 3. 修改代码后，在窗口中按 Command + R 即可刷新预览
```

---

### 开源协议

本项目采用 [MIT License](LICENSE) 授权。
