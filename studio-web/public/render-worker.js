import {render,wav} from './engine.js';
self.onmessage=({data})=>{try{const audio=render(data.project,data.options,data.samples),bytes=wav(audio);self.postMessage({bytes,stats:audio.stats,duration:audio.duration},[bytes.buffer])}catch(e){self.postMessage({error:e.message})}};
