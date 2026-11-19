<p align="center">
  <img src="assets/apple-books-logo.png" width="72" height="72" alt="ReadingOS Logo" style="border-radius: 16px;" />
</p>

<h1 align="center">ReadingOS for DeepSeek Harness</h1>

<p align="center">
  Keep your macOS Apple Books highlights and annotations close at hand during daily reflection.
</p>

<p align="center">
  <b>English</b> · <a href="README.md">简体中文</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-macOS-lightgrey?style=flat-square&logo=apple" alt="macOS Only">
  <img src="https://img.shields.io/badge/Host-DeepSeek%20Harness-blue?style=flat-square" alt="DeepSeek Harness">
  <img src="https://img.shields.io/badge/Privacy-Local--First-green?style=flat-square" alt="Local First">
  <img src="https://img.shields.io/badge/License-MIT-gray?style=flat-square" alt="MIT License">
</p>

---

### What Problems Is This Plugin Considering?

When reading electronic books, I often use the native "Books" (Apple Books) app on Mac or iPad, highlighting meaningful passages whenever inspiration strikes.

In practice, this specific reading habit often encounters several subtle frictions:

- **Highlights get buried and forgotten**: Annotations stay quietly tucked away in system databases, rarely revisited once a book is closed.
- **Exporting is inconvenient**: Native sharing typically requires emailing quotes to oneself and manually piecing notes together paragraph by paragraph.
- **Switching contexts with AI models is cumbersome**: Quoting a resonant sentence to explore deeper with an AI model requires constant window switching and manual copy-pasting.

**This plugin is not a monolithic all-in-one system; it is simply a quiet, personal companion tailored for this specific habit.**  
It runs unobtrusively in the DeepSeek Harness sidebar, reads local data directly, and provides a calm, peaceful interface to browse your reading thoughts.

---

### Core Modules

#### 1. Year in Highlights Footprint
Reads your local Books database to visualize your reading rhythm over the past year through a heatmap—when you read most actively, how many highlights you made, and how your reading distributes across knowledge dimensions.

<p align="center">
  <img src="assets/01-hero-bento.png" width="92%" alt="Year in Highlights Footprint" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

#### 2. Currently Reading & Companions
Displays books recently opened in Apple Books alongside your current progress, making it effortless to pick up right where your thoughts left off, accompanied by frequently revisited companion books.

<p align="center">
  <img src="assets/02-spotlight-and-companions.png" width="92%" alt="Currently Reading & Companions" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

#### 3. Cross-Book Theme Resonances
Brings together highlights from different books that share common themes (such as "Unity of Knowledge and Action" or "First Principles"), allowing you to expand 3 books side-by-side to compare how different authors articulate the same idea.

<p align="center">
  <img src="assets/03-theme-network.png" width="92%" alt="Cross-Book Theme Resonances" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

#### 4. Single-Book Highlights Drawer & Markdown Export
Clicking any book slides out a right drawer containing all highlights and annotations for that title. Easily copy quotes, export a clean Markdown summary, or send a selected sentence directly into the AI chat to discuss.

<p align="center">
  <img src="assets/04-reading-drawer.png" width="92%" alt="Single-Book Highlights Drawer & Markdown Export" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

#### 5. Daily Spark & Tsundoku Reminder
Two lightweight cards at the bottom: **Spark Bookmark** surfaces a random past highlight with each click (great for brief work breaks), while **Tsundoku Awakening** recalls downloaded books that have remained unread, gently reminding you to open them.

<p align="center">
  <img src="assets/05-dual-practical-cards.png" width="92%" alt="Daily Spark & Tsundoku Reminder" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.06);" />
</p>

---

### Suitable Habits & Scope

This is merely one attempt tailored for a specific way of reading—it is by no means a one-size-fits-all solution. Before installing, please check if it fits your daily routine:

| Dimension | Fits Well | Not Yet Applicable |
| :--- | :--- | :--- |
| **Operating System** | **macOS** (relies on reading the local SQLite database of Apple Books) | Windows, Linux |
| **Reading Habit** | Habitually reading EPUB / PDF in **Apple Books on macOS** and highlighting sentences (synced across devices via iCloud) | Primarily using WeChat Read, Kindle, or other third-party cloud apps, or reading without taking highlights |
| **Book Files** | E-books saved in `~/Downloads` (customizable via environment variables) | Cloud-only reading with no local book files |

---

### System Compatibility & Technical Notes

- **Verified Environment**: MacBook Pro (13-inch) · macOS 15.8.2 Sequoia
- **Compatibility**: macOS 12+ (Monterey / Ventura / Sonoma / Sequoia), universal support for both Apple Silicon (M-series) and Intel chips.
- **macOS Full Disk Access (FDA)**:  
  The plugin parses the local `com.apple.iBooksX` database in read-only mode. On modern macOS versions (Ventura / Sonoma / Sequoia), if no data appears upon initial sync, system TCC privacy controls may have restricted access to the sandbox container. Simply grant **Full Disk Access** to DeepSeek Harness under **System Settings ➔ Privacy & Security ➔ Full Disk Access**.
- **Customizable Paths (Optional)**:  
  Standard database locations are detected automatically. If your books or library reside on an external drive or non-standard path, configure them via environment variables:
  - `READING_OS_APPLE_BOOKS_DIR`: Base Documents directory containing Books SQLite files
  - `READING_OS_BKLIBRARY_PATH`: Exact path to `BKLibrary*.sqlite`
  - `READING_OS_AEANNOTATION_PATH`: Exact path to `AEAnnotation*.sqlite`
  - `READING_OS_BOOKS_DIR`: Downloaded e-books folder (defaults to `~/Downloads`)

---

### Data Sync & Privacy

- **Manual Sync by Default**: Click the "Sync" button in the top-right header whenever you wish to refresh data. No background polling or intrusive file watchers.
- **Strictly Local-First**: Zero external network requests, zero analytics, zero telemetry.
- **Read-Only Access**: Queries your local SQLite database in read-only mode (`mode=ro`), never modifying or overwriting your original reading data.

---

### Installation

1. Open the **DeepSeek Harness** desktop client;
2. Click **"🧩 Plugins" ➔ "Add Plugin"** at the bottom of the left sidebar;
3. Enter the repository URL and click Install:
   ```text
   https://github.com/maikaojai/dsh-plugin-reading-os
   ```
4. Once installed, the **`📖 ReadingOS`** icon will appear on the sidebar.

---

### In Closing

Finally, if you happen to share a similar reading routine, I hope this provides a quiet, undisturbed space for your reflection.

Crafted with care by [@maikaojai](https://github.com/maikaojai)

---

### License

This project is licensed under the [MIT License](LICENSE).
