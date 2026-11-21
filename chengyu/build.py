# -*- coding: utf-8 -*-
"""构建脚本：校验题库、把数据注入模板，输出单文件网页 chengyu.html。"""
import json
import sys
from pathlib import Path

from idioms_data import CHARPY, DICT, HARD, PY, SUPER, VALID

ROOT = Path(__file__).parent
TARGET = ROOT.parent / "chengyu.html"


def main():
    problems = []
    valid = set(VALID.split(","))

    for name, pool in (("HARD", HARD), ("SUPER", SUPER)):
        if len(set(pool)) != len(pool):
            problems.append(f"{name} 有重复条目")
        for w in pool:
            if len(w) != 4:
                problems.append(f"{name} 非四字：{w}")
            if w not in valid:
                problems.append(f"{name} 不在合法表：{w}")
            if w not in DICT:
                problems.append(f"{name} 缺释义：{w}")
            if w not in PY or len(PY[w].split()) != 4:
                problems.append(f"{name} 拼音异常：{w} {PY.get(w)}")
            for ch in w:
                if ch not in CHARPY:
                    problems.append(f"{name} 缺单字拼音：{w} / {ch}")

    if problems:
        print("[ERROR] 题库校验未通过：")
        for p in problems[:30]:
            print("   ", p)
        return 1

    tpl = (ROOT / "template.html").read_text(encoding="utf-8")
    for key, val in (("__HARD__", HARD), ("__SUPER__", SUPER), ("__DICT__", DICT),
                     ("__PY__", PY), ("__CHARPY__", CHARPY)):
        if key not in tpl:
            print(f"[ERROR] 模板缺少占位符 {key}")
            return 1
        tpl = tpl.replace(key, json.dumps(val, ensure_ascii=False, separators=(",", ":")))
    tpl = tpl.replace("__VALID__", json.dumps(",".join(sorted(valid)), ensure_ascii=False))

    TARGET.write_text(tpl, encoding="utf-8")

    print(f"困难档 {len(HARD)} 条 / 超难档 {len(SUPER)} 条（{len(SUPER) / len(HARD):.2f}x）")
    print(f"合法成语 {len(valid)} 条 / 单字拼音 {len(CHARPY)} 字")
    print(f"输出 -> {TARGET}（{TARGET.stat().st_size / 1024:.0f} KB）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
