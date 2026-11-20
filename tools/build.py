"""Jobzyn company carousel builder (approved design, 20 Nov 2026).
Usage: python3 build.py data.json OUT_DIR
data.json: {"company","company_slug","logo" (path to PNG),"offers":[{id,title,contract,city,experience,education,salary|null,profile:[3 lines]}]}
Writes: OUT_DIR/00-cover.png, NN-<id>.png, and "<company> recrute chez Jobzyn.pdf" (PDF title set the same)."""
import json, os, subprocess, html, glob, sys
from PIL import Image
from pypdf import PdfReader, PdfWriter
HERE=os.path.dirname(os.path.abspath(__file__))
D=json.load(open(sys.argv[1]))
OUT=os.path.abspath(sys.argv[2]); os.makedirs(OUT,exist_ok=True)
for f in glob.glob(OUT+"/*"): os.remove(f)
CHROME=next((c for c in ["google-chrome","chromium","chromium-browser"] if subprocess.run(["which",c],capture_output=True).returncode==0),"google-chrome")
e=html.escape
def icon(name,size=28):
    return open(os.path.join(HERE,"icons",name+".svg")).read().replace("<svg",f'<svg width="{size}" height="{size}" class="ico"',1)
FONTS="".join(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url('file://{HERE}/fonts/{f}')}}" for fam,w,f in [
 ("Gabarito",700,"gabarito-latin-700-normal.woff2"),("Gabarito",800,"gabarito-latin-800-normal.woff2"),
 ("Geist",400,"geist-sans-latin-400-normal.woff2"),("Geist",500,"geist-sans-latin-500-normal.woff2"),
 ("Geist",600,"geist-sans-latin-600-normal.woff2"),("Geist",700,"geist-sans-latin-700-normal.woff2")])
CSS=FONTS+"""
:root{--o:#F97316;--y:#FAC748;--ink:#1A1F2E;--mut:#718096;--line:#E2E8F0;--grad:linear-gradient(90deg,#EB7215,#FAC748)}
*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;height:1080px;overflow:hidden;font-family:'Geist',sans-serif;color:var(--ink)}
.pg{position:relative;width:1080px;height:1080px;padding:64px 76px;display:flex;flex-direction:column;overflow:hidden}
.white{background:#fff}
.white:before{content:"";position:absolute;inset:0;background-image:radial-gradient(#D5D2CF 1.6px,transparent 1.6px);background-size:44px 44px;opacity:.55;-webkit-mask-image:radial-gradient(ellipse 85% 70% at 70% 20%,#000,transparent 75%)}
.dark{background:linear-gradient(165deg,#0C0600,#140B03 55%,#1C1008);color:#fff}
.dark:before{content:"";position:absolute;inset:0;background:radial-gradient(ellipse 85% 70% at 50% 112%,rgba(249,115,22,.40),rgba(249,115,22,.10) 45%,transparent 72%)}
.pg>*{position:relative}
.top{display:flex;justify-content:space-between;align-items:center;height:86px}
.wm{font-family:'Gabarito';font-weight:800;font-size:38px;letter-spacing:-.02em}
.white .wm{background:var(--grad);-webkit-background-clip:text;color:transparent}
.chip{background:#fff;border-radius:18px;border:1px solid rgba(0,0,0,.08);box-shadow:0 8px 24px rgba(10,6,2,.10);display:flex;align-items:center;justify-content:center;padding:16px 24px}
.chip img{display:block;height:46px;width:auto}
.ico{fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;flex:none}
.mid{flex:1;display:flex;flex-direction:column;justify-content:center;padding:20px 0}
.kick{font-weight:600;letter-spacing:.2em;text-transform:uppercase;font-size:20px;color:var(--o);display:flex;align-items:center;gap:18px}
.kick .bar{height:2px;flex:1;background:linear-gradient(90deg,rgba(249,115,22,.5),transparent)}
.role{font-family:'Gabarito';font-weight:800;letter-spacing:-.03em;line-height:1.0;font-size:70px;margin-top:20px}
.co{font-size:23px;font-weight:500;color:var(--mut);margin-top:14px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:32px}
.tile{border:1px solid var(--line);background:rgba(255,255,255,.92);border-radius:18px;padding:16px 20px;display:flex;gap:16px;align-items:center}
.tile .ic{width:52px;height:52px;border-radius:13px;background:rgba(249,115,22,.10);color:var(--o);display:grid;place-items:center;flex:none}
.tile .l{font-size:15px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--mut)}
.tile .v{font-family:'Gabarito';font-weight:700;font-size:27px;margin-top:3px;line-height:1.1}
.tile.sal{grid-column:1/3;background:var(--grad);border:0;color:#1a1206}
.tile.sal .ic{background:rgba(255,255,255,.35);color:#1a1206}.tile.sal .l{color:rgba(26,18,6,.7)}.tile.sal .v{font-size:34px}
.sec{margin-top:30px;font-size:18px;font-weight:600;letter-spacing:.18em;text-transform:uppercase}
ul{list-style:none;margin-top:14px;display:flex;flex-direction:column;gap:12px}
li{font-size:25px;font-weight:500;line-height:1.3;display:flex;gap:16px;color:#2D3446}
li:before{content:"";width:11px;height:11px;border-radius:4px;background:var(--grad);margin-top:11px;flex:none}
.dark .kick{color:var(--y)} .dark .kick .bar{background:linear-gradient(90deg,rgba(250,199,72,.5),transparent)}
.ctitle{font-family:'Gabarito';font-weight:800;letter-spacing:-.035em;line-height:.98;font-size:80px;margin-top:18px}
.ctitle .g{background:var(--grad);-webkit-background-clip:text;color:transparent}
.meta{display:flex;gap:12px;margin-top:24px}
.meta span{border:1px solid rgba(255,255,255,.22);background:rgba(255,255,255,.07);border-radius:99px;padding:10px 20px;font-size:21px;font-weight:500}
.list{margin-top:30px;border-top:1px solid rgba(255,255,255,.14)}
.it{display:flex;gap:20px;align-items:baseline;padding:11px 0;border-bottom:1px solid rgba(255,255,255,.14)}
.it b{font-family:'Gabarito';font-weight:800;color:var(--y);font-size:21px;width:36px;flex:none}
.it span{font-size:23px;font-weight:500;color:rgba(255,255,255,.92);line-height:1.25}
.foot{display:flex;justify-content:space-between;align-items:center;padding-top:26px}
.swipe{display:inline-flex;align-items:center;gap:12px;background:var(--grad);color:#1a1206;border-radius:99px;padding:16px 28px;font-size:23px;font-weight:700}
.slogan{font-size:19px;font-weight:500;color:rgba(255,255,255,.6)}
"""
FIT="""<script>window.onload=function(){var p=document.querySelector('.pg');function ok(){return p.scrollHeight<=p.clientHeight+1}
function sh(sel,min){var els=[].slice.call(document.querySelectorAll(sel));if(!els.length)return;var s=parseFloat(getComputedStyle(els[0]).fontSize);
while(!ok()&&s>min){s-=1;els.forEach(function(x){x.style.fontSize=s+'px'})}}
sh('.role',46);sh('li',20);sh('.it span',17);}</script>"""
def page(b,cls): return f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{CSS}</style>{FIT}</head><body><div class='pg {cls}'>{b}</div></body></html>"
logo="file://"+os.path.abspath(D["logo"])
top=f"<div class='top'><span class='wm'>JOBZYN</span><div class='chip'><img src='{logo}'></div></div>"
offers=D["offers"];n=len(offers)
items="".join(f"<div class='it'><b>{i+1:02d}</b><span>{e(o['title'])}</span></div>" for i,o in enumerate(offers))
cities=" / ".join(sorted({o['city'] for o in offers}));contracts=" / ".join(sorted({o['contract'] for o in offers}))
cover=(top+"<div class='mid'><div class='kick'>Offres d'emploi<span class='bar'></span></div>"
 f"<div class='ctitle'>{e(D['company'])} <span class='g'>recrute</span></div>"
 f"<div class='meta'><span>{n} postes</span><span>{e(contracts)}</span><span>{e(cities)}</span></div>"
 f"<div class='list'>{items}</div></div>"
 f"<div class='foot'><span class='swipe'>Lien dans la caption {icon('arrow-up',24)}</span><span class='slogan'>A Better Way To Find Your Next Job.</span></div>")
