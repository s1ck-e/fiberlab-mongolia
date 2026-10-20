from pathlib import Path
import json, math
from flask import Flask, request, jsonify
from flask_cors import CORS
from engine import calculate, graph, stats
import networkx as nx
app=Flask(__name__);app.config['MAX_CONTENT_LENGTH']=2*1024*1024
# Explicit browser origins; development API is loopback-only.
CORS(app,origins=['http://localhost:8000','http://127.0.0.1:8000','https://fiberlab-mongolia.zanywren16.chatgpt.site'])
DEFAULT=Path(__file__).resolve().parents[1]/'data/network.json'

def data_input(body):return body if 'nodes' in body else json.loads(DEFAULT.read_text())
def hop_input(body):
    hop=body.get('hop_ms',.1)
    if not isinstance(hop,(int,float)) or not math.isfinite(hop) or hop<0:raise ValueError('Invalid hop_ms')
    return hop
@app.errorhandler(ValueError)
def bad(e):return jsonify(error=str(e)),400
@app.get('/api/health')
def health():return jsonify(status='ok')
@app.route('/api/network/topologies',methods=['GET','POST'])
def topologies():
    body=request.get_json(silent=True)
    if body is None:body={}
    if not isinstance(body,dict):raise ValueError('Expected JSON object')
    return jsonify(calculate(data_input(body),body.get('method','greedy'),hop_input(body)))
@app.post('/api/network/simulate-cut')
def simulate():
    body=request.get_json(silent=True)
    if not isinstance(body,dict):raise ValueError('Expected JSON object')
    data=data_input(body);hop=hop_input(body);result=calculate(data,body.get('method','greedy'),hop)
    topology=body.get('topology','resilient')
    if topology not in result['topologies']:raise ValueError('Unknown topology')
    h=nx.Graph();h.add_nodes_from(n['id'] for n in data['nodes'])
    for e in result['topologies'][topology]['edges']:h.add_edge(e['u'],e['v'],**e)
    edge_id=body.get('edge_id');chosen=next(((u,v) for u,v,d in h.edges(data=True) if d['id']==edge_id),None)
    if chosen is None:raise ValueError('Edge does not belong to topology')
    h.remove_edge(*chosen);s=stats(h,hop);anchor=body.get('anchor','ub' if 'ub' in h else data['nodes'][0]['id'])
    if anchor not in h:raise ValueError('Unknown anchor')
    reachable=nx.node_connected_component(h,anchor);isolated=sorted(set(h)-reachable)
    source,target=body.get('source'),body.get('target');routing=None
    if source is not None or target is not None:
        if source not in h or target not in h:raise ValueError('Unknown source/target')
        if nx.has_path(h,source,target):
            path=nx.shortest_path(h,source,target,weight='latency');routing={'path':path,'rtt':2*nx.path_weight(h,path,'latency')}
    return jsonify(cut=edge_id,stats=s,isolated_from_anchor=isolated,route=routing)
if __name__=='__main__':app.run(host='127.0.0.1',port=5000,debug=False)
