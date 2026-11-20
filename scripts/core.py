#!/usr/bin/env python3
"""
ReadingOS Core Engine
- Scans Apple Books SQLite database (BKLibrary + AEAnnotation)
- Scans Downloads directory (Z-Library books, EPUBs, PDFs)
- Handles standalone PDFs (opened via Preview/Acrobat vs Books)
- Correlates reading funnel (Download -> Read -> Highlight)
- Daily Spaced Repetition / Recall generator
- Markdown Knowledge Vault exporter
"""

import os
import sys
import glob
import json
import sqlite3
import re
import random
from datetime import datetime, timezone
from pathlib import Path

HOME = os.path.expanduser("~")
DEFAULT_BOOKS_DOCS = os.path.join(HOME, "Library/Containers/com.apple.iBooksX/Data/Documents")
CANDIDATE_BOOKS_DOCS = [
    os.environ.get("READING_OS_APPLE_BOOKS_DIR"),
    DEFAULT_BOOKS_DOCS,
    os.path.join(HOME, "Library/Containers/com.apple.BKAgentService/Data/Documents/iBooks"),
    os.path.join(HOME, "Library/Containers/Apple Books/Data/Documents")
]
DOWNLOADS_DIR = os.environ.get("READING_OS_BOOKS_DIR", os.path.join(HOME, "Downloads"))
APPLE_CORE_DATA_EPOCH = 978307200  # seconds between 1970-01-01 and 2001-01-01

def find_sqlite(subfolder, pattern, env_override=None):
    if env_override and os.path.exists(env_override):
        return env_override

    for base in CANDIDATE_BOOKS_DOCS:
        if not base:
            continue
        folder = os.path.join(base, subfolder)
        if os.path.exists(folder):
            matches = [f for f in glob.glob(os.path.join(folder, pattern)) if not f.endswith(("-wal", "-shm"))]
            if matches:
                return matches[0]
        direct_matches = [f for f in glob.glob(os.path.join(base, pattern)) if not f.endswith(("-wal", "-shm"))]
        if direct_matches:
            return direct_matches[0]

    fuzzy_matches = [f for f in glob.glob(os.path.join(HOME, "Library/Containers/*Books*/Data/Documents", subfolder, pattern)) if not f.endswith(("-wal", "-shm"))]
    if fuzzy_matches:
        return fuzzy_matches[0]

    return None

