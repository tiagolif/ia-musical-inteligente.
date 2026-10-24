from pathlib import Path
import urllib.request,urllib.parse,json,subprocess,hashlib,base64,uuid,io,wave
root=Path(__file__).resolve().parents[1]/'public/library';cat=json.loads((root/'catalog.json').read_text());rev=cat['revision']
items=[('vcsl-kawai-a4','Piano Kawai · A4','synth','Chordophones/Zithers/Grand Piano, Kawai - Legacy/Sustains/GrandPno_Main_Sus_A4_v3_rr1.wav',6),('vcsl-conga','Conga · toque aberto','hat','Membranophones/Struck Membranophones/Conga/Conga_HitN_v2_rr1_Sum.wav',2)]
for slug,name,kind,path,dur in items:
 url='https://raw.githubusercontent.com/sgossner/VCSL/'+rev+'/'+urllib.parse.quote(path);raw=urllib.request.urlopen(url,timeout=60).read();tmp=Path('/tmp/'+slug+'.wav');tmp.write_bytes(raw)
 out=subprocess.check_output(['ffmpeg','-v','error','-i',str(tmp),'-t',str(dur),'-ac','1','-ar','44100','-af','highpass=f=35,afade=t=out:st='+str(dur-.1)+':d=0.1','-f','wav','-c:a','pcm_s16le','pipe:1'])
 with wave.open(io.BytesIO(out),'rb') as w:frames=w.readframes(44100*dur)
 buf=io.BytesIO()
 with wave.open(buf,'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(44100);w.writeframes(frames)
 data=buf.getvalue();(root/(slug+'.json')).write_text(json.dumps({'wavBase64':base64.b64encode(data).decode()}))
 asset={'id':str(uuid.uuid5(uuid.NAMESPACE_URL,'https://github.com/sgossner/VCSL#'+slug)),'name':name,'type':kind,'license':'CC0-1.0','author':'Versilian Studios / VCSL contributors','sourceUrl':url,'sourceSha256':hashlib.sha256(raw).hexdigest(),'sha256':hashlib.sha256(data).hexdigest(),'duration':len(frames)/88200,'url':'/library/'+slug+'.json','processing':'Mono PCM16 44.1k; highpass 35Hz; trimmed and faded','rootMidi':69 if kind=='synth' else None}
 cat['assets']=[a for a in cat['assets'] if a['id']!=asset['id']]+[asset];print(name,len(data))
(root/'catalog.json').write_text(json.dumps(cat,ensure_ascii=False,indent=2))
