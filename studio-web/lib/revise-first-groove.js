import {clone,validate} from '../public/model.js';
export function reviseFirstGroove(backup){
 const p=clone(backup.project);validate(p);
 if(p.tracks.some(t=>t.locked))throw Error('Desbloqueie as pistas antes de revisar a produção');
 p.engineVersion=2;p.title='Primeiro Groove · Versão B';
 p.brief='Revisão técnica: harmonia do baixo corrigida, release suave, baixo com harmônicos e hi-hat em banda audível. Viradas por seção antes do respiro e do drop. Ainda aguardando avaliação auditiva.';
 const track=id=>p.tracks.find(t=>t.id===id);
 for(const sec of p.sections){const major=sec.name.includes('· F')||sec.name.includes('· G');if(!major)continue;const bass=sec.patterns?.['track-3'];if(!bass)continue;const fundamental=bass[0].note;for(const step of bass)if(step.note===fundamental+3)step.note=fundamental+4;}
 Object.assign(track('track-0'),{volume:.78,decay:.95,soundBrief:'Kick: ataque curto e corpo mais definido. Aguardando comparação com A.'});
 Object.assign(track('track-3'),{volume:.72,decay:.8,filter:1800,soundBrief:'Baixo: fundamental e harmônicos para presença em caixas pequenas; sem notas fora da harmonia planejada.'});
 Object.assign(track('track-2'),{volume:.56,filter:10000,decay:.85,pan:-.22,soundBrief:'Hi-hat: presença entre médios-agudos e agudos; evitar energia excessiva acima de 16 kHz.'});
 Object.assign(track('track-1'),{volume:1,pan:.08});
 Object.assign(track('track-4'),{volume:.3,pan:-.28});Object.assign(track('test-third'),{volume:.23,pan:.12});Object.assign(track('test-fifth'),{volume:.22,pan:.4});
 Object.assign(track('track-5'),{volume:.4,pan:-.12});Object.assign(track('test-shaker'),{volume:.5});Object.assign(track('test-open-hat'),{volume:.28});
 const sections=[];
 for(const sec of p.sections){
  if(sec.bars>=2&&(sec.name==='Groove · F'||sec.name==='Respiro · G')){
   const first=clone(sec);first.bars=sec.bars-1;sections.push(first);
   const fill=clone(sec);fill.bars=1;fill.name=sec.name==='Groove · F'?'Virada · F':'Preparação · G';
   fill.patterns||={};const hat=clone(fill.patterns['track-2']||track('track-2').steps);
   for(const i of [12,13,14,15])hat[i]={on:true,note:0,velocity:i===15?.8:.42+(i-12)*.08};
   fill.patterns['track-2']=hat;fill.active[p.tracks.findIndex(t=>t.id==='track-2')]=true;
   if(sec.name==='Groove · F'){
    const clap=clone(fill.patterns['track-1']||track('track-1').steps);clap[14]={on:true,note:0,velocity:.4};clap[15]={on:true,note:0,velocity:.55};fill.patterns['track-1']=clap;
   }
   sections.push(fill);
  }else sections.push(sec);
 }
 p.sections=sections;validate(p);
 const reference=clone(backup.project);reference.engineVersion??=1;
 return {...clone(backup),project:p,reference,versions:[...(backup.versions||[]),{at:Date.now(),label:'Versão A original — antes da revisão técnica',project:reference},{at:Date.now(),label:'Versão B — correções medidas, ainda não aprovada',project:clone(p)}]};
}
