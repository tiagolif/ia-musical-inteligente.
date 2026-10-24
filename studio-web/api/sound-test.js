import data from '../lib/sound-test-data.js';
const audio=Buffer.from(data,'base64');
export default function handler(req,res){
 res.setHeader('Content-Type','audio/mpeg');res.setHeader('Content-Disposition','inline; filename="studio-test-500hz.mp3"');res.setHeader('Accept-Ranges','bytes');res.setHeader('Cache-Control','public, max-age=86400');
 if(!['GET','HEAD'].includes(req.method))return res.status(405).end();
 let start=0,end=audio.length-1;
 if(req.headers.range){const match=/^bytes=(\d*)-(\d*)$/.exec(req.headers.range);if(!match||(!match[1]&&!match[2])){res.setHeader('Content-Range','bytes */'+audio.length);return res.status(416).end()}if(!match[1])start=Math.max(0,audio.length-Number(match[2]));else{start=Number(match[1]);if(match[2])end=Math.min(end,Number(match[2]))}if(start>end||start>=audio.length){res.setHeader('Content-Range','bytes */'+audio.length);return res.status(416).end()}res.status(206);res.setHeader('Content-Range','bytes '+start+'-'+end+'/'+audio.length)}
 res.setHeader('Content-Length',end-start+1);if(req.method==='HEAD')return res.end();return res.end(audio.subarray(start,end+1));
}
