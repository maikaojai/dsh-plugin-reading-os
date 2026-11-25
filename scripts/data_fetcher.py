#!/usr/bin/env python3
"""
ReadingOS Data Fetcher (Zero-dependency, works for any Mac user)
Extracts Apple Books annotations and Downloads folder metadata dynamically.
"""

import os
import re
import sys
import glob
import json
import sqlite3
from datetime import datetime, timedelta

def locate_apple_books_db():
    home = os.path.expanduser("~")
    bklib_env = os.environ.get("READING_OS_BKLIBRARY_PATH")
    ann_env = os.environ.get("READING_OS_AEANNOTATION_PATH")

    bklib = bklib_env if bklib_env and os.path.exists(bklib_env) else None
    ann = ann_env if ann_env and os.path.exists(ann_env) else None

    if bklib and ann:
        return bklib, ann

    candidates = [
        os.environ.get("READING_OS_APPLE_BOOKS_DIR"),
        os.path.join(home, "Library/Containers/com.apple.iBooksX/Data/Documents"),
        os.path.join(home, "Library/Containers/com.apple.BKAgentService/Data/Documents/iBooks"),
        os.path.join(home, "Library/Containers/Apple Books/Data/Documents")
    ]

    for base in candidates:
        if not base or not os.path.exists(base):
            continue
        if not bklib:
            b_matches = [f for f in glob.glob(os.path.join(base, "BKLibrary/BKLibrary-*.sqlite")) if not f.endswith(("-wal", "-shm"))]
            if not b_matches:
                b_matches = [f for f in glob.glob(os.path.join(base, "BKLibrary*.sqlite")) if not f.endswith(("-wal", "-shm"))]
            if b_matches:
                bklib = b_matches[0]
        if not ann:
            a_matches = [f for f in glob.glob(os.path.join(base, "AEAnnotation/AEAnnotation_*.sqlite")) if not f.endswith(("-wal", "-shm"))]
            if not a_matches:
                a_matches = [f for f in glob.glob(os.path.join(base, "AEAnnotation*.sqlite")) if not f.endswith(("-wal", "-shm"))]
            if a_matches:
                ann = a_matches[0]
        if bklib and ann:
            break

    if not bklib:
        fuzzy_b = [f for f in glob.glob(os.path.join(home, "Library/Containers/*Books*/Data/Documents/BKLibrary/BKLibrary-*.sqlite")) if not f.endswith(("-wal", "-shm"))]
        if fuzzy_b:
            bklib = fuzzy_b[0]
    if not ann:
        fuzzy_a = [f for f in glob.glob(os.path.join(home, "Library/Containers/*Books*/Data/Documents/AEAnnotation/AEAnnotation_*.sqlite")) if not f.endswith(("-wal", "-shm"))]
        if fuzzy_a:
            ann = fuzzy_a[0]

    return bklib, ann

