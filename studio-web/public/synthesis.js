// Deterministic browser/worker/server synthesis. No external plugins or audio services.
const TAU=2*Math.PI;
export function synthVoice(project,track,note,velocity,rate=44100,seed=0){
 const t=track,tonal=t.type==='bass'||t.type==='synth';
 const midi=project.root+(t.type==='synth'?12:0)+note+t.transpose;
 const frequency=440*2**((midi-69)/12);
 const seconds=Math.min(2.5,(t.type==='kick'?.45:t.type==='clap'?.24:t.type==='hat'?(t.preset==='open'?.4:.12):t.type==='bass'?.3:.85)*t.decay);
 const length=Math.max(2,Math.ceil(seconds*rate)),out=new Float32Array(length);
 const attack=Math.max(1,Math.round((t.type==='kick'?.0005:t.type==='hat'?.001:tonal?.005:.001)*rate));
 const release=Math.max(1,Math.min(Math.round(length*.22),Math.round((tonal?.035:.012)*rate)));
 let rng=(project.seed+seed*1664525+1013904223)>>>0,phase=0,low=0,noiseLow=0,noiseHigh=0,previous=0,dc=0;
 const random=()=>{rng=(Math.imul(rng,1664525)+1013904223)>>>0;return rng/2147483648-1};
 const cutoff=t.type==='hat'?Math.min(t.filter,10500):t.filter;
 const lowAlpha=1-Math.exp(-TAU*Math.min(cutoff,rate*.45)/rate);
 const noiseLowAlpha=1-Math.exp(-TAU*Math.min(2200,rate*.1)/rate);
 const noiseHighAlpha=1-Math.exp(-TAU*Math.min(10000,rate*.4)/rate);
 const dcR=Math.exp(-TAU*12/rate);
 const intervals=t.type==='synth'?(t.chordIntervals||[0]):[0];
 const harmonic=(angle,f,weights)=>{let sum=0;for(let h=1;h<=weights.length;h++)if(f*h<rate*.45)sum+=weights[h-1]*Math.sin(angle*h);return sum};
 for(let i=0;i<length;i++){
  const time=i/rate;let value=0;
  if(t.type==='kick'){
   const base=t.preset==='sub'?43:t.preset==='deep'?49:57;
   phase+=TAU*(base+145*Math.exp(-time*(t.preset==='punch'?110:80)))/rate;
   const damping=t.preset==='sub'?8:t.preset==='deep'?11:15;
   value=Math.sin(phase)*Math.exp(-time*damping/t.decay)+random()*.11*Math.exp(-time*240);
  }else if(t.type==='clap'){
   const noise=random();noiseLow+=noiseLowAlpha*(noise-noiseLow);
   const spacing=t.preset==='wide'?.019:.009,damping=t.preset==='wide'?23:t.preset==='snap'?65:48;
   const pulse=Math.exp(-time*damping/t.decay)+.6*(time>=spacing?Math.exp(-(time-spacing)*140):0)+.35*(time>=2*spacing?Math.exp(-(time-2*spacing)*140):0);
   value=(noise-noiseLow)*pulse*.65;
  }else if(t.type==='hat'){
   const noise=random();noiseLow+=noiseLowAlpha*(noise-noiseLow);noiseHigh+=noiseHighAlpha*(noise-noiseHigh);
   const band=noiseHigh-noiseLow;
   value=band*Math.exp(-time*(t.preset==='open'?12:45)/t.decay)*(t.preset==='soft'?.85:1.1);
  }else{
   phase+=TAU*frequency/rate;
   const weights=t.type==='bass'?(t.preset==='acid'?[1,.55,.34,.2,.12]:t.preset==='pluck'?[1,.48,.27,.13]:[1,.45,.28,.12]):t.preset==='bright'?[1,.48,.28,.18,.1]:t.preset==='glass'?[.8,.08,.35,.03,.14]:[1,.35,.17,.08];
   for(const semitone of intervals){const ratio=2**(semitone/12);value+=harmonic(phase*ratio,frequency*ratio,weights)}
   value/=Math.sqrt(intervals.length);
   value*=Math.exp(-time*(t.preset==='pluck'?15:t.type==='bass'?7:3.5)/t.decay)*(t.type==='bass'?.44:.42);
  }
  low+=lowAlpha*(value-low);
  dc=low-previous+dcR*dc;previous=low;
  const fadeIn=i>=attack?1:.5-.5*Math.cos(Math.PI*i/attack);
  const remaining=length-1-i,fadeOut=remaining>=release?1:.5-.5*Math.cos(Math.PI*remaining/release);
  out[i]=dc*fadeIn*fadeOut*t.volume*velocity*.55;
 }
 return out;
}
