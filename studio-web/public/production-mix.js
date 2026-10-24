import {events} from './model.js';
// Linear shared ambience/delay and kick-triggered ducking; all processing remains local.
export function mixProduction(project,ev,options,samples,voice,left,right,rate){
 const n=left.length,roomL=new Float32Array(n),roomR=new Float32Array(n),delayL=new Float32Array(n),delayR=new Float32Array(n);
 const kicks=events(project,{...options,trackId:undefined}).events.filter(e=>project.tracks[e.track].type==='kick').map(e=>Math.round(e.time*rate));
 for(let j=0;j<project.tracks.length;j++){
  const t=project.tracks[j],notes=ev.filter(e=>e.track===j);if(!notes.length)continue;
  if(t.sampleId&&!samples[t.sampleId])throw Error('Sample indisponível: '+t.name);
  const mono=new Float32Array(n);
  for(const e of notes){const data=voice(project,t,e.note,e.velocity,samples[t.sampleId],rate,e.track*100000+e.bar*16+e.step),start=Math.round(e.time*rate);for(let i=0;i<data.length&&start+i<n;i++)mono[start+i]+=data[i]}
  const fx=t.fx||{},pole=Math.exp(-2*Math.PI*(fx.highpass||20)/rate),panL=Math.cos((t.pan+1)*Math.PI/4),panR=Math.sin((t.pan+1)*Math.PI/4);let last=0,hp=0,k=0;
  for(let i=0;i<n;i++){
   hp=mono[i]-last+pole*hp;last=mono[i];
   while(k+1<kicks.length&&kicks[k+1]<=i)k++;
   const dt=kicks.length&&i>=kicks[k]?(i-kicks[k])/rate:100;
   const duck=1-(fx.duck||0)*(1-Math.exp(-dt/.003))*Math.exp(-dt/.13);
   const l=hp*duck*panL,r=hp*duck*panR;left[i]+=l;right[i]+=r;
   roomL[i]+=l*(fx.room||0);roomR[i]+=r*(fx.room||0);delayL[i]+=l*(fx.delay||0);delayR[i]+=r*(fx.delay||0);
  }
 }
 const echoSamples=Math.round(60/project.bpm*.75*rate),a=1-Math.exp(-2*Math.PI*4500/rate);let lpL=0,lpR=0;
 for(let i=0;i<n;i++){
  const l=i>=echoSamples?delayR[i-echoSamples]:0,r=i>=echoSamples?delayL[i-echoSamples]:0;
  lpL+=a*(l-lpL);lpR+=a*(r-lpR);
  delayL[i]+=lpL*.32;delayR[i]+=lpR*.32;left[i]+=lpL;right[i]+=lpR;
 }
 for(const [channel,input,offset]of [[left,roomL,0],[right,roomR,.0017]]){
  for(const seconds of [.0297,.0371,.0411,.0437]){
   const d=Math.round((seconds+offset)*rate),buffer=new Float32Array(d),feedback=10**(-3*(seconds+offset)/1.2);let index=0,damped=0;
   for(let i=0;i<n;i++){const delayed=buffer[index];damped+=.35*(delayed-damped);buffer[index]=input[i]+damped*feedback;channel[i]+=delayed*.25;if(++index===d)index=0}
  }
 }
}
