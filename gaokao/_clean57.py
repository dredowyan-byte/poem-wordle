# -*- coding: utf-8 -*-
"""一次性脚本：剔除文言文篇目里不成句的五字、七字串。

与 _clean6.py 同一套标准：
  1. 从长句中间截断、离开上下文读不通的碎片
  2. 引语标记 / 叹词被并进句子的
  3. 两个短句硬拼成一个定长串的
只动 文言文（k == "文"）篇目，诗、词、曲的五七言本身就是完整句，不碰。
"""
import re
import sys
from pathlib import Path

DROP = [
    # ---- 五字 ----
    "士大夫之族",       # 《师说》"士大夫之族，曰师曰弟子云者"——话题短语，后面才接谓语
    "戊申晦五鼓",       # 《登泰山记》"戊申晦，五鼓"——时间状语，不成句
    "山多石少土",       # 《登泰山记》"山多石，少土"——两句
    "冰雪无瀑水",       # 《登泰山记》"冰雪，无瀑水"——两句
    "使天下之人",       # 《阿房宫赋》"使天下之人，不敢言而敢怒"——介词短语
    "较秦之所得",       # 《六国论》"较秦之所得，与战胜而得者"——话题短语
    "诸侯之所亡",       # 《六国论》"诸侯之所亡，与战败而亡者"——话题短语
    "有席卷天下",       # 《过秦论》"有席卷天下、包举宇内……之意"——残
    "妪每谓余曰",       # 《项脊轩志》——只有引导语
    "余泣妪亦泣",       # 《项脊轩志》"余泣，妪亦泣"——两句
    "而山上栖鹘",       # 《石钟山记》"而山上栖鹘，闻人声亦惊起"——主语短语
    "因笑谓迈曰",       # 《石钟山记》——只有引导语
    "而言之不详",       # 《石钟山记》"而言之不详"——承前省略，独立读不通
    # ---- 七字 ----
    "歌曰桂棹兮兰桨",   # 《赤壁赋》"歌曰：桂棹兮兰桨"——引导语混入
    "是日观道中石刻",   # 《登泰山记》"是日，观道中石刻"——两句
    "呜呼以赂秦之地",   # 《六国论》"呜呼！以赂秦之地"——叹词混入
    "悲夫有如此之势",   # 《六国论》"悲夫！有如此之势"——叹词混入
    "朝闻道夕死可矣",   # 《论语》"朝闻道，夕死可矣"——两句
    "多可喜亦多可悲",   # 《项脊轩志》"多可喜，亦多可悲"——两句
    "某所而母立于兹",   # 《项脊轩志》"某所，而母立于兹"——两句
    "娘以指叩门扉曰",   # 《项脊轩志》——只有引导语
    "一日大母过余曰",   # 《项脊轩志》——只有引导语
    "又北向不能得日",   # 《项脊轩志》"又北向，不能得日"——两句
    "旦暮吏来而呼曰",   # 《种树郭橐驼传》——只有引导语
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
        new = re.sub(r'"' + re.escape(line) + r'",[ \t]*', "", text, count=1)
        if new == text:
            new = re.sub(r',[ \t]*"' + re.escape(line) + r'"', "", text, count=1)
        if new == text:
            missing.append(line)
            continue
        text = new
        removed.append(line)

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