def get_reading_os_data():
    home = os.path.expanduser("~")
    downloads_dir = os.environ.get("READING_OS_BOOKS_DIR", os.path.join(home, "Downloads"))

    bklib_path, ann_path = locate_apple_books_db()

    books_dict = {}
    spotlight_book_key = "JINGANG"
    day_counts = {}
    notes_by_day = {}
    total_apple_books = 0
    total_highlights_count = 0

    if bklib_path and ann_path:
        try:
            conn = sqlite3.connect(f"file:{bklib_path}?mode=ro", uri=True)
            c = conn.cursor()
            c.execute("ATTACH DATABASE ? AS ann;", (f"file:{ann_path}?mode=ro",))

            # Total apple books
            c.execute("SELECT count(*) FROM ZBKLIBRARYASSET;")
            total_apple_books = c.fetchone()[0]

            # Top active and recently opened books from Apple Books
            c.execute("""
            SELECT b.ZASSETID, b.ZTITLE, b.ZAUTHOR, b.ZGENRE, b.ZREADINGPROGRESS, b.ZBOOKHIGHWATERMARKPROGRESS,
                   count(a.ZANNOTATIONUUID) as cnt,
                   max(a.ZANNOTATIONCREATIONDATE) as last_annotation_ts,
                   coalesce(b.ZLASTOPENDATE, b.ZLASTENGAGEDDATE) as last_open_ts,
                   datetime(coalesce(b.ZLASTOPENDATE, b.ZLASTENGAGEDDATE) + 978307200, 'unixepoch', 'localtime') as last_open_str
            FROM ZBKLIBRARYASSET b
            LEFT JOIN ann.ZAEANNOTATION a ON b.ZASSETID = a.ZANNOTATIONASSETID AND a.ZANNOTATIONDELETED = 0 AND a.ZANNOTATIONSELECTEDTEXT IS NOT NULL
            WHERE b.ZTITLE IS NOT NULL
            GROUP BY b.ZASSETID
            ORDER BY max(coalesce(b.ZLASTOPENDATE, 0), coalesce(b.ZLASTENGAGEDDATE, 0), coalesce(max(a.ZANNOTATIONCREATIONDATE), 0)) DESC;
            """)
            active_rows = c.fetchall()
            if active_rows:
                spotlight_book_key = active_rows[0][0]

            for aid, raw_title, raw_author, raw_genre, raw_prog, raw_hw_prog, cnt, last_ann_ts, last_open_ts, last_open_str in active_rows:
                if not raw_title:
                    continue
                hl_rows = []
                if cnt > 0:
                    c.execute("""
                    SELECT ZANNOTATIONSELECTEDTEXT, ZANNOTATIONNOTE,
                           datetime(ZANNOTATIONCREATIONDATE + 978307200, 'unixepoch', 'localtime')
                    FROM ann.ZAEANNOTATION
                    WHERE ZANNOTATIONASSETID = ? AND ZANNOTATIONDELETED = 0 AND ZANNOTATIONSELECTEDTEXT IS NOT NULL
                    ORDER BY ZANNOTATIONCREATIONDATE DESC;
                    """, (aid,))
                    hl_rows = c.fetchall()

                clean_title = raw_title.strip()
                author_clean = (raw_author or "未知作者").strip()

                # Extract real reading progress directly from Apple Books database
                prog_val = raw_prog if (raw_prog is not None and raw_prog > 0) else raw_hw_prog
                if prog_val is not None and prog_val > 0:
                    if prog_val >= 0.995:
                        progress = 100
                    else:
                        progress = int(prog_val * 100)
                else:
                    progress = 100 if cnt >= 50 else min(95, max(15, cnt * 2))

                b_obj = {
                    "key": aid,
                    "title": clean_title,
                    "author": author_clean,
                    "genre": (raw_genre or "").strip(),
                    "progress": progress,
                    "highlights_count": len(hl_rows),
                    "sample_quote": hl_rows[0][0].strip() if hl_rows else "",
                    "last_open_time": last_open_str if last_open_str else (hl_rows[0][2] if hl_rows else ""),
                    "highlights": [
                        {"text": r[0].strip(), "note": r[1].strip() if r[1] else None, "time": r[2]}
                        for r in hl_rows
                    ]
                }
                books_dict[aid] = b_obj

                # Backward compatibility aliases for spotlight and companions
                if "金剛經白話講座" in clean_title and "JINGANG" not in books_dict:
                    books_dict["JINGANG"] = b_obj
                elif "估值原理" in clean_title and "VALUATION" not in books_dict:
                    books_dict["VALUATION"] = b_obj
                elif "老子他说" in clean_title and "LAOZI" not in books_dict:
                    books_dict["LAOZI"] = b_obj
                elif "最初和最终的自由" in clean_title and "FREEDOM" not in books_dict:
                    books_dict["FREEDOM"] = b_obj

            # Heatmap counts
            c.execute("""
            SELECT strftime('%Y-%m-%d', datetime(ZANNOTATIONCREATIONDATE + 978307200, 'unixepoch', 'localtime')) as day, count(*)
            FROM ann.ZAEANNOTATION
            WHERE ZANNOTATIONDELETED = 0 AND ZANNOTATIONSELECTEDTEXT IS NOT NULL
            GROUP BY day
            ORDER BY day ASC;
            """)
            day_counts = dict(c.fetchall())

            # Total annotations
            c.execute("SELECT count(*) FROM ann.ZAEANNOTATION WHERE ZANNOTATIONDELETED = 0 AND ZANNOTATIONSELECTEDTEXT IS NOT NULL;")
            total_highlights_count = c.fetchone()[0]

            # Notes by day
            c.execute("""
            SELECT date(datetime(ZANNOTATIONCREATIONDATE + 978307200, 'unixepoch', 'localtime')) as dt,
                   ZANNOTATIONSELECTEDTEXT, b.ZTITLE
            FROM ann.ZAEANNOTATION a
            JOIN ZBKLIBRARYASSET b ON a.ZANNOTATIONASSETID = b.ZASSETID
            WHERE a.ZANNOTATIONDELETED = 0 AND a.ZANNOTATIONSELECTEDTEXT IS NOT NULL
            ORDER BY a.ZANNOTATIONCREATIONDATE DESC;
            """)
            for r in c.fetchall():
                dt = r[0]
                if dt not in notes_by_day:
                    notes_by_day[dt] = []
                if len(notes_by_day[dt]) < 5:
                    notes_by_day[dt].append({"text": r[1].strip(), "book": r[2].split('（')[0].split('：')[0]})

            conn.close()
        except Exception as e:
            sys.stderr.write(f"SQLite reading notice: {e}\n")

    # Heatmap weeks
    end_date = datetime.now()
    start_date = end_date - timedelta(days=364)
    while start_date.weekday() != 6:
        start_date -= timedelta(days=1)

    heatmap_weeks = []
    cur = start_date
    while cur <= end_date:
        week = []
        for d in range(7):
            d_str = cur.strftime('%Y-%m-%d')
            week.append({"date": d_str, "count": day_counts.get(d_str, 0)})
            cur += timedelta(days=1)
        heatmap_weeks.append(week)

    # Downloads scan
    cutoff_30d = datetime.now().timestamp() - (30 * 86400)
    book_exts = (".epub", ".pdf", ".mobi", ".azw3")
    downloads_list = []
    recent_30d_files = []
    unread_queue = []

    if os.path.exists(downloads_dir):
        for f in os.listdir(downloads_dir):
            if f.lower().endswith(book_exts):
                fpath = os.path.join(downloads_dir, f)
                if os.path.isfile(fpath):
                    downloads_list.append(f)
                    mtime = os.path.getmtime(fpath)
                    if mtime >= cutoff_30d:
                        recent_30d_files.append((mtime, f))
                    
                    if 'z-lib' in f.lower() or 'zlibrary' in f.lower() or '1lib' in f.lower():
                        clean_n = f.replace(".epub", "").replace(".pdf", "").replace(".mobi", "")
                        clean_n = clean_n.split("(")[0].split("（")[0].strip()
                        if len(clean_n) > 1:
                            unread_queue.append({
                                "title": clean_n,
                                "ext": f.split(".")[-1].upper()
                            })

    recent_30d_files.sort(reverse=True)
    
    BOOK_DESCRIPTIONS = {
        "也无风雨也无晴": "出版大家沈昌文晚年口述自传，以幽默自嘲的口吻记录半生出版风云与文人交游往事。",
        "电影编剧的秘密": "芦苇与王天兵对谈录，深度解构经典电影剧作法、类型片法则与叙事艺术的内在规律。",
        "樱桃园": "契诃夫最后一部绝唱戏剧，以诗意而哀伤的笔触描摹贵族阶级的凋零与新旧时代的交替宿命。",
        "等待戈多": "萨缪尔·贝克特荒诞派戏剧巅峰之作，探讨人类在虚无、等待与存在绝境中的永恒叩问。",
        "A Very Easy Death": "波伏瓦记录母亲最后病榻时光的真实散文，直面肉身衰朽、亲情羁绊与死亡的残酷真相。",
        "卓别林自传": "电影大师查尔斯·卓别林亲笔自传，记录从伦敦底层贫民窟到好莱坞默片巅峰的传奇生平与艺术思考。",
        "最好的告别": "哈佛外科专家阿图·葛文德临床力作，探讨面对衰老与死亡时，医学局限与人之尊严的抉择。",
        "切尔诺贝利的祭祷": "阿列克谢耶维奇深入切尔诺贝利灾区访谈录，记录灾难背后平凡人的声音、恐惧与无尽创痛。",
        "重负与神恩": "法国哲学家西蒙娜·薇依灵性沉思录，探讨痛苦、重负、恩典与超脱凡俗的纯粹心智境界。",
        "聪明人的个人成长": "围绕“真实、爱、能量”三大基本原则，构建系统化自我进化框架，涵盖习惯重塑、清醒自主与心智成长。",
        "唤醒创作力": "针对创作瓶颈与心智卡顿，通过晨间随笔与灵性觉察练习，打通内在阻滞，唤醒与生俱来的原创动力。",
        "富有创造力的心灵": "探讨心智如何从成见、经验与传统惯性中解脱，恢复本真敏锐与深刻觉察，直达生命的创造力之源。",
        "此生何为": "深刻叩问生存的终极意义，直指现代人在关系、野心与焦虑中的冲突，引导回归纯粹观察。",
        "关系的真谛": "剖析人与人之间的心理防线、占有欲与依赖心理，揭示在自我认识中建立真实关系的可能。",
        "你就是世界": "汇集与心理学家及各界探索者的真实对谈，逐一剖析恐惧、爱、寂寞与生命质地。"
    }

    def parse_book_metadata(fname, mtime):
        ext = os.path.splitext(fname)[1].lstrip('.').upper()
        base = os.path.splitext(fname)[0]
        base = re.sub(r'\s*[\(\[][^()\[\]]*(?:z-lib|1lib|zlibrary)[^()\[\]]*[\)\]]', '', base, flags=re.I).strip()
        author = '待开启研读'
        title = base
        if base.endswith(')') or base.endswith('）'):
            depth = 0
            split_idx = -1
            for i in range(len(base)-1, -1, -1):
                ch = base[i]
                if ch in (')', '）'):
                    depth += 1
                elif ch in ('(', '（'):
                    depth -= 1
                    if depth == 0:
                        split_idx = i
                        break
            if split_idx > 0:
                title_part = base[:split_idx].strip()
                author_part = base[split_idx+1:-1].strip()
                if title_part:
                    title = title_part
                a = author_part
                a = re.sub(r'\[.*?\]', '', a)
                a = re.sub(r'【.*?】', '', a)
                a = re.sub(r'[\(（][A-Za-z\s]+[\)）]', '', a)
                a = a.replace('［', '【').replace('］', '】')
                a = a.replace('（俄罗斯）', '【俄】').replace('(俄罗斯)', '【俄】')
                a = re.sub(r'[◎]', '', a)
                if '著' in a:
                    a = a.split('著')[0].strip()
                if '译' in a and '【' not in a:
                    a = a.split('译')[0].strip()
                a = re.split(r'[,，;；]', a)[0].strip()
                a = re.sub(r'(?:author|etc\.|\d{4}-).*', '', a, flags=re.I).strip()
                a = ' '.join(a.split())
                if a:
                    author = a
        if '=' in title:
            title = title.split('=')[0].strip()
        m_book = re.search(r'《([^》]+)》', title)
        if m_book:
            title = m_book.group(1).strip()
        title = re.sub(r'\s+', ' ', title).strip()
        if '芦苇' in author and '王天兵' in author:
            author = '芦苇 / 王天兵'
        elif '沈昌文' in author:
            author = '沈昌文'
        elif '贝克特' in author:
            author = '【爱尔兰】萨缪尔·贝克特'
        elif '阿图' in author:
            author = '【美】阿图·葛文德'
        elif '朱莉娅·卡梅伦' in author:
            author = '【美】朱莉娅·卡梅伦'
        elif '西蒙娜•薇依' in author or '西蒙娜·薇依' in author:
            author = '【法】西蒙娜·薇依'
        elif '阿列克谢耶维奇' in author:
            author = '【白俄】S·A·阿列克谢耶维奇'
        elif '契诃夫' in author:
            author = '【俄】安东·契诃夫'
        elif '史蒂夫' in author:
            author = '【美】史蒂夫·帕弗利纳'
        dt = datetime.fromtimestamp(mtime)
        delta_days = (datetime.now().date() - dt.date()).days
        if delta_days == 0:
            time_tag = '今天'
        elif delta_days == 1:
            time_tag = '昨天'
        else:
            time_tag = f'{delta_days}天前'
        desc = None
        for k, v in BOOK_DESCRIPTIONS.items():
            if k in title:
                desc = v
                break
        if not desc:
            desc = f'下载入库：《{title}》，待开启深度阅读与划线记录。'
        return {
            'title': title,
            'author': author,
            'tag': f'{ext} · {time_tag}',
            'desc': desc
        }

    recent_downloads = [
        parse_book_metadata(f, m) for m, f in recent_30d_files
    ]
    if not recent_downloads:
        recent_downloads = [
            {
                "title": "聪明人的个人成长",
                "author": "【美】史蒂夫·帕弗利纳",
                "tag": "EPUB · 5天前",
                "desc": "围绕“真实、爱、能量”三大基本原则，构建系统化自我进化框架，涵盖习惯重塑、清醒自主与心智成长。"
            },
            {
                "title": "唤醒创作力：写给被卡住的创作者",
                "author": "【美】朱莉娅·卡梅伦",
                "tag": "EPUB · 5天前",
                "desc": "针对创作瓶颈与心智卡顿，通过晨间随笔与灵性觉察练习，打通内在阻滞，唤醒与生俱来的原创动力。"
            }
        ]

    # Deduplicate books by title for accurate statistics
    unique_books = []
    seen_titles = set()
    for b in books_dict.values():
        t = b.get("title", "")
        if t and t not in seen_titles:
            seen_titles.add(t)
            unique_books.append(b)

    # 1. Dynamic Total Books & Download-to-Read Conversion / Tsundoku Rate
    def normalize_title(s):
        s = re.sub(r'\(.*?\)|（.*?）|\[.*?\]|【.*?】', '', s)
        s = re.sub(r'[《》\s·:：\-_=]+', '', s).lower()
        return s

    apple_norm_titles = [(normalize_title(b["title"]), b) for b in unique_books if b.get("title")]
    matched_read = 0
    unmatched_downloads = 0
    for fname in downloads_list:
        meta = parse_book_metadata(fname, 0)
        dl_norm = normalize_title(meta["title"])
        matched_book = None
        if dl_norm:
            for a_norm, b_obj in apple_norm_titles:
                if dl_norm in a_norm or a_norm in dl_norm:
                    matched_book = b_obj
                    break
        if matched_book:
            if matched_book.get("highlights_count", 0) > 0 or matched_book.get("progress", 0) >= 5:
                matched_read += 1
        else:
            unmatched_downloads += 1

    total_books = total_apple_books + unmatched_downloads
    if downloads_list:
        conv_pct = round((matched_read / len(downloads_list)) * 100, 1)
        tsun_pct = round(100.0 - conv_pct, 1)
        conversion_rate_str = f"{conv_pct}%"
        tsundoku_rate_str = f"{tsun_pct}%"
    elif unique_books:
        read_books_cnt = sum(1 for b in unique_books if b.get("highlights_count", 0) > 0 or b.get("progress", 0) >= 5)
        conv_pct = round((read_books_cnt / len(unique_books)) * 100, 1)
        tsun_pct = round(100.0 - conv_pct, 1)
        conversion_rate_str = f"{conv_pct}%"
        tsundoku_rate_str = f"{tsun_pct}%"
    else:
        conversion_rate_str = "0.0%"
        tsundoku_rate_str = "0.0%"

    # 2. Dynamic 4-Dimension Knowledge Asset Weights
    dim_specs = [
        ("底层思维与方法", "#B8583E", ["思维", "逻辑", "认知", "方法", "原则", "说话", "写作", "学习", "系统", "心理", "心智", "习惯", "成长", "效率", "思考", "决策", "沟通"]),
        ("哲学与心智修行", "var(--accent-terracotta)", ["哲学", "佛", "禅", "道", "心经", "金刚", "老子", "庄子", "论语", "传习", "阳明", "修行", "自由", "沉思", "存在", "宗教", "伦理", "心灵", "克里希那", "道德经"]),
        ("投资、周期与商业", "#7D4336", ["投资", "估值", "周期", "经济", "金融", "商业", "股票", "基金", "财务", "管理", "创业", "博弈", "货币", "资本", "资产", "风险", "市场", "巴菲特", "芒格"]),
        ("科学、人文与通识", "#949086", [])
    ]
    dim_stats = [{"category": name, "count": 0, "highlights": 0, "color": color} for name, color, _ in dim_specs]

    for b in unique_books:
        text_for_cls = f"{b.get('title', '')} {b.get('genre', '')} {b.get('author', '')}".lower()
        assigned = 3  # default to general humanities/science
        for idx in range(3):
            if any(kw in text_for_cls for kw in dim_specs[idx][2]):
                assigned = idx
                break
        dim_stats[assigned]["count"] += 1
        dim_stats[assigned]["highlights"] += b.get("highlights_count", 0)

    total_dim_hls = sum(d["highlights"] for d in dim_stats)
    total_dim_cnt = sum(d["count"] for d in dim_stats)
    dimension_weights = []
    for d in dim_stats:
        if total_dim_hls > 0:
            pct = round((d["highlights"] / total_dim_hls) * 100)
        elif total_dim_cnt > 0:
            pct = round((d["count"] / total_dim_cnt) * 100)
        else:
            pct = 25
        dimension_weights.append({
            "category": d["category"],
            "count": d["count"],
            "highlights": d["highlights"],
            "pct": pct,
            "color": d["color"]
        })

    # 3. Dynamic Daily Spark Bookmarks Pool (prioritizing noted & well-formed highlights)
    spark_candidates = []
    for b in unique_books:
        for h in b.get("highlights", []):
            txt = h.get("text", "").strip()
            if 18 <= len(txt) <= 220:
                score = (2 if h.get("note") else 0) + (1 if 30 <= len(txt) <= 130 else 0)
                spark_candidates.append((score, b["title"], b["author"], txt))

    spark_candidates.sort(key=lambda x: x[0], reverse=True)
    sparks = []
    spark_books_seen = set()
    for _, b_title, b_author, txt in spark_candidates:
        if b_title not in spark_books_seen:
            spark_books_seen.add(b_title)
            sparks.append({"quote": txt, "book": b_title, "author": b_author})
            if len(sparks) >= 20:
                break
    if not sparks:
        sparks = [
            {"quote": "所有的「法」，从最高意义来说，都是行动的方法、实践的体悟，是内在圆满自在的心，以及放下的能力。", "book": "金剛經白話講座", "author": "王思迅"},
            {"quote": "估值不仅是对资产未来现金流的折现，更是在不确定性中为风险与期权定价的艺术。", "book": "估值原理", "author": "周洛华"},
            {"quote": "真相无法靠别人给你。你必须自己去发现它。倾听是有艺术的，必须舍弃所有的偏见和预设。", "book": "最初和最终的自由", "author": "克里希那穆提"}
        ]

    # 4. Dynamic Cross-Book Concept Network
    concept_defs = [
        ("detachment", "放下与破执", ["放下", "执着", "执著", "破执", "无住", "舍得", "解脱", "无常", "空性"]),
        ("essence", "本质与底层", ["本质", "底层", "第一性", "真相", "根本", "根源", "逻辑", "前提"]),
        ("uncertainty", "风险与期权", ["风险", "不确定", "期权", "估值", "周期", "波动", "概率", "安全边际", "赔率"]),
        ("law_dialectic", "规律与辩证", ["辩证", "矛盾", "对立", "规律", "自然", "因果", "因缘", "客观"]),
        ("action_practice", "知行与实践", ["知行", "行动", "实践", "践行", "习惯", "磨练", "实事求是", "条件", "方法"]),
        ("freedom", "自由与觉察", ["自由", "觉察", "觉醒", "心灵", "宁静", "自主", "独处", "内心", "从容"])
    ]
    concept_clusters = []
    for cid, cname, kws in concept_defs:
        hit_count = 0
        hit_books = set()
        samples = []
        sample_books_seen = set()
        for b in unique_books:
            for h in b.get("highlights", []):
                txt = h.get("text", "").strip()
                if any(kw in txt for kw in kws):
                    hit_count += 1
                    hit_books.add(b["title"])
                    if 16 <= len(txt) <= 240 and b["title"] not in sample_books_seen and len(samples) < 3:
                        sample_books_seen.add(b["title"])
                        samples.append({"book": b["title"], "author": b["author"], "quote": txt})
        if not samples:
            samples = [{"book": "ReadingOS 提示", "author": "本地书库", "quote": f"当前书库暂无包含「{cname}」关键词的划线，在 Apple Books 中标记后点击同步即可自动聚合。"}]
        concept_clusters.append({
            "id": cid,
            "name": cname,
            "count": hit_count,
            "books_count": len(hit_books),
            "samples": samples
        })

    return {
        "books": books_dict,
        "spotlight_book_key": spotlight_book_key,
        "heatmap_weeks": heatmap_weeks,
        "notes_by_day": notes_by_day,
        "sparks": sparks,
        "recent_downloads": recent_downloads,
        "concept_clusters": concept_clusters,
        "unread_queue": unread_queue[:20],
        "inventory": {
            "total_books": total_books,
            "downloads_30d": len(recent_30d_files),
            "conversion_rate": conversion_rate_str,
            "tsundoku_rate": tsundoku_rate_str
        },
        "dimension_weights": dimension_weights,
        "system_info": {
            "bklibrary_path": bklib_path,
            "annotation_path": ann_path,
            "downloads_dir": downloads_dir,
            "status": "connected" if (bklib_path and ann_path) else "not_found",
            "total_apple_books": total_apple_books,
            "total_highlights": total_highlights_count
        },
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

if __name__ == "__main__":
    data = get_reading_os_data()
    try:
        local_cache = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dashboard", "data.local.json")
        with open(local_cache, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:
        pass
    print(json.dumps(data, ensure_ascii=False))