class ReadingOS:
    def __init__(self, downloads_dir=DOWNLOADS_DIR):
        self.downloads_dir = downloads_dir
        self.bklibrary_db = find_sqlite("BKLibrary", "BKLibrary*.sqlite", os.environ.get("READING_OS_BKLIBRARY_PATH"))
        self.annotation_db = find_sqlite("AEAnnotation", "AEAnnotation*.sqlite", os.environ.get("READING_OS_AEANNOTATION_PATH"))
        self.books = {}        # asset_id -> book dict
        self.annotations = []  # list of annotation dicts
        self.downloads = []    # list of downloaded file dicts
        self.loaded = False

    def load_all(self):
        self.load_apple_books()
        self.load_downloads()
        self.correlate()
        self.loaded = True

    def load_apple_books(self):
        if not self.bklibrary_db or not self.annotation_db:
            return

        try:
            conn = sqlite3.connect(f"file:{self.bklibrary_db}?mode=ro", uri=True)
            cursor = conn.cursor()
            cursor.execute(f"ATTACH DATABASE 'file:{self.annotation_db}?mode=ro' AS ann;")

            # 1. Load books
            book_query = """
            SELECT ZASSETID, ZTITLE, ZAUTHOR, ZGENRE, ZPATH,
                   ZLASTOPENDATE, ZREADINGPROGRESS
            FROM ZBKLIBRARYASSET
            WHERE ZTITLE IS NOT NULL;
            """
            cursor.execute(book_query)
            for row in cursor.fetchall():
                asset_id, title, author, genre, path, last_open, progress = row
                last_open_dt = None
                if last_open:
                    try:
                        last_open_dt = datetime.fromtimestamp(last_open + APPLE_CORE_DATA_EPOCH).strftime('%Y-%m-%d %H:%M')
                    except Exception:
                        pass

                self.books[asset_id] = {
                    "asset_id": asset_id,
                    "title": (title or "").strip(),
                    "clean_title": self._clean_title(title or ""),
                    "author": (author or "未知作者").strip(),
                    "genre": genre or "未分类",
                    "path": path,
                    "last_open": last_open_dt,
                    "progress": round(progress * 100, 1) if progress else 0.0,
                    "highlights": []
                }

            # 2. Load annotations
            ann_query = """
            SELECT ZANNOTATIONASSETID, ZANNOTATIONSELECTEDTEXT, ZANNOTATIONNOTE,
                   ZANNOTATIONCREATIONDATE, ZANNOTATIONSTYLE, ZANNOTATIONISUNDERLINE
            FROM ann.ZAEANNOTATION
            WHERE ZANNOTATIONDELETED = 0 AND ZANNOTATIONSELECTEDTEXT IS NOT NULL
            ORDER BY ZANNOTATIONCREATIONDATE ASC;
            """
            cursor.execute(ann_query)
            for row in cursor.fetchall():
                asset_id, text, note, created, style, is_underline = row
                created_dt = None
                if created:
                    try:
                        created_dt = datetime.fromtimestamp(created + APPLE_CORE_DATA_EPOCH).strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        pass

                ann_item = {
                    "asset_id": asset_id,
                    "text": (text or "").strip(),
                    "note": (note or "").strip() if note else None,
                    "created_at": created_dt,
                    "timestamp": created + APPLE_CORE_DATA_EPOCH if created else 0,
                    "style": style,
                    "is_underline": bool(is_underline)
                }
                self.annotations.append(ann_item)
                if asset_id in self.books:
                    self.books[asset_id]["highlights"].append(ann_item)

            conn.close()
        except sqlite3.OperationalError as e:
            print(f"[Warning] Failed to read Apple Books database: {e}", file=sys.stderr)

    def _clean_title(self, raw_title):
        # Remove common marketing subtitles / brackets
        t = re.sub(r"\(z-library.*?\)", "", raw_title, flags=re.I)
        t = re.sub(r"（.*?）", "", t)
        t = re.sub(r"\(.*?\)", "", t)
        t = re.sub(r"【.*?】", "", t)
        t = re.sub(r"《|》", "", t)
        t = re.sub(r"\s+", " ", t).strip()
        return t

    def load_downloads(self):
        if not os.path.exists(self.downloads_dir):
            return

        for fname in os.listdir(self.downloads_dir):
            lower_fname = fname.lower()
            if not lower_fname.endswith(('.epub', '.pdf', '.mobi', '.azw3')):
                continue

            fpath = os.path.join(self.downloads_dir, fname)
            if not os.path.isfile(fpath):
                continue

            stat = os.stat(fpath)
            ctime = stat.st_birthtime if hasattr(stat, 'st_birthtime') else stat.st_ctime
            mtime = stat.st_mtime
            atime = stat.st_atime
            size_mb = round(stat.st_size / (1024 * 1024), 2)
            ext = os.path.splitext(fname)[1].lower().replace('.', '')

            # Parse Z-Library naming convention
            # e.g.: 一生之敌 (（美）史蒂文·普莱斯菲尔德) (Z-Library).epub
            is_zlib = 'z-lib' in lower_fname or 'zlibrary' in lower_fname
            title, author = self._parse_filename(fname)

            # Check if standalone PDF was opened (atime significantly after download)
            was_opened = False
            if atime > max(ctime, mtime) + 300:  # accessed >5 mins after write
                was_opened = True

            self.downloads.append({
                "filename": fname,
                "filepath": fpath,
                "title": title,
                "clean_title": self._clean_title(title),
                "author": author,
                "ext": ext,
                "size_mb": size_mb,
                "is_zlib": is_zlib,
                "download_time": datetime.fromtimestamp(ctime).strftime('%Y-%m-%d %H:%M'),
                "download_ts": ctime,
                "last_access_time": datetime.fromtimestamp(atime).strftime('%Y-%m-%d %H:%M'),
                "was_opened": was_opened,
                "status": "PENDING"
            })

    def _parse_filename(self, filename):
        name_no_ext = os.path.splitext(filename)[0]
        # Clean out z-lib tags
        clean_name = re.sub(r"\(z-library.*?\)", "", name_no_ext, flags=re.I)
        clean_name = re.sub(r"\(1lib.*?\)", "", clean_name, flags=re.I)
        clean_name = re.sub(r"\(z-lib.*?\)", "", clean_name, flags=re.I)
        clean_name = clean_name.strip()

        # Try pattern: Title (Author)
        match = re.search(r"^(.*?)\s*\((.*?)\)$", clean_name)
        if match:
            t = match.group(1).strip()
            a = match.group(2).strip()
            return t, a

        # Try pattern: 《Title》Author
        match = re.search(r"^《(.*?)》(.*?)$", clean_name)
        if match:
            t = match.group(1).strip()
            a = match.group(2).strip() or "未知作者"
            return t, a

        return clean_name, "未知作者"

    def correlate(self):
        """Cross-correlate downloads with Apple Books library."""
        book_clean_map = {}
        for b_id, b in self.books.items():
            ct = b["clean_title"].lower()
            if ct:
                book_clean_map[ct] = b

        for d in self.downloads:
            ct = d["clean_title"].lower()
            matched_book = None

            # Exact or substring match
            for b_ct, b in book_clean_map.items():
                if ct in b_ct or b_ct in ct:
                    matched_book = b
                    break

            if matched_book:
                d["matched_book_id"] = matched_book["asset_id"]
                num_hl = len(matched_book["highlights"])
                d["highlights_count"] = num_hl
                d["apple_progress"] = matched_book["progress"]

                if num_hl >= 5:
                    d["status"] = "DEEP_READ"  # 深度研读
                elif num_hl > 0 or matched_book["progress"] > 10:
                    d["status"] = "ACTIVE_READ" # 正在阅读 / 有批注
                else:
                    d["status"] = "IMPORTED_UNREAD" # 已导入但未读
            else:
                d["matched_book_id"] = None
                d["highlights_count"] = 0
                if d["ext"] == "pdf" and d["was_opened"]:
                    d["status"] = "STANDALONE_PDF_OPENED" # 独立PDF已打开阅读
                else:
                    # Check age in days
                    days_old = (datetime.now().timestamp() - d["download_ts"]) / 86400
                    if days_old > 21:
                        d["status"] = "TSUNDOKU" # 积读（沉睡超3周）
                    else:
                        d["status"] = "RECENT_UNREAD" # 新下载未读

    def get_summary(self):
        if not self.loaded:
            self.load_all()

        total_downloads = len(self.downloads)
        zlib_downloads = sum(1 for d in self.downloads if d["is_zlib"])
        total_in_books = len(self.books)
        total_highlights = len(self.annotations)
        books_with_highlights = sum(1 for b in self.books.values() if len(b["highlights"]) > 0)

        # Status breakdown of downloads
        status_counts = {}
        for d in self.downloads:
            s = d["status"]
            status_counts[s] = status_counts.get(s, 0) + 1

        # Top highlighted books
        top_books = sorted(
            [b for b in self.books.values() if len(b["highlights"]) > 0],
            key=lambda x: len(x["highlights"]),
            reverse=True
        )[:15]

        # Top categories / themes inferred
        theme_buckets = {
            "哲学与心智修行": ["克里希那穆提", "庄子", "金刚经", "道德经", "南怀瑾", "曾仕强", "塞涅卡", "鲁米", "心学", "王阳明"],
            "底层思维与心智模型": ["汤质", "刘润", "纳瓦尔", "有限与无限", "卡斯", "吴军", "见识", "底层逻辑", "人间清醒"],
            "风险、周期与投资": ["反脆弱", "塔勒布", "估值原理", "周洛华", "周期", "霍华德", "马克斯", "康波", "周金涛", "金钱心理学", "投资"],
            "认知探索与科学": ["事实", "人工智能", "维纳", "休谟", "人类理解", "光明"]
        }

        theme_counts = {k: 0 for k in theme_buckets}
        for b in self.books.values():
            text_to_check = f"{b['title']} {b['author']}"
            for theme, keywords in theme_buckets.items():
                if any(kw in text_to_check for kw in keywords):
                    theme_counts[theme] += len(b["highlights"]) or 1

        return {
            "total_downloads": total_downloads,
            "zlib_downloads": zlib_downloads,
            "total_apple_books": total_in_books,
            "books_with_highlights": books_with_highlights,
            "total_highlights": total_highlights,
            "download_status_funnel": status_counts,
            "tsundoku_rate": round((status_counts.get("TSUNDOKU", 0) / max(1, total_downloads)) * 100, 1),
            "top_highlighted_books": [
                {
                    "title": b["clean_title"] or b["title"],
                    "full_title": b["title"],
                    "author": b["author"],
                    "highlights": len(b["highlights"]),
                    "last_open": b["last_open"]
                }
                for b in top_books
            ],
            "theme_distribution": theme_counts
        }

    def get_daily_recall(self, count=3, seed=None):
        """Pick high-signal highlights for daily contemplation."""
        if not self.loaded:
            self.load_all()

        # Filter out short fragments (<25 chars) and trivial lines
        valid_anns = []
        for ann in self.annotations:
            txt = ann["text"].strip()
            if len(txt) >= 28 and not txt.startswith("第") and not txt.isdigit():
                book = self.books.get(ann["asset_id"])
                valid_anns.append({
                    "quote": txt,
                    "note": ann.get("note"),
                    "book_title": book["clean_title"] if book else "未知书目",
                    "author": book["author"] if book else "佚名",
                    "created_at": ann["created_at"]
                })

        if not valid_anns:
            return []

        rnd = random.Random(seed or datetime.now().strftime('%Y%m%d'))
        sample_count = min(count, len(valid_anns))
        return rnd.sample(valid_anns, sample_count)

    def get_tsundoku_diagnostics(self, limit=10):
        """Diagnose dormant / unread books and suggest actions."""
        if not self.loaded:
            self.load_all()

        dormant = [d for d in self.downloads if d["status"] in ("TSUNDOKU", "RECENT_UNREAD")]
        # Sort by download time desc
        dormant.sort(key=lambda x: x["download_ts"], reverse=True)

        diagnosed = []
        for d in dormant[:limit]:
            days = int((datetime.now().timestamp() - d["download_ts"]) / 86400)
            suggestion = "速览目录或前言（15分钟），决定保留或归档"
            if d["size_mb"] > 40:
                suggestion = "大体积扫描版PDF，建议在iPad或大屏粗读，或用AI提取核心框架"
            elif days > 60:
                suggestion = "沉睡超2个月，动机可能已过期，建议痛快移入归档区或断舍离"

            diagnosed.append({
                "title": d["clean_title"] or d["title"],
                "author": d["author"],
                "format": d["ext"].upper(),
                "size": f"{d['size_mb']}MB",
                "days_dormant": days,
                "suggestion": suggestion
            })
        return diagnosed

    def export_markdown_vault(self, output_dir=None):
        """Export all books and notes to an Obsidian-ready Markdown folder."""
        if not self.loaded:
            self.load_all()

        out_path = Path(output_dir or os.path.join(self.downloads_dir, "reading-os", "vault"))
        out_path.mkdir(parents=True, exist_ok=True)

        exported_count = 0
        for asset_id, book in self.books.items():
            if not book["highlights"]:
                continue

            safe_title = re.sub(r'[\\/*?:"<>|]', "_", book["clean_title"] or book["title"])
            file_path = out_path / f"{safe_title}.md"

            content = []
            content.append("---")
            content.append(f'title: "{book["title"]}"')
            content.append(f'author: "{book["author"]}"')
            content.append(f'genre: "{book["genre"]}"')
            content.append(f'total_highlights: {len(book["highlights"])}')
            content.append(f'last_opened: "{book["last_open"] or ""}"')
            content.append('tags: ["reading-notes", "apple-books"]')
            content.append("---\n")
            content.append(f"# 《{book['title']}》\n")
            content.append(f"**作者**：{book['author']} | **最后阅读**：{book['last_open'] or '未记录'}\n")
            content.append("## 划线与批注精选\n")

            for idx, h in enumerate(book["highlights"], 1):
                date_str = h["created_at"] or ""
                content.append(f"> 📌 **划线 {idx}** ({date_str})")
                content.append(f"> {h['text']}\n")
                if h["note"]:
                    content.append(f"**💭 我的思考**：{h['note']}\n")

            file_path.write_text("\n".join(content), encoding="utf-8")
            exported_count += 1

        return {
            "vault_path": str(out_path),
            "books_exported": exported_count,
            "total_highlights": len(self.annotations)
        }

if __name__ == "__main__":
    os_engine = ReadingOS()
    os_engine.load_all()

    if "--recall" in sys.argv:
        recalls = os_engine.get_daily_recall(3)
        print("\n================== 🌟 每日阅读反刍 (Daily Recall) ==================")
        for i, r in enumerate(recalls, 1):
            print(f"\n【{i}】《{r['book_title']}》 ({r['author']})")
            print(f"“{r['quote']}”")
            if r['note']:
                print(f"  └─ 个人批注：{r['note']}")
        print("\n===================================================================\n")
    else:
        summary = os_engine.get_summary()
        print(json.dumps(summary, ensure_ascii=False, indent=2))