pages=[("00-cover",page(cover,"dark"))]
for i,o in enumerate(offers,1):
    t=""
    if o.get("salary"): t+=f"<div class='tile sal'><div class='ic'>{icon('banknote')}</div><div><div class='l'>Salaire</div><div class='v'>{e(o['salary'])}</div></div></div>"
    for ic,l,k in [("briefcase","Contrat","contract"),("map-pin","Lieu","city"),("award","Expérience","experience"),("graduation-cap","Formation","education")]:
        t+=f"<div class='tile'><div class='ic'>{icon(ic)}</div><div><div class='l'>{l}</div><div class='v'>{e(o[k])}</div></div></div>"
    prof="".join(f"<li>{e(p)}</li>" for p in o["profile"][:3])
    b=(top+f"<div class='mid'><div class='kick'>Offre {i:02d} / {n:02d}<span class='bar'></span></div>"
       f"<div class='role'>{e(o['title'])}</div><div class='co'>{e(D['company'])}</div>"
       f"<div class='grid'>{t}</div><div class='sec'>Profil recherché</div><ul>{prof}</ul></div>")
    pages.append((f"{i:02d}-{o['id']}",page(b,"white")))
for name,h in pages:
    hp=os.path.join(OUT,name+".html");open(hp,"w").write(h);png=os.path.join(OUT,name+".png")
    subprocess.run([CHROME,"--headless=new","--no-sandbox","--disable-gpu","--hide-scrollbars","--allow-file-access-from-files",
      "--window-size=1080,1080","--virtual-time-budget=4000",f"--screenshot={png}","file://"+hp],check=True,capture_output=True)
    os.remove(hp);print(png)

title=f"{D['company']} recrute chez Jobzyn"
fs=sorted(glob.glob(os.path.join(OUT,"*.png")));imgs=[Image.open(f).convert("RGB") for f in fs]
tmp=os.path.join(OUT,"_tmp.pdf");imgs[0].save(tmp,save_all=True,append_images=imgs[1:],resolution=144)
r=PdfReader(tmp);w=PdfWriter()
for p in r.pages: w.add_page(p)
w.add_metadata({"/Title":title,"/Author":"Jobzyn"});pdf=os.path.join(OUT,title+".pdf");w.write(pdf);os.remove(tmp)
print("PDF",pdf,len(r.pages),"pages")
