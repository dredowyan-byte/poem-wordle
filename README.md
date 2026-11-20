# 名句 Wordle

猜一句古诗词的 Wordle，仿 [chengyu-wordle](https://cheeaun.github.io/chengyu-wordle/) 做的中文版，打开网页就能玩，不用安装。

| 版本 | 入口 | 范围 | 机会 |
| --- | --- | --- | --- |
| 初中版（中考） | [`index.html`](index.html) | 统编版初中课本 + 课外名句，五言 / 七言 | 五言 6 次，七言 7 次 |
| 高中版（高考） | [`gaokao.html`](gaokao.html) | 《高考必背古诗文 60 篇》，五字 / 六字 / 七字，诗词曲与文言文混排 | 五字 6 次，六字 7 次，七字 8 次 |

两版顶部标签栏可以互相跳转。

## 玩法

- 每局随机一句古诗文，格数就是字数
- 提交后每格变色：
  - 绿 = 这个字位置正确
  - 黄 = 这个字在句中，但位置不对
  - 灰 = 这句里没有这个字
- 判定用标准 Wordle 双遍算法，重复字不会多给提示
- 字库里有若干句干扰名句，很多字能同时拼进好几句，只有一句是答案
- 可以用鼠标点字库，也可以直接用输入法打字

其他：每次打开随机一题（最近 24 句不重复）、做不出来可点「换题」、网址后加 `#daily` 可玩当天固定题目、两级求助（作者 → 篇名）、连胜统计、emoji 分享、明暗主题切换。

## 题库

| 版本 | 篇目 | 句子 |
| --- | --- | --- |
| 初中版 | 统编版初中语文（七上—九下）+ 课外名句 | 475 句（课内 385 / 课外 90，出题按 80 / 20 加权） |
| 高中版 | 高考必背古诗文 60 篇 | 1070 句（5 字 308 / 6 字 293 / 7 字 469） |

高中版的《短歌行》《无衣》通篇四言，凑不出 5/6/7 字的句子，未收，故为 58 篇。

## 目录结构

```
index.html            初中版（构建产物）
gaokao.html           高中版（构建产物）
junior/               初中版源码
  poems_data.py       题库：(篇名, 作者, 朝代, [句子...])
  template.html       页面模板，含 __POEMS__ / __PINYIN__ 占位符
  build.py            校验字数 + 生成拼音 + 注入模板
gaokao/               高中版源码（结构同上，题库多一个「文体」字段）
```

## 本地构建

网页是单文件产物，无需服务器，双击 `index.html` 即可。改题库后重新生成：

```bash
pip install pypinyin
cd junior && python build.py     # 输出 ../index.html
cd ../gaokao && python build.py  # 输出 ../gaokao.html
```

构建时会打印不合规的句子（字数不符或含标点），直接跳过。

## 访问统计

页面默认**不加载任何第三方脚本**。要统计访问量，二选一：

**1. GoatCounter（推荐，免费，有面板 + 可在页面显示数字）**

1. 到 https://www.goatcounter.com/signup 注册，选一个站点代码（例如 `dredowyan`）
2. 把 `junior/template.html` 和 `gaokao/template.html` 里的 `const STATS_CODE = "";` 改成 `const STATS_CODE = "dredowyan";`
3. 重新 build 并推送，页面底部就会出现「N 次开局」，面板在 `https://dredowyan.goatcounter.com`

统计不用 cookie，只记路径 / 来源 / 国家，不存 IP。

**2. Cloudflare Web Analytics（要完整报表：来源、地区、路径）**

在 Cloudflare 后台 Web Analytics 里添加站点 `dredowyan-byte.github.io`（不需要改 DNS），把拿到的 `<script>` 粘到两个模板的 `</body>` 前，重新 build。

> GitHub 仓库自带的 Insights → Traffic 只统计 github.com 上的仓库页面，不统计 Pages 站点，看不到玩家人数。

## 许可

代码 MIT。诗句均为公有领域作品。
