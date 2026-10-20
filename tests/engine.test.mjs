import test from 'node:test';import assert from'node:assert/strict';import{readFileSync}from'node:fs';import{topologies,stats,route,validate}from'../src/engine.mjs';
const data=JSON.parse(readFileSync(new URL('../data/network.json',import.meta.url))),t=topologies(data);
test('MST tree and 231-edge theoretical mesh',()=>{assert.equal(t.mst.length,21);assert.equal(stats(data.nodes,t.mst).bridges.length,21);assert.equal(t.mesh.length,231)});
test('Every resilient cable can fail without isolating a city',()=>{assert.equal(t.error,null);assert.equal(stats(data.nodes,t.resilient).bridges.length,0);for(const e of t.resilient)assert.equal(stats(data.nodes,t.resilient.filter(x=>x.id!==e.id)).connected,true)});
test('Every MST cut splits the graph',()=>{for(const e of t.mst)assert.equal(stats(data.nodes,t.mst.filter(x=>x.id!==e.id)).connected,false)});
test('Routing excludes cut link',()=>{for(const e of t.resilient){const r=route(data.nodes,t.resilient.filter(x=>x.id!==e.id),e.u,e.v);assert.ok(r);assert.ok(!r.edges.includes(e.id))}});
test('Reject invalid data, disconnected and infeasible candidates',()=>{assert.throws(()=>validate({...data,edges:[{u:'ub',v:'missing',km:1}]}));assert.throws(()=>topologies({...data,edges:[]}));const impossible=topologies({...data,edges:t.mst});assert.ok(impossible.error);assert.equal(impossible.resilient.length,0)});
test('Zero-latency local route and RTT formula',()=>{const nodes=[{id:'a'},{id:'b'}],edges=[{u:'a',v:'b',id:'a--b',km:100}];assert.equal(stats(nodes,edges,.1).rtt,1.2);assert.equal(route(nodes,edges,'a','a').rtt,0)});
