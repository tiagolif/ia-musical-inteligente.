export const PRESETS={kick:[['deep','Deep · redondo'],['punch','Punch · seco'],['sub','Sub · longo']],clap:[['tight','Tight · curto'],['wide','Wide · aberto'],['snap','Snap · estalo']],hat:[['closed','Closed · fechado'],['open','Open · aberto'],['soft','Soft · suave']],bass:[['round','Round · senoidal'],['acid','Acid · serrilhado'],['pluck','Pluck · curto']],synth:[['glass','Glass · cristalino'],['warm','Warm · suave'],['bright','Bright · incisivo']]};
export const clone=x=>structuredClone(x);
export function createProject(style='house'){
 const defs=[['kick','Kick','#c4a0ff'],['clap','Clap','#f7a0b4'],['hat','Hi-hat','#f5cf82'],['bass','Bass','#6bdac6'],['synth','Chords','#91baff'],['synth','Lead','#c3a3f5']];
 return {schemaVersion:3,title:'Nova produção',brief:'',bpm:126,root:57,master:.75,swing:0,seed:1701,tracks:defs.map(([type,name,color],j)=>({id:'track-'+j,name,type,color,preset:PRESETS[type][0][0],sampleId:null,volume:j===4?.38:.65,pan:0,mute:false,solo:false,locked:false,filter:18000,decay:1,transpose:0,steps:Array.from({length:16},(_,i)=>({on:j===0?i%4===0:j===1?i%8===4:j===2?i%2===1:j===3?[0,3,6,10,14].includes(i):j===4?i%8===0:[2,7,11,14].includes(i),note:j===3?[0,0,7,3][Math.floor(i/4)]:j===5?[12,15,19,22][Math.floor(i/4)]:0,velocity:1}))})),sections:[{name:'Intro',bars:4,active:[true,false,true,false,true,false]},{name:'Groove',bars:8,active:[true,true,true,true,true,false]},{name:'Break',bars:4,active:[false,false,true,false,true,true]},{name:'Drop',bars:8,active:[true,true,true,true,true,true]},{name:'Outro',bars:4,active:[true,false,true,true,false,false]}]};
}
const finite=(x,a,b)=>Number.isFinite(x)&&x>=a&&x<=b;
export function validate(p){
 if(!p||p.schemaVersion!==3||typeof p.title!=='string'||!p.title.trim()||p.title.length>120||typeof p.brief!=='string'||p.brief.length>4000||!finite(p.bpm,40,240)||!finite(p.root,24,84)||!finite(p.master,0,1)||!finite(p.swing,0,.45)||!Number.isInteger(p.seed)||!Array.isArray(p.tracks)||p.tracks.length<1||p.tracks.length>16)throw Error('Projeto inválido');
 const ids=new Set();for(const t of p.tracks){if(typeof t.id!=='string'||ids.has(t.id)||typeof t.name!=='string'||t.name.length>60||!PRESETS[t.type]||!PRESETS[t.type].some(x=>x[0]===t.preset)||!finite(t.volume,0,1)||!finite(t.pan,-1,1)||!finite(t.filter,100,20000)||!finite(t.decay,.2,3)||!finite(t.transpose,-24,24)||!['mute','solo','locked'].every(k=>typeof t[k]==='boolean')||(t.sampleId!==null&&(typeof t.sampleId!=='string'||t.sampleId.length>100))||!Array.isArray(t.steps)||t.steps.length!==16||!t.steps.every(s=>s&&typeof s.on==='boolean'&&finite(s.note,-24,36)&&finite(s.velocity,0,1)))throw Error('Pista inválida');ids.add(t.id)}
 if(!Array.isArray(p.sections)||!p.sections.length||p.sections.length>16||p.sections.reduce((n,s)=>n+s.bars,0)>64||!p.sections.every(s=>typeof s.name==='string'&&s.name.length<=40&&Number.isInteger(s.bars)&&s.bars>=1&&s.bars<=32&&Array.isArray(s.active)&&s.active.length===p.tracks.length&&s.active.every(x=>typeof x==='boolean')))throw Error('Arranjo inválido');return p;
}
export function applyCommand(project,cmd){
 const p=clone(project);if(!cmd||typeof cmd.action!=='string')throw Error('Comando inválido');
 if(cmd.action==='set_tempo'){p.bpm=cmd.bpm}else if(cmd.action==='set_brief'){p.brief=cmd.brief}else if(cmd.action==='set_arrangement'){if(p.tracks.some(t=>t.locked))throw Error('Desbloqueie as pistas antes de substituir o arranjo');p.sections=clone(cmd.sections)}else{
 const t=p.tracks.find(t=>t.id===cmd.trackId);if(!t)throw Error('Pista não encontrada');if(t.locked&&cmd.action!=='set_lock')throw Error('Pista aprovada e bloqueada. Desbloqueie para editar.');
 if(cmd.action==='replace_instrument'){if(!PRESETS[t.type].some(x=>x[0]===cmd.preset))throw Error('Preset incompatível');t.preset=cmd.preset;t.sampleId=null}
 else if(cmd.action==='set_sample')t.sampleId=cmd.sampleId;
 else if(cmd.action==='set_lock')t.locked=cmd.locked;
 else if(cmd.action==='set_steps')t.steps=clone(cmd.steps);
 else if(cmd.action==='set_track'){for(const k of ['volume','pan','mute','solo','filter','decay','transpose'])if(k in cmd)t[k]=cmd[k]}
 else throw Error('Ação desconhecida');
 }return validate(p);
}
export function migrate(old){if(old?.schemaVersion===3)return validate(old);if(old&&Array.isArray(old.tracks)&&old.tracks.length===5){const p=createProject();p.bpm=old.bpm;p.tracks=p.tracks.slice(0,5);p.sections.forEach(s=>s.active=s.active.slice(0,5));const map=[0,2,3,1,4];for(let j=0;j<5;j++){const t=old.tracks[map[j]];p.tracks[j].volume=t.volume;p.tracks[j].mute=t.mute;p.tracks[j].steps.forEach((s,i)=>s.on=t.steps[i])}return validate(p)}throw Error('Arquivo incompatível')}
export function events(project,{mode='arrangement',section=0,bars,trackId}={}){
 validate(project);const result=[];const spb=60/project.bpm/4;let offset=0;const sections=mode==='loop'?[{...project.sections[section],bars:bars||1}]:project.sections;const solo=project.tracks.some(t=>t.solo);
 for(const sec of sections){for(let bar=0;bar<sec.bars;bar++)project.tracks.forEach((t,j)=>{if(!sec.active[j]||t.mute||(solo&&!t.solo)||(trackId&&trackId!==t.id))return;t.steps.forEach((s,i)=>{if(s.on)result.push({track:j,step:i,note:s.note,velocity:s.velocity,time:(offset+bar*16+i+(i%2?project.swing:0))*spb,bar:offset/16+bar})})});offset+=sec.bars*16}
 return {events:result,duration:offset*spb+2};
}
