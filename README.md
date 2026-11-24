<p align="center">
  <img src="assets/apple-books-logo.png" width="72" height="72" alt="ReadingOS Logo" style="border-radius: 16px;" />
</p>

<h1 align="center">ReadingOS for DeepSeek Harness</h1>

<p align="center">
  让散落在 macOS 苹果图书里的划线与批注，在日常思考中随手可翻。
</p>

<p align="center">
  <a href="README_EN.md">English</a> · <b>简体中文</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-macOS-lightgrey?style=flat-square&logo=apple" alt="macOS Only">
  <img src="https://img.shields.io/badge/Host-DeepSeek%20Harness-blue?style=flat-square" alt="DeepSeek Harness">
  <img src="https://img.shields.io/badge/Privacy-Local--First-green?style=flat-square" alt="Local First">
  <img src="https://img.shields.io/badge/License-MIT-gray?style=flat-square" alt="MIT License">
</p>

---

### 这个插件在考虑哪些问题？

平时看电子书，习惯在 Mac 或 iPad 自带的「图书（Apple Books）」里翻阅，遇到触动自己的句子，随手划上一道线。

但在日常使用中，这种特定习惯常会碰上几个具体的小麻烦：

- **划线容易留在系统里被遗忘**：划线静静躺在系统的数据库里，合上书之后很少再去翻看，时间一长便慢慢淡忘了；
- **导出整理不太顺手**：官方自带的导出方式通常需要通过“邮件分享”发给自己，再一段段复制粘贴整理，处理整本书比较费劲；
- **想和模型聊聊时来回切换太繁琐**：遇到某句有共鸣的话想在侧边栏探讨时，需要在不同窗口之间反复复制粘贴。

它安静地运行在 DeepSeek Harness 的侧边栏，直接读取本地数据，提供一个不打扰、顺手看划线的界面。

---

### 核心界面与功能概览

#### 1. 全景阅读大盘：足迹热力图 · 动态伴读 · 认知资产
直接读取 macOS 苹果图书底层数据库，全自动生成过去 365 天阅读足迹热力图；智能呈现最近打开的在读图书与主力伴读书目，并归纳统计四大认知维度的知识沉淀密度。

<p align="center">
  <img src="assets/screenshot-1.png" width="94%" alt="ReadingOS 全景阅读大盘截图" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.08);" />
</p>

---

#### 2. 单书研读抽屉：全量划线流 · 选题现实思考 · 一键直通 DeepSeek
点击任意书籍，右侧优雅滑出全书划线批注流。
- **一键直通 DeepSeek**：点击「✨ 联动探讨」，自动剥除系统版权杂质，将书名与纯净划线原文直达对话框，免除繁琐的手动复制粘贴。
- **选题与现实思考**：从全书划线中提炼现实选题、社会痛点与本质反思，辅助灵感孵化。

<p align="center">
  <img src="assets/screenshot-2.png" width="94%" alt="ReadingOS 单书划线抽屉与联动探讨截图" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.08);" />
</p>

---

#### 3. 结构化复盘导出：高密度 Markdown 报告 · 知识库归档
支持一键生成具备多维思考框架的结构化复盘报告，或一键导出原汁原味的全书划线底稿。支持剪贴板双保险复制与 `.md` 文本下载，轻松衔接 Obsidian、Notion 或本地知识库。

<p align="center">
  <img src="assets/screenshot-3.png" width="94%" alt="ReadingOS 结构化 Markdown 导出截图" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.08);" />
</p>

---

### 适用习惯说明

这仅仅是针对某种阅读习惯的一种尝试，解决方案绝非唯一，适用场景也比较有限。安装前建议先看看是否符合你的日常习惯：

| 维度 | 符合习惯的情况 | 暂不适用的情况 |
| :--- | :--- | :--- |
| **操作系统** | **macOS**（依赖读取系统自带「图书」的本地数据库） | Windows、Linux |
| **阅读习惯** | 习惯用 **macOS 自带「图书（Apple Books）」** 看 EPUB / PDF 并随手划线（多端可通过 iCloud 自动同步） | 主要使用微信读书、Kindle、得到等第三方平台，或者看书从不划线（没有划线记录时界面会是空的） |
| **书籍文件** | 电子书存放在 `~/Downloads`（也支持在界面中自定义） | 仅在第三方云端 App 阅读，本地没有书籍文件 |

---

### 关于数据读取与设置

- **默认全自动识别**：插件会自动识别 macOS 系统「图书」的本地划线记录，并读取 `~/Downloads` 目录下的电子书，通常无需任何配置，打开即用。
- **界面设置与自定义路径**：如果你的电子书存放在其他文件夹、或者把书库迁移到了外接移动硬盘，直接在界面右上角点击 **`⚙️`（偏好设置）** 填入自定义目录保存即可，无需去终端折腾命令。
- **初次权限提示**：插件以纯只读方式读取本地数据。部分系统在初次打开时若显示空白，通常是 macOS 系统的隐私保护所致，在「系统设置 ➔ 隐私与安全性 ➔ 完全磁盘访问权限」中为 DeepSeek Harness 开启勾选即可。
- **实测验证环境**：已在 MacBook Pro（13-inch，macOS 15.8.2 Sequoia）上验证通过，适配 macOS 12+ 系统（通用支持 Apple Silicon 与 Intel 机型）。

---

### 关于数据更新与隐私

- **手动同步**：需要更新阅读数据时，点击右上角「同步」按钮即可。默认不做后台静默轮询，避免频繁弹窗打扰。
- **纯本地只读**：零外部网络请求，全程纯本地运行；仅对系统图书数据进行只读查询，绝不改写你的任何原始文件。

---

### 安装方式

1. 打开 **DeepSeek Harness** 桌面客户端；
2. 点击左侧工具栏底部的 **「🧩 插件」 ➔ 「添加插件」**；
3. 在地址输入框中填入本仓库地址并点击安装：
   ```text
   https://github.com/maikaojai/dsh-plugin-reading-os
   ```
4. 安装完成后，左侧栏会出现 **`📖 ReadingOS 读书`** 图标。

---

### 写在最后

最后，如果你也刚好有类似的阅读习惯，希望它能为你提供一份安静、不打扰的思考空间。

Crafted with care by [@maikaojai](https://github.com/maikaojai)

---

### 协议

本项目采用 [MIT License](LICENSE) 授权。
