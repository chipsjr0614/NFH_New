# -*- coding: utf-8 -*-
import urllib.parse, urllib.request, json, os, ssl, time
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA="Mozilla/5.0 (NFH-edu research)"
def api(p):
    req=urllib.request.Request("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(p),headers={"User-Agent":UA})
    return json.load(urllib.request.urlopen(req,timeout=30,context=ctx))
def search(term,limit=15):
    d=api({"action":"query","list":"search","srsearch":term,"srnamespace":6,"srlimit":limit,"format":"json"})
    return [x["title"] for x in d["query"]["search"]]
def info(t):
    d=api({"action":"query","titles":t,"prop":"imageinfo","iiprop":"url|extmetadata","format":"json"})
    p=list(d["query"]["pages"].values())[0]; ii=p["imageinfo"][0]
    return ii["url"], ii.get("extmetadata",{}).get("LicenseShortName",{}).get("value","")
def dl(url,path):
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    open(path,"wb").write(urllib.request.urlopen(req,timeout=90,context=ctx).read())
meta=json.load(open("images/_meta.json"))
TASKS=[
 ("36_xray_ileus",["Bowel obstruction X-ray","Ileus radiograph","Intestinal obstruction abdominal radiograph","Air fluid levels abdomen"]),
 ("11_ct_aortic",["Aortic dissection","Aortic dissection computed tomography","Stanford type A aortic dissection CT"]),
]
for key,terms in TASKS:
    done=False
    for term in terms:
        if done: break
        for attempt in range(3):
            try:
                time.sleep(5)
                files=search(term,15)
                cand=[t for t in files if t.lower().endswith((".jpg",".jpeg",".png"))]
                if not cand: print(f"[{key}] '{term}' 후보없음"); break
                chosen=cand[0]; time.sleep(5)
                url,lic=info(chosen); ext=os.path.splitext(url)[1].lower(); path=f"images/{key}{ext}"
                dl(url,path); meta[key]={"file":path,"title":chosen,"license":lic,"src":url}
                print(f"[{key}] ✅ {chosen[:46]} | {lic}"); done=True; break
            except urllib.error.HTTPError as e:
                if e.code==429: time.sleep(12); continue
                print(f"[{key}] ❌ {e}"); break
            except Exception as e:
                print(f"[{key}] ❌ {e}"); break
json.dump(meta,open("images/_meta.json","w"),ensure_ascii=False,indent=1)
print("총 이미지:",len(meta))
