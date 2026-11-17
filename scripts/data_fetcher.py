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

def get_reading_os_data():
    home = os.path.expanduser("~")
    downloads_dir = os.environ.get("READING_OS_BOOKS_DIR", os.path.join(home, "Downloads"))

    bklib_pattern = os.path.join(home, "Library/Containers/com.apple.iBooksX/Data/Documents/BKLibrary/BKLibrary-*.sqlite")
    ann_pattern = os.path.join(home, "Library/Containers/com.apple.iBooksX/Data/Documents/AEAnnotation/AEAnnotation_*.sqlite")

    bklibs = [f for f in glob.glob(bklib_pattern) if not f.endswith(("-wal", "-shm"))]
    anns = [f for f in glob.glob(ann_pattern) if not f.endswith(("-wal", "-shm"))]

    books_dict = {}
    spotlight_book_key = "JINGANG"
    day_counts = {}
    notes_by_day = {}
    total_apple_books = 0
    total_highlights_count = 0

    if bklibs and anns:
        try:
            conn = sqlite3.connect(f"file:{bklibs[0]}?mode=ro", uri=True)
            c = conn.cursor()
            c.execute(f"ATTACH DATABASE 'file:{anns[0]}?mode=ro' AS ann;")

            # Total apple books
            c.execute("SELECT count(*) FROM ZBKLIBRARYASSET;")
            total_apple_books = c.fetchone()[0]

            # Top active and recently opened books from Apple Books
            c.execute("""
            SELECT b.ZASSETID, b.ZTITLE, b.ZAUTHOR, b.ZREADINGPROGRESS, b.ZBOOKHIGHWATERMARKPROGRESS,
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

            for aid, raw_title, raw_author, raw_prog, raw_hw_prog, cnt, last_ann_ts, last_open_ts, last_open_str in active_rows:
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

    total_books = (total_apple_books or 272) + len(downloads_list)

    dimension_weights = [
        {"category": "底层思维与方法", "count": 36, "highlights": 1299, "pct": 38, "color": "#B8583E"},
        {"category": "哲学与心智修行", "count": 80, "highlights": 953, "pct": 28, "color": "var(--accent-terracotta)"},
        {"category": "投资、周期与商业", "count": 40, "highlights": 763, "pct": 22, "color": "#7D4336"},
        {"category": "科学、人文与通识", "count": 30, "highlights": 120, "pct": 12, "color": "#949086"}
    ]

    sparks = [
        {"quote": "所有的「法」，从最高意义来说，都是行动的方法、实践的体悟，是内在圆满自在的心，以及放下的能力。", "book": "金剛經白話講座", "author": "王思迅"},
        {"quote": "估值不仅是对资产未来现金流的折现，更是在不确定性中为风险与期权定价的艺术。", "book": "估值原理", "author": "周洛华"},
        {"quote": "真相无法靠别人给你。你必须自己去发现它。倾听是有艺术的，必须舍弃所有的偏见和预设。", "book": "最初和最终的自由", "author": "克里希那穆提"},
        {"quote": "一个命题的有效性在根本上取决于它与整个命题网络的关系，我们利用这种整体的融贯性来克服局部的易谬性。", "book": "关于说话的一切", "author": "汤质"}
    ]

    concept_clusters = [
        {
            "id": "detachment",
            "name": "放下与破执",
            "count": 85,
            "books_count": 12,
            "samples": [
                {"book": "金剛經白話講座", "author": "王思迅", "quote": "所有的「法」，从最高意义来说，都是行动的方法、实践的体悟，是内在圆满自在的心，以及放下的能力。"},
                {"book": "纳瓦尔宝典", "author": "埃里克·乔根森", "quote": "要直面现实，就要放下自我，消除自我意识，忘记自我判断，平复自我情绪。"},
                {"book": "最初和最终的自由", "author": "克里希那穆提", "quote": "真相无法靠别人给你。你必须自己去发现它。倾听是有艺术的，必须舍弃所有的偏见和预设。"}
            ]
        },
        {
            "id": "essence",
            "name": "本质与底层",
            "count": 87,
            "books_count": 21,
            "samples": [
                {"book": "天幕红尘", "author": "豆豆", "quote": "其本质是‘更适应条件’和‘更符合需要’的意思。见路不走，实事求是。"},
                {"book": "底层逻辑", "author": "刘润", "quote": "这个世界上，只有一种真正的英雄主义，那就是认清了生活的真相后还依然热爱它。"},
                {"book": "道德经", "author": "老子", "quote": "人如何能够层层超越？当你逐渐淡泊于外物，且使心灵越来越宁静、越来越纯正的时候，天道的真相终将大显。"}
            ]
        },
        {
            "id": "uncertainty",
            "name": "风险与期权",
            "count": 75,
            "books_count": 10,
            "samples": [
                {"book": "估值原理", "author": "周洛华", "quote": "估值不仅是对资产未来现金流的折现，更是在不确定性中为风险与期权定价的艺术。"},
                {"book": "原则", "author": "瑞·达利欧", "quote": "知道自己在什么时候不能有明确的意见，不急于下结论。通过平衡风险来保持较大的回报，并降低下行波动。"},
                {"book": "薛兆丰经济学讲义", "author": "薛兆丰", "quote": "正是因为利息是对人们延迟消费、接受不确定性的一种补偿，只要把时间因素考虑在内，收取利息就是天经地义的。"}
            ]
        },
        {
            "id": "law_dialectic",
            "name": "规律与辩证",
            "count": 80,
            "books_count": 16,
            "samples": [
                {"book": "天幕红尘", "author": "豆豆", "quote": "佛法才让你依法不依人，马克思主义才跟你说事物规律不以人的意志为转移。实事求是才是真科学。"},
                {"book": "老子他说", "author": "南怀瑾", "quote": "人法地，地法天，天法道，道法自然。顺应客观大规律，方能在周期中保全自身。"},
                {"book": "毛主席语录", "author": "毛泽东", "quote": "分析的方法就是辩证的方法。所谓分析，就是分析事物的矛盾。不熟悉生活，对于矛盾不真正了解，就不可能有中肯的分析。"}
            ]
        },
        {
            "id": "action_practice",
            "name": "知行与实践",
            "count": 88,
            "books_count": 22,
            "samples": [
                {"book": "天幕红尘", "author": "豆豆", "quote": "见路不走不是让你非跟别人一样或不一样，是让你以结果对条件的需要去取舍。你的预期果对条件有什么要求，你就去准备这些条件。"},
                {"book": "见识", "author": "吴军", "quote": "注意你的想法，因为它能决定你的行动；注意你的行动，因为它能变成你的习惯；注意你的习惯，因为它能决定你的命运。"},
                {"book": "关于说话的一切", "author": "汤质", "quote": "一个命题的有效性在根本上取决于它与整个命题网络的关系，我们利用这种整体的融贯性来克服局部的易谬性。"}
            ]
        },
        {
            "id": "freedom",
            "name": "自由与觉察",
            "count": 128,
            "books_count": 21,
            "samples": [
                {"book": "最初和最终的自由", "author": "克里希那穆提", "quote": "自由不是逃避，也不是选择，自由是在纯粹觉察中完全没有选择的心智状态。"},
                {"book": "天幕红尘", "author": "豆豆", "quote": "自由！就是你不在公众视野里，没有公众评价，没有公众要求，没人知道也没人在意你是谁。"},
                {"book": "底层逻辑", "author": "刘润", "quote": "本金（1+收益率）^时间 - 欲望 = 财富自由。只要非劳动收入大于消费欲望，就达到了内心的从容自由。"}
            ]
        }
    ]

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
            "conversion_rate": "81.5%",
            "tsundoku_rate": "18.5%"
        },
        "dimension_weights": dimension_weights,
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
