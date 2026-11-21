# -*- coding: utf-8 -*-
"""生成题库：从 THUOCL 词频表 + chinese-xinhua 词典筛出两档成语池，写出 idioms_data.py。

用法：
    python prep_data.py            # 用 data/ 下已有的原始文件
    python prep_data.py --fetch    # 先联网下载原始文件

数据来源：
- 词频排序：THUOCL_chengyu.txt（清华大学开放中文词库，8519 条，按频次降序）
- 释义/拼音/合法性：chinese-xinhua/data/idiom.json（30895 条）
"""
import json
import re
import sys
import urllib.request
from collections import Counter
from pathlib import Path

from pypinyin import Style, pinyin

ROOT = Path(__file__).parent
DATA = ROOT / "data"
THUOCL = DATA / "THUOCL_chengyu.txt"
DICT = DATA / "idiom.json"

URL_THUOCL = "https://raw.githubusercontent.com/thunlp/THUOCL/master/data/THUOCL_chengyu.txt"
URL_DICT = "https://raw.githubusercontent.com/pwxcoo/chinese-xinhua/master/data/idiom.json"

HAN4 = re.compile(r"^[\u4e00-\u9fff]{4}$")

# 网上流传较广、但词频表里排不进去的生僻成语，只进「超难」档
RARE = """
惨绿少年 兰因絮果 焚膏继晷 吉光片羽 光风霁月 空谷足音 沆瀣一气 魑魅魍魉 茕茕孑立 踽踽独行
曲突徙薪 目无全牛 不刊之论 危言危行 弹冠相庆 别无长物 敬谢不敏 人浮于事 惨淡经营 白云苍狗
暴虎冯河 不落窠臼 草蛇灰线 尝鼎一脔 城狐社鼠 樗栎庸材 厝火积薪 箪食瓢饮 得鱼忘筌 鼎铛玉石
斗筲之人 对床夜雨 焚琴煮鹤 凤毛麟角 甘之如饴 膏粱子弟 割席分坐 觥筹交错 管窥蠡测 龟毛兔角
鬼蜮伎俩 含英咀华 汗牛充栋 好整以暇 河清海晏 涸辙之鲋 红叶题诗 呼卢喝雉 狐死首丘 怙恶不悛
画脂镂冰 怀瑾握瑜 黄钟大吕 毁家纾难 浑金璞玉 积毁销骨 掎裳连袂 胶柱鼓瑟 结草衔环 金瓯无缺
锦心绣口 荆钗布裙 鸠占鹊巢 举案齐眉 聚蚊成雷 刻鹄类鹜 苦心孤诣 兰摧玉折 蓝田生玉 老蚌生珠
醴酒不设 梁上君子 林下风气 流金铄石 龙章凤姿 鲁鱼亥豕 履舄交错 马齿徒增 买椟还珠 扪虱而谈
梦笔生花 明眸善睐 木人石心 沐猴而冠 南橘北枳 涅而不缁 牛角挂书 弄璋之喜 鸥鹭忘机 披沙拣金
皮里阳秋 牝鸡司晨 剖腹藏珠 期期艾艾 齐大非偶 前倨后恭 罄竹难书 趋之若鹜 人琴俱亡 阮囊羞涩
三缄其口 色厉内荏 上下其手 少不更事 蛇影杯弓 深藏若虚 升堂入室 师心自用 拾人牙慧 始作俑者
恃才傲物 首鼠两端 数典忘祖 双瞳剪水 吮痈舐痔 硕果仅存 司马青衫 探骊得珠 天女散花 唾面自干
万马齐喑 尾大不掉 文不加点 蜗角虚名 席不暇暖 下车伊始 萧规曹随 信口雌黄 行将就木 虚与委蛇
悬梁刺股 雪泥鸿爪 寻章摘句 睚眦必报 言简意赅 杳如黄鹤 一丘之貉 一衣带水 以邻为壑 倚马可待
饮鸩止渴 蝇营狗苟 郢书燕说 优孟衣冠 余音绕梁 鹬蚌相争 越俎代庖 运斤成风 再作冯妇 凿壁偷光
曾参杀人 债台高筑 枕戈待旦 郑人买履 止戈为武 纸上谈兵 指鹿为马 众口铄金 煮豆燃萁 铸山煮海
庄周梦蝶 锥处囊中 子虚乌有 紫气东来 左支右绌 坐怀不乱 七月在野 白头如新 白首同归 百身莫赎
"""

