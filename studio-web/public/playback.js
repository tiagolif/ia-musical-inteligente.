// Native media playback deliberately does not depend on a running AudioContext.
export function playbackError(error){
 if(error?.name==='NotAllowedError')return 'O navegador bloqueou o início automático. Toque no ▶ do player de áudio abaixo.';
 if(error?.name==='NotSupportedError')return 'O navegador não conseguiu abrir este áudio. Use o teste MP3 de saída de som.';
 return 'Falha ao iniciar áudio: '+(error?.message||'erro desconhecido');
}
export function mediaError(code){return ({1:'Reprodução cancelada.',2:'Falha ao carregar o arquivo de áudio.',3:'O navegador não conseguiu decodificar o áudio.',4:'Formato de áudio não suportado pelo navegador.'})[code]||'Falha de reprodução de áudio.'}
export async function startNative(player){player.muted=false;player.volume=1;try{await player.play();return {started:true}}catch(error){return {started:false,message:playbackError(error)}}}
export function renderHasSignal(data){return Number.isFinite(data?.stats?.peakDb)&&data.stats.peakDb> -100}
