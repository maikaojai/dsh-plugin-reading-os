#!/usr/bin/env python3
"""
ReadingOS MCP Server
Model Context Protocol (MCP) compliant server over stdio.
Works with: DeepSeekHarness, Antigravity, Claude Desktop, Cursor.
"""

import sys
import json
import logging
from core import ReadingOS

logging.basicConfig(level=logging.ERROR, stream=sys.stderr)

engine = None

def get_engine():
    global engine
    if engine is None:
        engine = ReadingOS()
        engine.load_all()
    return engine

TOOLS = [
    {
        "name": "get_reading_overview",
        "description": "获取用户的整体阅读操作系统大盘数据，包括下载量、Apple Books藏书量、4400+划线分布、阅读漏斗（已精读/独立PDF阅读/积读率）、四大主题分布与最常研读书单。",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_book_highlights",
        "description": "按书名模糊查询某本书在 Apple Books 中的所有划线高亮、批注和阅读记录。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "book_title": {
                    "type": "string",
                    "description": "要查询的书名关键词（如'最初和最终的自由'、'估值原理'、'关于说话的一切'）"
                },
                "limit": {
                    "type": "integer",
                    "description": "返回划线的最大条数，默认50",
                    "default": 50
                }
            },
            "required": ["book_title"]
        }
    },
    {
        "name": "search_highlights",
        "description": "在全库 4400+ 条划线中全文语义/关键词检索，寻找跨书籍的观点、概念碰撞（如搜索'周期'、'心学'、'逻辑'、'逆向'等）。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "检索关键词"
                },
                "limit": {
                    "type": "integer",
                    "description": "返回条数，默认15",
                    "default": 15
                }
            },
            "required": ["keyword"]
        }
    },
    {
        "name": "get_daily_recall",
        "description": "抽取 1-5 条高启发性的划线作为每日反思/反刍卡片，附带作者与上下文，供 AI 结合用户今日工作/心境进行启发式提问。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "count": {
                    "type": "integer",
                    "description": "抽取条数，默认3",
                    "default": 3
                }
            }
        }
    },
    {
        "name": "diagnose_tsundoku",
        "description": "分析已下载但长期未读（积读）的书籍清单，提供阅读阻力诊断与断舍离/15分钟试读建议。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "诊断数量，默认10",
                    "default": 10
                }
            }
        }
    },
    {
        "name": "get_concept_network",
        "description": "获取跨书核心主题网络（如'放下与破执'、'本质与底层'、'风险与期权'、'规律与辩证'、'知行与实践'、'自由与觉察'），返回跨不同书目的观点对照与共鸣，供 AI 开展多书综合研读与碰撞分析。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "concept_id": {
                    "type": "string",
                    "description": "概念标识：detachment(放下与破执), essence(本质与底层), uncertainty(风险与期权), law_dialectic(规律与辩证), action_practice(知行与实践), freedom(自由与觉察)。留空则返回所有概念列表。"
                }
            }
        }
    },
    {
        "name": "export_to_markdown",
        "description": "将所有图书的划线与批注一键全量导出为 Obsidian/Logseq 兼容的 Markdown 知识库文件夹。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "output_dir": {
                    "type": "string",
                    "description": "导出目标目录，留空则默认导出到 reading-os/vault"
                }
            }
        }
    }
]

