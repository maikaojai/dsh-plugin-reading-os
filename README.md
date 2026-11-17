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

### 这个插件在考虑哪些问题？

平时看电子书，习惯在 Mac 或 iPad 自带的「图书（Apple Books）」里翻阅，遇到有所触动的句子，随手划上一道线。

但在日常使用中，这种特定习惯常会碰上几个具体的小麻烦：

- **划线容易留在系统里被遗忘**：划线静静存放在系统的数据库中，合上书之后很少再去翻看，时间一长便容易淡忘；
- **导出整理不太顺手**：官方自带的导出方式通常需要通过“邮件分享”发给自己，再一段段复制粘贴整理，处理整本书比较费劲；
- **想和模型聊聊时的阻力**：遇到某句有共鸣的话想在侧边栏探讨时，来回选中文本、切换窗口与粘贴有些繁琐。

**这个插件并不是什么大而全的系统，只是针对上述特定习惯做的一个随手翻阅的小工具。**  
它安静地运行在 DeepSeek Harness 的侧边栏，直接读取本地数据，提供一个不打扰、顺手看划线的界面。

---

### 几个主要模块

#### 1. 一年的划线足迹
读取本地图书数据库，通过热力图看看过去一年哪几天读得比较多、划了多少线，以及常看的书大概分布在哪些领域。

<p align="center">
  <img src="assets/01-hero-bento.png" width="92%" alt="阅读足迹与藏书概览" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

#### 2. 最近在读的书
展示最近在 Apple Books 里打开过的书籍与阅读进度，方便下次顺着思绪接着读；旁边也会带上几本常读的书。

<p align="center">
  <img src="assets/02-spotlight-and-companions.png" width="92%" alt="最近打开与伴读" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

#### 3. 跨书的主题整理
把散落在不同书里、讨论相似主题（如“知行合一”、“本质与底层”等）的划线放在一起，支持展开 3 本书横向对照，看看不同作者面对同一命题时的不同说法。

<p align="center">
  <img src="assets/03-theme-network.png" width="92%" alt="跨书主题整理与 3 本对比" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

#### 4. 单书划线与 Markdown 导出
点击任意一本书，右侧滑出抽屉列出全书所有划线与批注。可以直接一键复制或导出干净的 Markdown 笔记，也可以把选中的句子直接发到对话框里聊聊。

<p align="center">
  <img src="assets/04-reading-drawer.png" width="92%" alt="单书划线抽屉与导出" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

#### 5. 灵光偶遇与积读提醒
底部放了两个顺手的小卡片：**灵光书签**每次点击随机翻出一句往昔划线，适合工作间隙看一眼；**沉睡之书**则随手翻出以前下载了但还没读的书，提醒自己抽空翻开看看。

<p align="center">
  <img src="assets/05-dual-practical-cards.png" width="92%" alt="灵光书签与沉睡书籍提醒" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

### 适用习惯说明

这仅仅是针对特定阅读习惯的一种尝试，解决方案也绝非唯一，适用范围相对特定。安装前请先看看是否符合你的习惯：

| 维度 | 符合习惯的情况 | 暂不适用的情况 |
| :--- | :--- | :--- |
| **操作系统** | **macOS**（依赖读取系统自带「图书」的本地数据库） | Windows、Linux |
| **阅读习惯** | 习惯用 **macOS 自带「图书（Apple Books）」** 看 EPUB / PDF 并随手划线（多端可通过 iCloud 自动同步） | 主要使用微信读书、Kindle、得到等第三方平台，或者看书从不划线（没有划线记录时界面会是空的） |
| **书籍文件** | 电子书存放在 `~/Downloads`（也支持通过环境变量自定义） | 仅在第三方云端 App 阅读，本地没有书籍文件 |

---

### 关于自动刷新

插件支持静默自动刷新：当你在「图书」App 中读完书、划完线，切回 DeepSeek Harness 窗口时，页面会自动检测并拉取最新数据，无需手动按同步或刷新。

---

### 关于数据与隐私

- **纯本地运行**：不包含任何外部网络请求、遥测或埋点代码；
- **只读读取**：只对系统「图书」的本地 SQLite 数据库进行只读查询，绝不改写或修改你的任何原有图书数据。

---

### 安装方式

#### 方式一：在 DeepSeek Harness 中在线安装（推荐）

1. 打开 **DeepSeek Harness** 桌面客户端；
2. 点击左侧工具栏底部的 **「🧩 插件」 ➔ 「添加插件」**；
3. 在地址输入框中填入本仓库地址并点击安装：
   ```text
   https://github.com/maikaojai/dsh-plugin-reading-os
   ```
4. 安装完成后，左侧栏会出现 **`📖 ReadingOS 读书`** 图标。

#### 方式二：本地开发安装

如果你希望微调样式或参与贡献：

```bash
# 1. 克隆代码仓库到本地
git clone https://github.com/maikaojai/dsh-plugin-reading-os.git

# 2. 在 DeepSeek Harness 的「添加插件」中填入本地目录绝对路径确认安装
# 3. 本地修改代码后，在窗口中按 Command + R 即可刷新预览
```

---

### 协议

本项目采用 [MIT License](LICENSE) 授权。
