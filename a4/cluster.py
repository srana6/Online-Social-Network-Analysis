"""
cluster.py
"""
from collections import Counter, OrderedDict
import matplotlib.pyplot as plt
import networkx as nx
import sys
import time, json
from TwitterAPI import TwitterAPI
#from config import *

followers_filename = 'followersdata.json'

def get_common_followers(filename):
    
    followers_count = Counter()
    follow_list = []
    
    with open(filename, 'r',encoding='utf-8') as file:
        for line in file:
            data_fetched = json.loads(line)
            
            for key,value in data_fetched.items():
                if len(value)>0:
                    followers_count.update(value)
                else:
                    print('no value in followerdata file')
    
    for key_name, values_list in dict(followers_count).items():
        if values_list > 2:
            follow_list.append(key_name)
     
    return follow_list

def girvan_newman(G, depth=0):
	
    if G.order() == 1:
        return [G.nodes()]

    def find_best_edge(G0):
        eb = nx.edge_betweenness_centrality(G0)
		
        return sorted(eb.items(), key=lambda x: x[1], reverse=True)[0][0]

	# Each component is a separate community. We cluster each of these.
    components = [c for c in nx.connected_component_subgraphs(G)]
    while len(components) == 1:
        edge_to_remove = find_best_edge(G)
        G.remove_edge(*edge_to_remove)
        components = [c for c in nx.connected_component_subgraphs(G)]
    return components


 
def get_edges(follow_list):
    edges_dict = {}
    user_dict = {}
    with open('tweets.txt',encoding='utf-8') as fp:
        for line in fp:
            data_fetched = line.split(' || ')
            user_dict[data_fetched[2]] = data_fetched[0]
   
    
    print("creating edges file...")
    top_list = set(follow_list)
    print("TOP_LIST::",len(top_list))
    
    with open(followers_filename, 'r',encoding='utf-8') as fp:
        for line in fp:
            data = json.loads(line)
            for key, value in data.items():
                common_list = set(value).intersection(top_list)
                print("Common_List::",len(common_list))
                if common_list:
                    edges_dict[str(user_dict[key])] = list(common_list)[:20]
                else:
                    edges_dict[str(user_dict[key])] = value[:20]
                     
    with open('edges.txt', 'w',encoding='utf-8') as fp:
        for key, value in edges_dict.items():
            for ids in value:
                if ids>-1:
                    fp.write(str(key)+ "-->"+ str(ids)+ "\n")
                else:
                    print('error')
    print("edges file created")

     
def draw_network(graph, filename):
    """
    Draw the network to a file. Only label the candidate nodes; the friend
    nodes should have no labels (to reduce clutter).
    """
    pos=nx.spring_layout(graph)
    plt.figure(figsize=(14,14))
    nx.draw_networkx(graph,pos, node_color='r',edge_color='b', alpha=.8, width=.5, node_size=400)
    plt.axis("off")
    plt.savefig(filename, format="PNG")
    

def read_graph():
	""" Read 'edges.txt.gz' into a networkx **undirected** graph.
	Done for you.
	Returns:
	A networkx undirected graph.
	"""
	return nx.read_edgelist('edges.txt', delimiter='-->')

def main():
    
    common_followers_list = get_common_followers(followers_filename) #find common followers for different users   
    get_edges(common_followers_list)
    
    graph = read_graph()

    draw_network(graph, 'network.png')
    print('graph has %d nodes and %d edges' %(graph.order(), graph.number_of_edges()))
    
    i = 0
    while i < 3:
       clusters = girvan_newman(graph)
       if len(clusters)==1:
           break
       graph = clusters[0]
       i += 1
        #print("total clusters formed: %s" %len(clusters))
        #for i in range(len(clusters)):
            #print("cluster[%s] has %s nodes" %(i, clusters[i].order()))
            
if __name__ == '__main__': 
   main()