HARD_N = 1200        # 困难档：词频前 1200
SUPER_EXTRA = 1400   # 超难档：再往后取 1400 条
EXP_MAX = 96         # 释义截断长度


def fetch():
    DATA.mkdir(parents=True, exist_ok=True)
    for url, dst in ((URL_THUOCL, THUOCL), (URL_DICT, DICT)):
        if dst.exists() and dst.stat().st_size > 1000:
            continue
        print("下载", url)
        urllib.request.urlretrieve(url, dst)


def clean_exp(text, word):
    """清掉词典里的残缺符号，压成一行。"""
    s = (text or "").replace("\u3000", " ")
    s = s.replace("～", word).replace("◇", "。").replace("※", "")
    s = re.sub(r"\s+", "", s)
    s = s.strip("。 ")
    if len(s) > EXP_MAX:
        s = s[:EXP_MAX].rstrip("，、；") + "…"
    return s


def main():
    if "--fetch" in sys.argv:
        fetch()

    dic = {}
    for row in json.loads(DICT.read_text(encoding="utf-8")):
        w = row.get("word", "").strip()
        if not HAN4.match(w) or w in dic:
            continue
        exp = clean_exp(row.get("explanation"), w)
        if len(exp) < 8:            # 释义缺失或过短，做不了提示
            continue
        dic[w] = (exp, (row.get("pinyin") or "").strip())

    ranked, seen = [], set()
    for line in THUOCL.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if not parts:
            continue
        w = parts[0].strip()
        if not HAN4.match(w) or w in seen:
            continue
        seen.add(w)
        ranked.append(w)

    common = [w for w in ranked if w in dic]
    hard = common[:HARD_N]
    super_pool = hard + common[HARD_N:HARD_N + SUPER_EXTRA]

    rare_hit, rare_miss = [], []
    for w in RARE.split():
        (rare_hit if w in dic else rare_miss).append(w)

    hard_set = set(hard)
    for w in rare_hit:
        if w not in hard_set:
            super_pool.append(w)
    super_pool = list(dict.fromkeys(super_pool))

    valid = "".join(sorted(dic))

    # 单字拼音：优先用成语整体拼音里的读音（多音字更准），缺失再退回 pypinyin
    votes = {}
    for w in super_pool:
        parts = dic[w][1].split()
        if len(parts) != 4:
            continue
        for ch, syl in zip(w, parts):
            votes.setdefault(ch, Counter())[syl] += 1
    charpy = {}
    for ch in {c for w in super_pool for c in w}:
        if ch in votes:
            charpy[ch] = votes[ch].most_common(1)[0][0]
        else:
            r = pinyin(ch, style=Style.TONE, heteronym=False, errors="ignore")
            charpy[ch] = r[0][0] if r and r[0] else ""

    payload = {
        "HARD": hard,
        "SUPER": super_pool,
        "DICT": {w: dic[w][0] for w in super_pool},
        "PY": {w: dic[w][1] for w in super_pool},
        "CHARPY": charpy,
        "VALID": valid,
    }

    out = ROOT / "idioms_data.py"
    lines = [
        "# -*- coding: utf-8 -*-",
        '"""自动生成，勿手改。改题库请编辑 prep_data.py 后重跑。"""',
        "",
        "HARD = " + json.dumps(payload["HARD"], ensure_ascii=False),
        "",
        "SUPER = " + json.dumps(payload["SUPER"], ensure_ascii=False),
        "",
        "DICT = " + json.dumps(payload["DICT"], ensure_ascii=False, separators=(",", ":")),
        "",
        "PY = " + json.dumps(payload["PY"], ensure_ascii=False, separators=(",", ":")),
        "",
        "CHARPY = " + json.dumps(payload["CHARPY"], ensure_ascii=False, separators=(",", ":")),
        "",
        "# 全部合法四字成语，用逗号分隔（提交时校验用）",
        "VALID = " + json.dumps(",".join(sorted(dic)), ensure_ascii=False),
        "",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")

    print(f"词典可用四字成语 {len(dic)} 条")
    print(f"困难档 {len(hard)} 条")
    print(f"超难档 {len(super_pool)} 条（困难档 {len(hard)} + 扩展 {len(super_pool) - len(hard)}）"
          f"，倍率 {len(super_pool) / len(hard):.2f}x")
    print(f"生僻清单 {len(rare_hit)} 条命中" + (f"，缺 {rare_miss}" if rare_miss else ""))
    print(f"输出 -> {out}（{out.stat().st_size / 1024:.0f} KB）")


if __name__ == "__main__":
    main()
