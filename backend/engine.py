"""NetworkX reference engine; exact augmentation preserves the selected MST."""
import math, time
import networkx as nx
import numpy as np
from scipy.optimize import milp, Bounds, LinearConstraint

def validate(data):
    nodes, edges = data.get('nodes'), data.get('edges')
    if not isinstance(nodes,list) or not 2 <= len(nodes) <= 100 or not isinstance(edges,list):
        raise ValueError('Expected 2–100 nodes and an edges array')
    ids=set()
    for n in nodes:
        if not isinstance(n.get('id'),str) or not n['id'] or n['id'] in ids or not isinstance(n.get('name'),str): raise ValueError('Invalid/duplicate node')
        for field,limit in [('lat',90),('lon',180)]:
            if not isinstance(n.get(field),(int,float)) or not math.isfinite(n[field]) or abs(n[field])>limit: raise ValueError('Invalid coordinates')
        ids.add(n['id'])
    seen=set()
    for e in edges:
        if e.get('u') not in ids or e.get('v') not in ids or e['u']==e['v']: raise ValueError('Invalid edge endpoint')
        if not isinstance(e.get('km'),(int,float)) or not math.isfinite(e['km']) or e['km']<=0: raise ValueError('Invalid edge weight')
        pair=tuple(sorted((e['u'],e['v'])))
        if pair in seen: raise ValueError('Duplicate edge')
        seen.add(pair)
    return data

def graph(data):
    validate(data); g=nx.Graph()
    for n in data['nodes']:g.add_node(n['id'],**n)
    for e in data['edges']:g.add_edge(e['u'],e['v'],km=e['km'],id='--'.join(sorted((e['u'],e['v']))),kind='base')
    return g

def greedy(g,t):
    h=t.copy(); candidates=[(u,v,d) for u,v,d in g.edges(data=True) if not h.has_edge(u,v)]
    while True:
        count=len(list(nx.bridges(h)))
        if not count:break
        best=None;score=math.inf
        for u,v,d in candidates:
            trial=h.copy();trial.add_edge(u,v,**d)
            gain=count-len(list(nx.bridges(trial)))
            if gain and d['km']/gain<score:best=(u,v,d);score=d['km']/gain
        if best is None:raise ValueError('Candidate graph cannot be made 2-edge-connected')
        u,v,d=best;h.add_edge(u,v,**{**d,'kind':'extra'});candidates=[c for c in candidates if c[:2]!=(u,v)]
    for u,v,d in sorted(list(h.edges(data=True)),key=lambda e:-e[2]['km']):
        if d['kind']!='extra':continue
        h.remove_edge(u,v)
        if list(nx.bridges(h)):h.add_edge(u,v,**d)
    return h

def exact(g,t):
    te=list(t.edges()); index={frozenset(e):i for i,e in enumerate(te)}
    candidates=[(u,v,d) for u,v,d in g.edges(data=True) if not t.has_edge(u,v)]
    if not candidates:raise ValueError('No augmentation candidates')
    A=np.zeros((len(te),len(candidates)))
    for j,(u,v,d) in enumerate(candidates):
        path=nx.shortest_path(t,u,v)
        for a,b in zip(path,path[1:]):A[index[frozenset((a,b))],j]=1
    if np.any(A.sum(axis=1)==0):raise ValueError('Some MST edges have no backup candidate')
    result=milp(c=np.array([d['km'] for _,_,d in candidates]),integrality=np.ones(len(candidates)),bounds=Bounds(0,1),constraints=LinearConstraint(A,np.ones(len(te)),np.full(len(te),np.inf)),options={'time_limit':5.0})
    if result.x is None:raise ValueError('Exact solver returned no feasible result')
    h=t.copy()
    for x,(u,v,d) in zip(result.x,candidates):
        if x>.5:h.add_edge(u,v,**{**d,'kind':'extra'})
    if list(nx.bridges(h)):raise ValueError('Solver result failed connectivity verification')
    return h,dict(status='optimal' if result.status==0 else 'feasible_time_limited',scope='minimum augmentation of this fixed MST',mip_gap=float(result.mip_gap) if result.mip_gap is not None else None)

def distance(a,b):
    la,lb=math.radians(a['lat']),math.radians(b['lat']);dl=lb-la;dn=math.radians(b['lon']-a['lon'])
    return 12742*math.asin(math.sqrt(math.sin(dl/2)**2+math.cos(la)*math.cos(lb)*math.sin(dn/2)**2))

def mesh(data):
    h=nx.Graph();h.add_nodes_from((n['id'],n) for n in data['nodes'])
    for i,a in enumerate(data['nodes']):
        for b in data['nodes'][i+1:]:h.add_edge(a['id'],b['id'],km=round(distance(a,b)*1.25,1),id='--'.join(sorted((a['id'],b['id']))),kind='theoretical')
    return h

def stats(g,hop_ms=.1):
    connected=nx.is_connected(g); br=['--'.join(sorted(e)) for e in nx.bridges(g)]
    for u,v,d in g.edges(data=True):d['latency']=d['km']*.005+hop_ms
    worst=0;pair=None
    for u,ds in nx.all_pairs_dijkstra_path_length(g,weight='latency'):
        for v,w in ds.items():
            if w*2>worst:worst=w*2;pair=[u,v]
    return dict(km=sum(d['km'] for _,_,d in g.edges(data=True)),bridges=br,connected=connected,tolerant=connected and not br,rtt=worst if connected else None,pair=pair if connected else None,components=[sorted(c) for c in nx.connected_components(g)])

def serialize(g,hop=.1):
    return dict(edges=[dict(u=u,v=v,**{k:v for k,v in d.items() if k!='latency'}) for u,v,d in g.edges(data=True)],stats=stats(g,hop))

def calculate(data,method='greedy',hop=.1):
    start=time.perf_counter();g=graph(data)
    if not nx.is_connected(g):raise ValueError('Candidate graph is disconnected')
    if list(nx.bridges(g)):raise ValueError('Candidate graph contains bridges: add backup corridors')
    t=nx.minimum_spanning_tree(g,weight='km',algorithm='kruskal'); meta={'status':'heuristic','scope':'greedy bridge-cover + pruning'}
    if method=='exact':h,meta=exact(g,t)
    elif method=='greedy':h=greedy(g,t)
    else:raise ValueError('Unknown method')
    return dict(nodes=data['nodes'],topologies={k:serialize(v,hop) for k,v in [('mst',t),('resilient',h),('mesh',mesh(data))]},exact=meta,elapsed_ms=(time.perf_counter()-start)*1000)
