import sys,json,itertools
from pathlib import Path
import networkx as nx
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from engine import calculate,graph,exact
from app import app
DATA=json.loads((Path(__file__).resolve().parents[1]/'data/network.json').read_text())
def test_every_failure():
    result=calculate(DATA,'exact');assert result['exact']['status']=='optimal'
    for topo,robust in [('mst',False),('resilient',True)]:
        g=nx.Graph();g.add_nodes_from(n['id'] for n in DATA['nodes'])
        for e in result['topologies'][topo]['edges']:g.add_edge(e['u'],e['v'])
        for u,v in list(g.edges()):
            h=g.copy();h.remove_edge(u,v);assert nx.is_connected(h)==robust
    assert len(result['topologies']['mesh']['edges'])==231

def test_exact_against_enumeration():
    g=nx.Graph();g.add_weighted_edges_from([(0,1,1),(1,2,1),(2,3,1),(0,2,3),(1,3,3),(0,3,4)],weight='km')
    for u,v,d in g.edges(data=True):d.update(id=f'{u}--{v}',kind='base')
    t=nx.minimum_spanning_tree(g,weight='km');h,meta=exact(g,t)
    candidates=[(u,v,d) for u,v,d in g.edges(data=True) if not t.has_edge(u,v)];best=float('inf')
    for mask in itertools.product([0,1],repeat=len(candidates)):
        trial=t.copy();cost=0
        for take,(u,v,d) in zip(mask,candidates):
            if take:trial.add_edge(u,v,**d);cost+=d['km']
        if not list(nx.bridges(trial)):best=min(best,cost)
    assert sum(d['km'] for u,v,d in h.edges(data=True) if not t.has_edge(u,v))==best

def test_api():
    c=app.test_client();r=c.get('/api/network/topologies');assert r.status_code==200
    res=r.get_json();edge=res['topologies']['resilient']['edges'][0]
    cut=c.post('/api/network/simulate-cut',json={'edge_id':edge['id'],'source':edge['u'],'target':edge['v']}).get_json()
    assert cut['stats']['connected'];assert cut['isolated_from_anchor']==[];assert len(cut['route']['path'])>2
    assert c.post('/api/network/simulate-cut',json={'edge_id':'invalid'}).status_code==400
    assert c.post('/api/network/topologies',json=[]).status_code==400
    assert c.post('/api/network/topologies',json={'nodes':[],'edges':[]}).status_code==400
