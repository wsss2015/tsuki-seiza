"""月の星座ノート：静的サイトを生成する。
python3 build.py [出力先=dist] [--base https://example.com] [--days 30]
毎日1回走らせる（今日のページとトップが入れ替わる）。"""
import sys, os, html
from datetime import datetime, timedelta
from astro import JST, sun_lon, moon_lon, elongation, moon_age, sign_changes

SIGNS = [("aries","おひつじ座","3/21〜4/19"),("taurus","おうし座","4/20〜5/20"),
         ("gemini","ふたご座","5/21〜6/21"),("cancer","かに座","6/22〜7/22"),
         ("leo","しし座","7/23〜8/22"),("virgo","おとめ座","8/23〜9/22"),
         ("libra","てんびん座","9/23〜10/23"),("scorpio","さそり座","10/24〜11/22"),
         ("sagittarius","いて座","11/23〜12/21"),("capricorn","やぎ座","12/22〜1/19"),
         ("aquarius","みずがめ座","1/20〜2/18"),("pisces","うお座","2/19〜3/20")]

# 太陽星座から数えて、月が何番目の部屋にいるか（ソーラーサイン・ハウス）
HOUSES = {
 1:("自分の部屋","気持ちが前を向きやすい日。後回しにしていた自分のことを1つ片づけると、残りの1日が軽くなります。"),
 2:("お金と持ち物の部屋","お金や持ち物に目が向く日。財布やカードの明細を一度見直すと、使い方の癖が見えてきます。"),
 3:("ことばと近所の部屋","話す・書く・調べるが進む日。短い連絡をこまめに返すと、話が早く回ります。"),
 4:("家の部屋","家や家族に意識が向く日。部屋の一角を整えたり、早めに帰ったりすると落ち着きます。"),
 5:("楽しみの部屋","好きなことに素直になれる日。趣味や遊びの予定を入れると、気分が大きく上がります。"),
 6:("段取りの部屋","細かい作業がはかどる日。やることを書き出して順に消すと、達成感が残ります。体調管理にも向く日です。"),
 7:("相手の部屋","人との関わりが中心になる日。相手の話を先に聞くと、思ったより話がまとまります。"),
 8:("深いつながりの部屋","ひとつのことを深く掘り下げられる日。広く手を出すより、1人・1件にじっくり向き合うのが吉です。"),
 9:("遠くの部屋","視野が広がる日。いつもと違う本や道、知らない分野にふれると良いヒントがあります。"),
 10:("仕事の部屋","仕事ぶりが目に留まりやすい日。結果を言葉にして報告しておくと評価につながります。"),
 11:("仲間の部屋","仲間や先の計画に縁がある日。久しぶりの人に連絡すると、話が広がります。"),
 12:("休む部屋","内側に気持ちが向く日。無理に予定を詰めず、早めに休むと次の日に響きません。"),
}
# 順位の付け方（about に同じ表を載せる）
HOUSE_ORDER = [1,5,9,11,10,3,7,2,6,4,8,12]

def phase(e):
    if e < 22.5 or e >= 337.5: return ("新月","新月のころ。始めたいことを1つ決めて書き留めておくのに向きます。")
    if e < 157.5: return ("満ちていく月","月が満ちていく時期。新しく始めたことを少しずつ増やしていくと勢いが付きます。")
    if e < 202.5: return ("満月","満月のころ。ここまでの結果がはっきりしやすい時期です。区切りを付けるのに向きます。")
    return ("欠けていく月","月が欠けていく時期。増やすより減らす・手放す・片づけるが進みます。")

SEKKI = ["春分","清明","穀雨","立夏","小満","芒種","夏至","小暑","大暑","立秋","処暑","白露",
         "秋分","寒露","霜降","立冬","小雪","大雪","冬至","小寒","大寒","立春","雨水","啓蟄"]

