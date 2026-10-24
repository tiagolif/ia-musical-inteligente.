"""Rebuild the curated CC0 percussion pack from pinned VCSL source files."""
import urllib.request, urllib.parse, json, subprocess, pathlib, hashlib, base64, concurrent.futures, uuid
ROOT=pathlib.Path(__file__).resolve().parents[1]
revision=json.load(urllib.request.urlopen('https://api.github.com/repos/sgossner/VCSL/commits/master',timeout=30))['sha']
choices=[
('vcsl-bass-drum','Bumbo acústico','kick','Membranophones/Struck Membranophones/Bass Drum 1/BDrumNew_hit_v3_rr1_Sum.wav'),
('vcsl-clap-1','Palma natural 01','clap','Idiophones/Struck Idiophones/Claps/Clap_rr1.wav'),
('vcsl-clap-2','Palma natural 02','clap','Idiophones/Struck Idiophones/Claps/Clap_rr2.wav'),
('vcsl-hat-closed','Hi-hat acústico fechado','hat','Idiophones/Struck Idiophones/Hi-Hat Cymbal/HiHat_HitC_v3_rr1_Mid.wav'),
('vcsl-hat-open','Hi-hat acústico aberto','hat','Idiophones/Struck Idiophones/Hi-Hat Cymbal/HiHat_HitO_rr1_Mid.wav'),
('vcsl-shaker','Shaker orgânico','hat','Idiophones/Struck Idiophones/Shaker, Large/LShaker_Hit_rr1_Mid.wav'),
('vcsl-tambourine','Pandeirola','hat','Idiophones/Struck Idiophones/Tambourine 1/Tamb1_Hit_v2_rr1_Mid.wav')]
def make(item):
 id,name,type,path=item
 url='https://raw.githubusercontent.com/sgossner/VCSL/'+revision+'/'+urllib.parse.quote(path)
 raw=urllib.request.urlopen(url,timeout=60).read()
 tmp=pathlib.Path('/tmp/'+id+'.wav');tmp.write_bytes(raw)
 # Mono PCM at the engine's native rate, trimmed to 4 seconds, safe peak and short fade.
 out=subprocess.check_output(['ffmpeg','-v','error','-i',str(tmp),'-t','4','-ac','1','-ar','44100','-af','loudnorm=I=-23:TP=-3:LRA=7','-f','wav','-c:a','pcm_s16le','pipe:1'])
 # ffmpeg's streamed WAV uses an open-ended data size. Rewrite a canonical RIFF header.
 import io,wave
 with wave.open(io.BytesIO(out),'rb') as f: frames=f.readframes(176400)
 buf=io.BytesIO()
 with wave.open(buf,'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(44100);f.writeframes(frames)
 data=buf.getvalue()
 (ROOT/'public/library'/f'{id}.json').write_text(json.dumps({'wavBase64':base64.b64encode(data).decode()}))
 return {'id':str(uuid.uuid5(uuid.NAMESPACE_URL,'https://github.com/sgossner/VCSL#'+id)),'name':name,'type':type,'license':'CC0-1.0','author':'Versilian Studios / VCSL contributors','sourceUrl':url,'sourceSha256':hashlib.sha256(raw).hexdigest(),'sha256':hashlib.sha256(data).hexdigest(),'duration':len(frames)/88200,'url':'/library/'+id+'.json','processing':'Mono PCM 16-bit, 44.1 kHz; trimmed to 4 s; loudness adjusted'}
with concurrent.futures.ThreadPoolExecutor(max_workers=7) as pool: assets=list(pool.map(make,choices))
(ROOT/'public/library/catalog.json').write_text(json.dumps({'source':'https://github.com/sgossner/VCSL','revision':revision,'license':'CC0-1.0','assets':assets},ensure_ascii=False,indent=2))
print('Prepared',len(assets),'CC0 samples;',sum((ROOT/'public/library'/f'{x[0]}.json').stat().st_size for x in choices),'bytes')
