# -*- coding: utf-8 -*-
"""构建脚本：校验题库、生成拼音、把数据注入 HTML 模板，输出单文件网页。"""
import json
import re
import sys
from pathlib import Path

from pypinyin import Style, pinyin

from poems_data import EXTRA, TEXTBOOK

ROOT = Path(__file__).parent
HAN = re.compile(r"^[\u4e00-\u9fff]+$")


def collect(rows, source):
    items, bad = [], []
    for title, author, dynasty, lines in rows:
        for line in lines:
            if not HAN.match(line) or len(line) not in (5, 7):
                bad.append(f"{title}《{line}》 len={len(line)}")
                continue
            items.append(
                {"l": line, "t": title, "a": author, "d": dynasty, "s": source}
            )
    return items, bad


def main():
    tb, bad1 = collect(TEXTBOOK, "tb")
    ex, bad2 = collect(EXTRA, "ex")
    bad = bad1 + bad2
    if bad:
        print("[WARN] 已跳过不合规句子：")
        for b in bad:
            print("   ", b)

    # 去重（同一句只保留一条）
    seen, poems = set(), []
    for it in tb + ex:
        if it["l"] in seen:
            continue
        seen.add(it["l"])
        poems.append(it)

    # 拼音表：只覆盖题库出现过的字
    chars = sorted({c for p in poems for c in p["l"]})
    py = {}
    for ch in chars:
        r = pinyin(ch, style=Style.TONE, heteronym=False, errors="ignore")
        py[ch] = r[0][0] if r and r[0] else ""

    tpl = (ROOT / "template.html").read_text(encoding="utf-8")
    out = (
        tpl.replace("__POEMS__", json.dumps(poems, ensure_ascii=False, separators=(",", ":")))
        .replace("__PINYIN__", json.dumps(py, ensure_ascii=False, separators=(",", ":")))
    )
    target = ROOT.parent / "index.html"   # GitHub Pages 入口
    target.write_text(out, encoding="utf-8")

    print(f"课内 {len(tb)} 句 / 课外 {len(ex)} 句 / 合计 {len(poems)} 句")
    print(f"五言 {sum(1 for p in poems if len(p['l'])==5)} 句，七言 {sum(1 for p in poems if len(p['l'])==7)} 句")
    print(f"字池 {len(chars)} 字")
    print(f"输出 -> {target}")


if __name__ == "__main__":
    sys.exit(main())