def day_info(d):
    start = datetime(d.year, d.month, d.day, tzinfo=JST)
    noon = start + timedelta(hours=12)
    end = start + timedelta(days=1)
    e = elongation(noon)
    ms = int(moon_lon(noon) // 30)
    ss = int(sun_lon(noon) // 30)
    sl = sun_lon(noon)
    sekki_now = SEKKI[int(sl // 15)]
    ingress = sign_changes(start, end, moon_lon)
    return dict(date=d, moon_sign=ms, sun_sign=ss, elong=e, age=moon_age(noon), phase=phase(e),
                sekki=sekki_now, sekki_today=[(t, SEKKI[int(sun_lon(t) // 15)]) for (t, _, _) in sign_changes(start, end, lambda t: sun_lon(t) * 2)],  # 15度区切り
                ingress=ingress)

def ranking(info):
    out = []
    for i, s in enumerate(SIGNS):
        h = (info["moon_sign"] - i) % 12 + 1
        out.append((HOUSE_ORDER.index(h), i, h))
    out.sort()
    return [(r + 1, i, h) for r, (_, i, h) in enumerate(out)]

WD = "月火水木金土日"
def jdate(d): return f"{d.year}年{d.month}月{d.day}日（{WD[d.weekday()]}）"
def e(s): return html.escape(s)

CSS = """:root{--bg:#fbfaf7;--fg:#24232a;--sub:#6b6875;--line:#e4e1da;--acc:#4b4a8f;--card:#fff}
@media (prefers-color-scheme:dark){:root{--bg:#16161c;--fg:#ecebf2;--sub:#a3a1ad;--line:#2d2d38;--acc:#a9a8ff;--card:#1e1e26}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.8 "Hiragino Sans","Noto Sans JP",sans-serif}
main,header,footer{max-width:720px;margin:0 auto;padding:0 16px}header{padding-top:24px}
header a{color:var(--fg);text-decoration:none;font-weight:700;font-size:1.1rem}
h1{font-size:1.5rem;line-height:1.4;margin:24px 0 8px}h2{font-size:1.15rem;margin:32px 0 8px;border-bottom:1px solid var(--line);padding-bottom:4px}
a{color:var(--acc)}.sub{color:var(--sub);font-size:.9rem}
.sky{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin:16px 0}
.sky dl{display:grid;grid-template-columns:auto 1fr;gap:4px 16px;margin:0}.sky dt{color:var(--sub)}.sky dd{margin:0}
ol.rank{padding:0;list-style:none}ol.rank li{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 16px;margin:8px 0}
.no{display:inline-block;min-width:2.2em;font-weight:700;color:var(--acc)}.h{color:var(--sub);font-size:.85rem;margin-left:.5em}
table{border-collapse:collapse;width:100%;font-size:.92rem}td,th{border-bottom:1px solid var(--line);padding:6px 4px;text-align:left}
nav.pn{display:flex;justify-content:space-between;margin:24px 0}footer{color:var(--sub);font-size:.8rem;padding:32px 16px}"""

def page(title, desc, body, base, path, root):
    canon = f'<link rel="canonical" href="{base}/{path}">' if base else ""
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">{canon}
<link rel="stylesheet" href="{root}style.css"></head><body>
<header><a href="{root}index.html">月の星座ノート</a> <span class="sub">天文計算でよむ、今日の月</span></header>
<main>{body}</main>
<footer>占いは楽しみとしてお読みください。月と太陽の位置は天文計算（Meeusの式・低精度版）で出しています。<a href="{root}about.html">計算と順位の決め方</a></footer>
</body></html>"""

def sky_block(info):
    ms = SIGNS[info["moon_sign"]][1]
    rows = [("月の星座", f"{ms}（正午の時点）")]
    for t, p, c in info["ingress"]:
        rows.append(("月の移動", f"{t.astimezone(JST):%H:%M}ごろ {SIGNS[p][1]} → {SIGNS[c][1]}"))
    rows.append(("月齢", f"{info['age']:.1f}（{info['phase'][0]}）"))
    sk = info["sekki"]
    for t, name in info["sekki_today"]:
        sk = f"{t.astimezone(JST):%H:%M}ごろ {name}に入る"
    rows.append(("二十四節気", sk))
    return '<div class="sky"><dl>' + "".join(f"<dt>{a}</dt><dd>{e(b)}</dd>" for a, b in rows) + "</dl></div>"

def day_body(info, root, prev_d, next_d):
    d = info["date"]
    ms = SIGNS[info["moon_sign"]][1]
    b = [f"<h1>{jdate(d)}の月と12星座</h1>",
         f'<p class="sub">今日の月は{e(ms)}。{e(info["phase"][1])}</p>', sky_block(info), "<h2>12星座の順位</h2><ol class=\"rank\">"]
    for r, i, h in ranking(info):
        slug, name, _ = SIGNS[i]
        b.append(f'<li><span class="no">{r}位</span><a href="{root}signs/{slug}.html"><b>{name}</b></a>'
                 f'<span class="h">月が{h}番目・{HOUSES[h][0]}</span><br>{e(HOUSES[h][1])}</li>')
    b.append("</ol>")
    nav = '<nav class="pn">'
    nav += f'<a href="{root}days/{prev_d}.html">← 前の日</a>' if prev_d else "<span></span>"
    nav += f'<a href="{root}days/{next_d}.html">次の日 →</a>' if next_d else "<span></span>"
    b.append(nav + "</nav>")
    return "".join(b)

def sign_body(i, infos, root):
    slug, name, rng = SIGNS[i]
    b = [f"<h1>{name}の月のめぐり</h1><p class=\"sub\">{name}（{rng}生まれ）から見て、月が毎日どの部屋を通るか。</p>"]
    today = infos[0]
    r, _, h = [x for x in ranking(today) if x[1] == i][0]
    b.append(f'<h2>{jdate(today["date"])}：{r}位</h2><p><b>{HOUSES[h][0]}</b>（月は{SIGNS[today["moon_sign"]][1]}）<br>{e(HOUSES[h][1])}</p>')
    b.append('<h2>この先2週間</h2><table><tr><th>日付</th><th>月の星座</th><th>部屋</th><th>順位</th></tr>')
    for inf in infos[:14]:
        r, _, h = [x for x in ranking(inf) if x[1] == i][0]
        dd = inf["date"]
        b.append(f'<tr><td><a href="{root}days/{dd.isoformat()}.html">{dd.month}/{dd.day}（{WD[dd.weekday()]}）</a></td>'
                 f'<td>{SIGNS[inf["moon_sign"]][1]}</td><td>{h}・{HOUSES[h][0]}</td><td>{r}位</td></tr>')
    b.append("</table>")
    return "".join(b)

def about_body():
    rows = "".join(f"<tr><td>{n+1}位</td><td>{h}番目</td><td>{HOUSES[h][0]}</td></tr>" for n, h in enumerate(HOUSE_ORDER))
    return f"""<h1>計算と順位の決め方</h1>
<h2>月と太陽の位置</h2><p>月と太陽の黄経は、J.Meeus『Astronomical Algorithms』の式の主な項で計算しています。
月は約0.3度、太陽は約0.01度の精度です。星座は黄経を30度ずつに区切ったもの（トロピカル方式）です。
月が星座を移る時刻は10分ごとに調べてから1分単位まで詰めたもので、数分ずれることがあります。</p>
<h2>部屋（ハウス）と順位</h2><p>自分の星座を1番目として、今日の月が何番目の星座にいるかを「部屋」と呼んでいます（ソーラーサイン・ハウス）。
順位は、部屋の番号だけで次の表のとおりに決めています。くじや気分で入れ替えることはしません。</p>
<table><tr><th>順位</th><th>部屋</th><th>意味</th></tr>{rows}</table>
<h2>月齢と節気</h2><p>月齢は直前の新月からの日数（正午時点）、二十四節気は太陽の黄経15度ごとの区切りです。</p>
<p class="sub">占いは楽しみとしてお読みください。健康・お金・仕事の大事な判断には使わないでください。</p>"""

def main():
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else "dist"
    base = args[args.index("--base") + 1].rstrip("/") if "--base" in args else ""
    ndays = int(args[args.index("--days") + 1]) if "--days" in args else 30
    today = datetime.now(JST).date()
    dates = [today + timedelta(days=k) for k in range(-3, ndays)]
    infos = {d: day_info(d) for d in dates}
    os.makedirs(f"{out}/days", exist_ok=True); os.makedirs(f"{out}/signs", exist_ok=True)
    w = lambda p, s: open(f"{out}/{p}", "w", encoding="utf-8").write(s)
    w("style.css", CSS)
    urls = []
    for k, d in enumerate(dates):
        inf = infos[d]
        prev_d = dates[k - 1].isoformat() if k > 0 else None
        next_d = dates[k + 1].isoformat() if k + 1 < len(dates) else None
        title = f"{jdate(d)}の12星座占い｜月は{SIGNS[inf['moon_sign']][1]}"
        desc = f"{jdate(d)}、月は{SIGNS[inf['moon_sign']][1]}・月齢{inf['age']:.1f}。天文計算で出した月の位置から12星座の順位をよみます。"
        p = f"days/{d.isoformat()}.html"
        w(p, page(title, desc, day_body(inf, "../", prev_d, next_d), base, p, "../")); urls.append(p)
        if d == today:
            w("index.html", page(f"今日の12星座占い｜月の星座ノート", desc, day_body(inf, "", prev_d, next_d), base, "", ""))
    fut = [infos[d] for d in dates if d >= today]
    for i, (slug, name, _) in enumerate(SIGNS):
        p = f"signs/{slug}.html"
        w(p, page(f"{name}の今日と2週間の運勢｜月の星座ノート", f"{name}から見た月のめぐりと、この先2週間の順位。", sign_body(i, fut, "../"), base, p, "../")); urls.append(p)
    w("about.html", page("計算と順位の決め方｜月の星座ノート", "月の位置の計算方法と順位の決め方。", about_body(), base, "about.html", "")); urls.append("about.html")
    if base:
        w("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
          + f"<url><loc>{base}/</loc></url>" + "".join(f"<url><loc>{base}/{u}</loc></url>" for u in urls) + "</urlset>")
        w("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")
    print(f"{out}: {len(urls)+1}ページ（{dates[0]}〜{dates[-1]}）")

if __name__ == "__main__":
    main()
