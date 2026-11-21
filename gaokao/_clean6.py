# -*- coding: utf-8 -*-
"""一次性脚本：从 poems_data.py 中剔除不成句的六字串。

剔除标准：不是完整单句——包括
  1. 从长句中间截断、离开上下文读不通的碎片
  2. 引语标记/叹词被并进句子的（"孔子曰三人行""呜呼盛衰之理"）
  3. 两个短句硬拼成一个六字串的（"六王毕四海一""父母在不远游"）
"""
import re
import sys
from pathlib import Path

DROP = [
    # 《师说》"孔子曰：三人行，则必有我师"——引语标记混入
    "孔子曰三人行",
    # 《子路、曾皙、冉有、公西华侍坐》"夫子喟然叹曰：吾与点也"——只有引导语
    "夫子喟然叹曰",
    # 《阿房宫赋》"六王毕，四海一"为两句；"嗟乎！一人之心，千万人之心也"为残句
    "六王毕四海一",
    "蜀山兀阿房出",
    "嗟乎一人之心",
    "千万人之心也",
    # 《六国论》"或曰：六国互丧"引语标记；"薪不尽，火不灭"为两句
    "或曰六国互丧",
    "薪不尽火不灭",
    # 《论语》"父母在，不远游"为两句
    "父母在不远游",
    # 《将进酒》"五花马，千金裘"为两句
    "五花马千金裘",
    # 《江城子》"不思量，自难忘""尘满面，鬓如霜""小轩窗，正梳妆""明月夜，短松冈"均为两句
    "不思量自难忘",
    "尘满面鬓如霜",
    "小轩窗正梳妆",
    "明月夜短松冈",
    # 《过秦论》"氓隶之人，而迁徙之徒也""陶朱、猗顿之富"——残
    "而迁徙之徒也",
    "陶朱猗顿之富",
    # 《五代史伶官传序》"呜呼！盛衰之理"——叹词混入
    "呜呼盛衰之理",
    # 《项脊轩志》"儿寒乎？欲食乎？"为两句；"述诸小妹语曰"只有引导语
    "儿寒乎欲食乎",
    "述诸小妹语曰",
    # 《种树郭橐驼传》"甚善，名我固当"为两句
    "甚善名我固当",
    # 《苏幕遮》"燎沉香，消溽暑""故乡遥，何日去"均为两句
    "燎沉香消溽暑",
    "故乡遥何日去",
    # 《青玉案·元夕》"更吹落，星如雨"为两句
    "更吹落星如雨",
    # 《贺新郎》"快投笔，莫题柱"为两句
    "快投笔莫题柱",
    # 《长亭送别》"碧云天，黄花地"为两句
    "碧云天黄花地",
    # 《朝天子·咏喇叭》"曲儿小，腔儿大"为两句
    "曲儿小腔儿大",
]


def main() -> int:
    path = Path(__file__).parent / "poems_data.py"
    text = path.read_text(encoding="utf-8")
    removed, missing = [], []

    for line in DROP:
        token = f'"{line}"'
        if token not in text:
            missing.append(line)
            continue
        # 先尝试"句子, "（行内非末项）
        new = re.sub(r'"' + re.escape(line) + r'",[ \t]*', "", text, count=1)
        if new == text:
            # 行末项：去掉前面的 ", " 和本项
            new = re.sub(r',[ \t]*"' + re.escape(line) + r'"', "", text, count=1)
        if new == text:
            missing.append(line)
            continue
        text = new
        removed.append(line)

    # 清理删除后可能残留的空行与行尾空格
    text = "\n".join(l.rstrip() for l in text.split("\n"))
    path.write_text(text, encoding="utf-8")

    print(f"已删除 {len(removed)} 条")
    for r in removed:
        print("  -", r)
    if missing:
        print(f"[WARN] 未找到 {len(missing)} 条：")
        for m in missing:
            print("  ?", m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
