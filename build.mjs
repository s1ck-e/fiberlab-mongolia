import {build} from 'esbuild';
import {cpSync,mkdirSync} from 'node:fs';
mkdirSync('dist',{recursive:true});
await build({entryPoints:['src/app.jsx'],bundle:true,outdir:'dist',minify:true,loader:{'.png':'file'},define:{'process.env.NODE_ENV':'"production"'}});
cpSync('data/network.json','dist/network.json');
