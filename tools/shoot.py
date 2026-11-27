# -*- coding: utf-8 -*-
"""把 21 句在手機尺寸（375×900，2 倍）各拍一張，拼成 PDF 給使用者核對"""
import subprocess, os, datetime, glob, sys
from PIL import Image, ImageDraw, ImageFont
Image.init()  # 註冊 JPEG 等編碼器，存 PDF 要用

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
HTML = r"D:\USER\A240613\GitHub\meters-web\index.html"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")
os.makedirs(OUT, exist_ok=True)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 21
t = datetime.date.today(); roc = f"{t.year-1911}{t.month:02d}{t.day:02d}"

for i in range(3):  # intro shots
    png = os.path.join(OUT, f"i{i:02d}.png")
    url = "file:///" + HTML.replace("\\", "/") + f"?i={i}&shot=1"
    cmd = [EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=375,900",
           "--force-device-scale-factor=2", "--virtual-time-budget=8000", f"--screenshot={png}", url]
    subprocess.run(cmd, capture_output=True, timeout=90)
for i in range(N):
    png = os.path.join(OUT, f"q{i:02d}.png")
    url = "file:///" + HTML.replace("\\", "/") + f"?q={i}&shot=1"
    cmd = [EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=375,900",
           "--force-device-scale-factor=2", "--virtual-time-budget=8000", f"--screenshot={png}", url]
    r = subprocess.run(cmd, capture_output=True, timeout=90)
    print(i, os.path.exists(png), os.path.getsize(png) if os.path.exists(png) else r.returncode)

# 拼頁：每頁 3 支手機並排，標上句號
files = sorted(glob.glob(os.path.join(OUT, "i*.png"))) + sorted(glob.glob(os.path.join(OUT, "q*.png")))
imgs = [Image.open(f).convert("RGB") for f in files]
w, h = imgs[0].size
pad, top = 40, 70
pages = []
try:
    font = ImageFont.truetype(r"C:\Windows\Fonts\msjh.ttc", 34)
except Exception:
    font = ImageFont.load_default()
for k in range(0, len(imgs), 3):
    group = imgs[k:k+3]
    page = Image.new("RGB", (pad + len(group) * (w + pad), top + h + pad), "#f4f1ea")
    d = ImageDraw.Draw(page)
    for j, im in enumerate(group):
        x = pad + j * (w + pad)
        name = os.path.basename(files[k+j]); d.text((x, 18), (f"開場 {int(name[1:3])+1}" if name.startswith("i") else f"第 {int(name[1:3])+1:02d} 句"), fill="#2a333c", font=font)
        page.paste(im, (x, top))
    pages.append(page)
pdf = os.path.join(r"D:\USER\A240613\Desktop", f"離開地面_21句手機畫面_{roc}.pdf")
try:
    pages[0].save(pdf, save_all=True, append_images=pages[1:], resolution=144)
except PermissionError:  # 使用者開著舊檔，就加時間另存
    hm = datetime.datetime.now().strftime("%H%M")
    pdf = os.path.join(r"D:\USER\A240613\Desktop", f"離開地面_21句手機畫面_{roc}_{hm}.pdf")
    pages[0].save(pdf, save_all=True, append_images=pages[1:], resolution=144)
print("PDF:", pdf, len(pages), "pages")