def handle_tool_call(name, args):
    eng = get_engine()

    if name == "get_reading_overview":
        res = eng.get_summary()
        return json.dumps(res, ensure_ascii=False, indent=2)

    elif name == "get_book_highlights":
        query = args.get("book_title", "").lower().strip()
        limit = args.get("limit", 50)
        matched = []
        for b in eng.books.values():
            if query in b["title"].lower() or query in b["clean_title"].lower():
                matched.append(b)

        if not matched:
            return f"未找到书名包含 '{query}' 的图书。"

        output = []
        for b in matched[:3]:
            output.append(f"### 《{b['title']}》 - {b['author']}")
            output.append(f"进度：{b['progress']}% | 划线条数：{len(b['highlights'])} | 最后阅读：{b['last_open'] or '未记录'}\n")
            for i, h in enumerate(b["highlights"][:limit], 1):
                date_tag = f" ({h['created_at']})" if h['created_at'] else ""
                output.append(f"{i}. “{h['text']}”{date_tag}")
                if h['note']:
                    output.append(f"   💬 我的思考：{h['note']}")
            output.append("\n" + "-"*40 + "\n")
        return "\n".join(output)

    elif name == "search_highlights":
        kw = args.get("keyword", "").lower().strip()
        limit = args.get("limit", 15)
        hits = []
        for ann in eng.annotations:
            txt = ann["text"]
            note = ann.get("note") or ""
            if kw in txt.lower() or kw in note.lower():
                book = eng.books.get(ann["asset_id"])
                hits.append({
                    "book": book["clean_title"] if book else "未知书籍",
                    "author": book["author"] if book else "",
                    "quote": txt,
                    "note": note if note else None,
                    "date": ann["created_at"]
                })
                if len(hits) >= limit:
                    break

        if not hits:
            return f"在 4400+ 条划线中未检索到关键词 '{kw}'。"

        output = [f"🔍 关键词【{kw}】命中 {len(hits)} 条划线：\n"]
        for i, hit in enumerate(hits, 1):
            output.append(f"{i}. 《{hit['book']}》({hit['author']})")
            output.append(f"   “{hit['quote']}”")
            if hit['note']:
                output.append(f"   💭 批注：{hit['note']}")
            output.append("")
        return "\n".join(output)

    elif name == "get_daily_recall":
        count = args.get("count", 3)
        recalls = eng.get_daily_recall(count)
        output = ["🌟 今日阅读反刍与认知唤醒：\n"]
        for i, r in enumerate(recalls, 1):
            output.append(f"【卡片 {i}】《{r['book_title']}》 - {r['author']}")
            output.append(f"“{r['quote']}”")
            if r['note']:
                output.append(f"   💭 当时批注：{r['note']}")
            output.append("   🤔 思考建议：这句话在当下的工作或生活情境中，是否有了新的意义？\n")
        return "\n".join(output)

    elif name == "get_concept_network":
        cid = args.get("concept_id", "").strip().lower()
        clusters = {
            "detachment": {"name": "放下与破执", "count": 85, "books": 12, "samples": [
                {"book": "金剛經白話講座", "author": "王思迅", "quote": "所有的「法」，从最高意义来说，都是行动的方法、实践的体悟，是内在圆满自在的心，以及放下的能力。"},
                {"book": "纳瓦尔宝典", "author": "埃里克·乔根森", "quote": "要直面现实，就要放下自我，消除自我意识，忘记自我判断，平复自我情绪。"},
                {"book": "最初和最终的自由", "author": "克里希那穆提", "quote": "真相无法靠别人给你。你必须自己去发现它。倾听是有艺术的，必须舍弃所有的偏见和预设。"}
            ]},
            "essence": {"name": "本质与底层", "count": 87, "books": 21, "samples": [
                {"book": "天幕红尘", "author": "豆豆", "quote": "其本质是‘更适应条件’和‘更符合需要’的意思。见路不走，实事求是。"},
                {"book": "底层逻辑", "author": "刘润", "quote": "这个世界上，只有一种真正的英雄主义，那就是认清了生活的真相后还依然热爱它。"},
                {"book": "道德经", "author": "老子", "quote": "人如何能够层层超越？当你逐渐淡泊于外物，且使心灵越来越宁静、越来越纯正的时候，天道的真相终将大显。"}
            ]},
            "uncertainty": {"name": "风险与期权", "count": 75, "books": 10, "samples": [
                {"book": "估值原理", "author": "周洛华", "quote": "估值不仅是对资产未来现金流的折现，更是在不确定性中为风险与期权定价的艺术。"},
                {"book": "原则", "author": "瑞·达利欧", "quote": "知道自己在什么时候不能有明确的意见，不急于下结论。通过平衡风险来保持较大的回报，并降低下行波动。"},
                {"book": "薛兆丰经济学讲义", "author": "薛兆丰", "quote": "正是因为利息是对人们延迟消费、接受不确定性的一种补偿，只要把时间因素考虑在内，收取利息就是天经地义的。"}
            ]},
            "law_dialectic": {"name": "规律与辩证", "count": 80, "books": 16, "samples": [
                {"book": "天幕红尘", "author": "豆豆", "quote": "佛法才让你依法不依人，马克思主义才跟你说事物规律不以人的意志为转移。实事求是才是真科学。"},
                {"book": "老子他说", "author": "南怀瑾", "quote": "人法地，地法天，天法道，道法自然。顺应客观大规律，方能在周期中保全自身。"},
                {"book": "毛主席语录", "author": "毛泽东", "quote": "分析的方法就是辩证的方法。所谓分析，就是分析事物的矛盾。不熟悉生活，对于矛盾不真正了解，就不可能有中肯的分析。"}
            ]},
            "action_practice": {"name": "知行与实践", "count": 88, "books": 22, "samples": [
                {"book": "天幕红尘", "author": "豆豆", "quote": "见路不走不是让你非跟别人一样或不一样，是让你以结果对条件的需要去取舍。你的预期果对条件有什么要求，你就去准备这些条件。"},
                {"book": "见识", "author": "吴军", "quote": "注意你的想法，因为它能决定你的行动；注意你的行动，因为它能变成你的习惯；注意你的习惯，因为它能决定你的命运。"},
                {"book": "关于说话的一切", "author": "汤质", "quote": "一个命题的有效性在根本上取决于它与整个命题网络的关系，我们利用这种整体的融贯性来克服局部的易谬性。"}
            ]},
            "freedom": {"name": "自由与觉察", "count": 128, "books": 21, "samples": [
                {"book": "最初和最终的自由", "author": "克里希那穆提", "quote": "自由不是逃避，也不是选择，自由是在纯粹觉察中完全没有选择的心智状态。"},
                {"book": "天幕红尘", "author": "豆豆", "quote": "自由！就是你不在公众视野里，没有公众评价，没有公众要求，没人知道也没人在意你是谁。"},
                {"book": "底层逻辑", "author": "刘润", "quote": "本金（1+收益率）^时间 - 欲望 = 财富自由。只要非劳动收入大于消费欲望，就达到了内心的从容自由。"}
            ]}
        }
        if cid and cid in clusters:
            return json.dumps({cid: clusters[cid]}, ensure_ascii=False, indent=2)
        return json.dumps(clusters, ensure_ascii=False, indent=2)

    elif name == "diagnose_tsundoku":
        limit = args.get("limit", 10)
        diags = eng.get_tsundoku_diagnostics(limit)
        return json.dumps(diags, ensure_ascii=False, indent=2)

    elif name == "export_to_markdown":
        out_dir = args.get("output_dir")
        res = eng.export_markdown_vault(out_dir)
        return json.dumps(res, ensure_ascii=False, indent=2)

    return f"未知工具: {name}"

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            req = json.loads(line)
        except Exception:
            continue

        method = req.get("method")
        msg_id = req.get("id")

        if method == "initialize":
            res = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "reading-os",
                        "version": "2.0.0"
                    }
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "notifications/initialized":
            pass

        elif method == "tools/list":
            res = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": TOOLS
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})
            try:
                content = handle_tool_call(name, args)
                res = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": content
                            }
                        ]
                    }
                }
            except Exception as e:
                res = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "isError": True,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error executing {name}: {str(e)}"
                            }
                        ]
                    }
                }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
