# -*- coding: utf-8 -*-
"""构建脚本：校验题库、生成拼音、把数据注入 HTML 模板，输出单文件网页。"""
import json
import re
import sys
from pathlib import Path

from pypinyin import Style, pinyin

from poems_data import DATA

ROOT = Path(__file__).parent
HAN = re.compile(r"^[\u4e00-\u9fff]+$")
LENS = (5, 6, 7)


def main():
    items, bad = [], []
    for title, author, dynasty, kind, lines in DATA:
        for line in lines:
            if not HAN.match(line) or len(line) not in LENS:
                bad.append(f"《{title}》{line} len={len(line)}")
                continue
            items.append(
                {"l": line, "t": title, "a": author, "d": dynasty, "k": kind}
            )

    if bad:
        print("[WARN] 已跳过不合规句子：")
        for b in bad:
            print("   ", b)

    seen, rows = set(), []
    for it in items:
        if it["l"] in seen:
            continue
        seen.add(it["l"])
        rows.append(it)

    chars = sorted({c for p in rows for c in p["l"]})
    py = {}
    for ch in chars:
        r = pinyin(ch, style=Style.TONE, heteronym=False, errors="ignore")
        py[ch] = r[0][0] if r and r[0] else ""

    tpl = (ROOT / "template.html").read_text(encoding="utf-8")
    out = (
        tpl.replace("__POEMS__", json.dumps(rows, ensure_ascii=False, separators=(",", ":")))
        .replace("__PINYIN__", json.dumps(py, ensure_ascii=False, separators=(",", ":")))
    )
    target = ROOT.parent / "gaokao.html"
    target.write_text(out, encoding="utf-8")

    print(f"篇目 {len(DATA)} 篇 / 句子 {len(rows)} 句 / 字池 {len(chars)} 字")
    for n in LENS:
        print(f"  {n} 字：{sum(1 for p in rows if len(p['l']) == n)} 句")
    print(f"输出 -> {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
