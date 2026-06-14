# -*- coding: utf-8 -*-
import urllib.parse, urllib.request, json, os, ssl, time
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA="Mozilla/5.0 (NFH-edu research)"
def api(params):
    url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    return json.load(urllib.request.urlopen(req,timeout=30,context=ctx))
def search_files(term,limit=12):
    d=api({"action":"query","list":"search","srsearch":term,"srnamespace":6,"srlimit":limit,"format":"json"})
    return [x["title"] for x in d["query"]["search"]]
def info(title):
    d=api({"action":"query","titles":title,"prop":"imageinfo","iiprop":"url|extmetadata","format":"json"})
    p=list(d["query"]["pages"].values())[0]; ii=p["imageinfo"][0]; em=ii.get("extmetadata",{})
    return ii["url"], em.get("LicenseShortName",{}).get("value","")
def download(url,path):
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    data=urllib.request.urlopen(req,timeout=90,context=ctx).read(); open(path,"wb").write(data); return len(data)
BAD=(".ogv",".webm",".gif",".pdf",".tif",".tiff",".svg")
TASKS=[
 ("40_ecg_hyperK","Hyperkalemia ECG peaked T wave"),
 ("15_xray_pneumothorax","Pneumothorax chest x-ray"),
 ("36_xray_ileus","Small bowel obstruction x-ray erect"),
 ("14_ct_pe","Pulmonary embolism CT pulmonary angiogram"),
 ("11_ct_aortic","Aortic dissection CT angiography"),
 ("20_ct_ischemic","Middle cerebral artery infarct CT"),
 ("21_ct_ich","Intracerebral hemorrhage CT scan"),
 ("23_ct_sah","Subarachnoid hemorrhage CT scan"),
]
meta=json.load(open("images/_meta.json"))
for key,term in TASKS:
    for attempt in range(4):
        try:
            time.sleep(4)
            files=search_files(term,12)
            chosen=next((t for t in files if t.lower().endswith((".jpg",".jpeg",".png")) and not any(t.lower().endswith(b) for b in BAD)),None)
            if not chosen: print(f"[{key}] 후보없음"); break
            time.sleep(4)
            url,lic=info(chosen)
            ext=os.path.splitext(url)[1].lower(); path=f"images/{key}{ext}"
            sz=download(url,path)
            meta[key]={"file":path,"title":chosen,"license":lic,"src":url}
            print(f"[{key}] ✅ {chosen[:44]} | {lic} | {sz//1024}KB"); break
        except urllib.error.HTTPError as e:
            if e.code==429: print(f"[{key}] 429 재시도 {attempt+1}"); time.sleep(10); continue
            print(f"[{key}] ❌ {e}"); break
        except Exception as e:
            print(f"[{key}] ❌ {e}"); break
json.dump(meta,open("images/_meta.json","w"),ensure_ascii=False,indent=1)
print("\n총 이미지:",len(meta))
