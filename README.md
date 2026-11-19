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

### 几个主要模块

#### 1. 一年的划线足迹
读取本地图书数据库，通过热力图看看过去一年哪几天读得比较多、划了多少线，以及常看的书大概分布在哪些领域。

<p align="center">
  <img src="assets/01-hero-bento.png" width="92%" alt="一年的划线足迹" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

#### 2. 最近在读的书
展示最近在 Apple Books 里打开过的书籍与阅读进度，方便下次顺着思绪接着读；旁边也会带上几本常读的书。

<p align="center">
  <img src="assets/02-spotlight-and-companions.png" width="92%" alt="最近在读的书" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

#### 3. 跨书的主题整理
把散落在不同书里、讨论相似主题（如“知行合一”、“本质与底层”等）的划线放在一起，支持展开 3 本书横向对照，看看不同作者对同一个命题的不同视角与表达。

<p align="center">
  <img src="assets/03-theme-network.png" width="92%" alt="跨书的主题整理" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

#### 4. 单书划线与 Markdown 导出
点击任意一本书，右侧滑出抽屉列出全书所有划线与批注。可以直接一键复制或导出干净的 Markdown 笔记，也可以把选中的句子直接发到对话框里聊聊。

<p align="center">
  <img src="assets/04-reading-drawer.png" width="92%" alt="单书划线与 Markdown 导出" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

#### 5. 灵光偶遇与积读提醒
底部放了两个顺手的小卡片：**灵光书签**每次点击随机翻出一句往昔划线，适合工作间隙看一眼；**沉睡之书**则随手翻出以前下载了但还没读的书，提醒自己抽空翻开看看。

<p align="center">
  <img src="assets/05-dual-practical-cards.png" width="92%" alt="灵光偶遇与积读提醒" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

#### 6. 一键直通 DeepSeek 展开探讨
在日常阅读中，当我们想针对某一句话与 AI 交流时，原来的路径往往是：在 Apple Books 划线 ➔ 复制句子 ➔ 切到 AI 聊天软件 ➔ 粘贴 ➔ 手动删掉系统自动追加的一长串版权信息 ➔ 敲字发送。

ReadingOS 将这个步骤简化为一次点击：
- **零粘贴直达**：在抽屉或灵光卡片中点击 **`✨ 联动探讨`**，自动提取书名、作者与整洁的划线原文直通 DeepSeek Harness 对话框，省去反复切换与清理版权杂质的繁琐。
- **提示词随心设置**：在右上角 `⚙️`（偏好设置）中，你可以保留默认的多维研读引导，也可以切换为**「原句直问（自由提问）」**，把发问与思考的空间完全留给自己自由手打，或者编辑专属的提示词模板。

<p align="center">
  <img src="assets/06-dsh-bridge.gif" width="92%" alt="一键直通 DeepSeek 展开探讨" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.06);" />
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
