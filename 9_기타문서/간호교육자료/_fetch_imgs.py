# -*- coding: utf-8 -*-
import urllib.parse, urllib.request, json, os, ssl
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA="Mozilla/5.0 (NFH-edu research)"
def api(params):
    url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    return json.load(urllib.request.urlopen(req,timeout=30,context=ctx))
def search_files(term,limit=10):
    d=api({"action":"query","list":"search","srsearch":term,"srnamespace":6,"srlimit":limit,"format":"json"})
    return [x["title"] for x in d["query"]["search"]]
def info(title):
    d=api({"action":"query","titles":title,"prop":"imageinfo","iiprop":"url|extmetadata","format":"json"})
    pages=d["query"]["pages"]
    p=list(pages.values())[0]
    ii=p["imageinfo"][0]
    em=ii.get("extmetadata",{})
    return ii["url"], em.get("LicenseShortName",{}).get("value",""), em.get("Artist",{}).get("value","")[:80]
def download(url,path):
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    data=urllib.request.urlopen(req,timeout=60,context=ctx).read()
    open(path,"wb").write(data); return len(data)

BAD=(".ogv",".webm",".gif",".pdf",".tif",".tiff",".svg")
TASKS=[
 ("01_ecg_stemi","12 Lead EKG ST Elevation tracing color coded"),
 ("06_ecg_vf","Ventricular fibrillation ECG"),
 ("08_ecg_af","Atrial fibrillation ECG 12 lead"),
 ("40_ecg_hyperK","Hyperkalemia ECG"),
 ("13_xray_pneumonia","Lobar pneumonia chest x-ray"),
 ("15_xray_pneumothorax","Pneumothorax chest x-ray"),
 ("36_xray_ileus","Small bowel obstruction x-ray"),
 ("14_ct_pe","Pulmonary embolism CT angiography"),
 ("11_ct_aortic","Aortic dissection CT"),
 ("20_ct_ischemic","Ischemic stroke CT scan"),
 ("21_ct_ich","Intracerebral hemorrhage CT"),
 ("23_ct_sah","Subarachnoid hemorrhage CT"),
]
import re
meta={}
for key,term in TASKS:
    try:
        files=search_files(term,12)
        chosen=None
        for t in files:
            low=t.lower()
            if any(low.endswith(b) for b in BAD): continue
            if not (low.endswith(".jpg") or low.endswith(".jpeg") or low.endswith(".png")): continue
            chosen=t; break
        if not chosen:
            print(f"[{key}] 후보 없음 (results={files[:3]})"); continue
        url,lic,artist=info(chosen)
        ext=os.path.splitext(url)[1].lower()
        path=f"images/{key}{ext}"
        sz=download(url,path)
        meta[key]={"file":path,"title":chosen,"license":lic,"src":url}
        print(f"[{key}] ✅ {chosen[:45]} | {lic} | {sz//1024}KB")
    except Exception as e:
        print(f"[{key}] ❌ {e}")
json.dump(meta,open("images/_meta.json","w"),ensure_ascii=False,indent=1)
print("\n메타 저장: images/_meta.json")
