import networkx as nx
from scipy.stats import expon, gamma
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
import seaborn as sns
from copy import deepcopy


##### Utils

def trigger_threshold(requested, funds, supply, alpha, params):
    '''
    Description:
    Function that determines threshold for proposals being accepted. 

    Parameters:
    requested: float, funds requested
    funds: float, funds
    supply: float
    alpha: float
    params: dictionary of parameters as floats

    Returns:
    Threshold value
    '''

    share = requested/funds
    if share < params['beta']:
        threshold = params['rho']*supply/(params['beta']-share)**2  * 1/(1-alpha)
        return threshold 
    else: 
        return np.inf

def initial_social_network(network, scale = 1, sigmas=3):
    '''
    Description:
    Function to initialize network x social network edges

    Parameters:
    network: network x digraph object
    scale: optional float
    sigmas: optional float

    Assumptions:
    Initialized network x object

    Returns:
    Updated networkx object with influence edges
    '''
    participants = get_nodes_by_type(network, 'participant')
    
    for i in participants:
        for j in participants:
            if not(j==i):
                influence_rv = expon.rvs(loc=0.0, scale=scale)
                if influence_rv > scale+sigmas*scale**2:
                    network.add_edge(i,j)
                    network.edges[(i,j)]['influence'] = influence_rv
                    network.edges[(i,j)]['type'] = 'influence'
    return network
                    
def initial_conflict_network(network, rate = .25):
    '''
    Definition:
    Function to initialize network x conflict edges

    Parameters:
    network: network x digraph object
    rate: optional float

    Assumptions:
    Initialized network x object

    Returns:
    Updated networkx object with conflict edges

    '''
    proposals = get_nodes_by_type(network, 'proposal')
    
    for i in proposals:
        for j in proposals:
            if not(j==i):
                conflict_rv = np.random.rand()
                if conflict_rv < rate :
                    network.add_edge(i,j)
                    network.edges[(i,j)]['conflict'] = 1-conflict_rv
                    network.edges[(i,j)]['type'] = 'conflict'
    return network

def gen_new_participant(network, new_participant_holdings):
    '''
    Definition:
    Driving processes for the  arrival of participants.

    Parameters:
    network: networkx object
    new_participant_holdings: Tokens of new participants

    Assumptions:
    Initialized network x object

    Returns:
    Update network x object
    '''
    
    i = len([node for node in network.nodes])
    
    network.add_node(i)
    network.nodes[i]['type']="participant"
    
    s_rv = np.random.rand() 
    network.nodes[i]['sentiment'] = s_rv
    network.nodes[i]['holdings']=new_participant_holdings

    # influence edges
    social_links(network, i)
    
    for j in get_nodes_by_type(network, 'proposal'):
        network.add_edge(i, j)
        # uniform distribution between -1 and 1
        a_rv = a_rv = np.random.uniform(-1,1,1)[0]
        network.edges[(i, j)]['affinity'] = a_rv
        network.edges[(i,j)]['tokens'] = 0 
        network.edges[(i, j)]['conviction'] = 0
        network.edges[(i,j)]['type'] = 'support'
    
    return network
    

def gen_new_proposal(network, funds, supply, funds_requested,params):
    '''
    Definition:
    Driving processes for the arrival of proposals.

    Parameters:
    network: networkx object
    funds: float
    supply: float
    funds_requested: float
    params: dictionary of float parameters

    Assumptions:
    Initialized network x object

    Returns:
    Update network x object with new proposals
    '''
    j = len([node for node in network.nodes])
    network.add_node(j)
    network.nodes[j]['type']="proposal"
    
    network.nodes[j]['conviction']=0
    network.nodes[j]['status']='candidate'
    network.nodes[j]['age']=0
    
    network.nodes[j]['funds_requested'] =funds_requested
    
    network.nodes[j]['trigger']= trigger_threshold(funds_requested, funds, supply, params['alpha'],params)
    
    participants = get_nodes_by_type(network, 'participant')
    proposing_participant = np.random.choice(participants)

    # conflict edges
    conflict_links(network, j)
    
    for i in participants:
        network.add_edge(i, j)
        if i==proposing_participant:
            network.edges[(i, j)]['affinity']=1
        else:
            a_rv = np.random.uniform(-1,1,1)[0]
            network.edges[(i, j)]['affinity'] = a_rv
            
        network.edges[(i, j)]['conviction'] = 0
        network.edges[(i,j)]['tokens'] = 0
        network.edges[(i,j)]['type'] = 'support'
        
    return network
        

def get_nodes_by_type(g, node_type_selection):
    '''
    Definition:
    Function to extract nodes based by named type

    Parameters:
    g: network x object
    node_type_selection: node type


    Returns:
    List column of the desired information 

    Example:
    proposals = get_nodes_by_type(network, 'proposal')

    '''
    return [node for node in g.nodes if g.nodes[node]['type']== node_type_selection ]

def get_sentimental(sentiment, force, decay=.1):
    '''
    Definition:
    Function to update sentiment

    Parameters:
    sentiment: float
    force: float
    decay: optional float

    Returns:
    returns updated sentiment between 1 and 0.
    '''
    mu = decay
    sentiment = sentiment*(1-mu) + force*mu
    
    if sentiment > 1:
        sentiment = 1
    elif sentiment < 0:
        sentiment = 0
        
    return sentiment

def get_edges_by_type(g, edge_type_selection):
    '''
    Definition:
    Function to extract edges based on type

    Parameters:
    g: network x object
    edge_type_selection: edge type


    Returns:
    List of edges
    '''
    return [edge for edge in g.edges if g.edges[edge]['type']== edge_type_selection ]


def conviction_order(network, proposals):
    '''
    Definition:
    Function to sort conviction order

    Parameters:
    network: network x object
    proposals: list of proposals

    Returns:
    List of ordered proposals
    '''
    ordered = sorted(proposals, key=lambda j:network.nodes[j]['conviction'] , reverse=True)
    
    return ordered
    


def social_links(network, participant, scale = 1):
    '''
    Definition:
    Function to add influence edges to network

    Parameters:
    network: network x object
    participant: int

    Returns:
    update network x object with social links
    ''' 
    participants = get_nodes_by_type(network, 'participant')
    
    i = participant
    for j in participants:
        if not(j==i):
            influence_rv = expon.rvs(loc=0.0, scale=scale)
            if influence_rv > scale+scale**2:
                network.add_edge(i,j)
                network.edges[(i,j)]['influence'] = influence_rv
                network.edges[(i,j)]['type'] = 'influence'
    return network


def conflict_links(network,proposal, rate = .25):
    '''
    Definition:
    Function to add conflict edges to network

    Parameters:
    network: network x object
    proposal: int
    rate: optional float 

    Returns:
    update network x object with conflict links
    '''
    proposals = get_nodes_by_type(network, 'proposal')
    
    i = proposal
    for j in proposals:
        if not(j==i):
            conflict_rv = np.random.rand()
            if conflict_rv < rate :
                network.add_edge(i,j)
                network.edges[(i,j)]['conflict'] = 1-conflict_rv
                network.edges[(i,j)]['type'] = 'conflict'
    return network

def social_affinity_booster(network, proposal, participant):
    '''
    Definition:
    Function to create aggregate influence for participant

    Parameters:
    network: network x object
    proposal: int
    participant: int

    Returns:
    Float of aggregated affinity boost
    '''
    participants = get_nodes_by_type(network, 'participant')
    influencers = get_edges_by_type(network, 'influence')
    
    j=proposal
    i=participant
    
    i_tokens = network.nodes[i]['holdings']
   
    influence = np.array([network.edges[(i,node)]['influence'] for node in participants if (i, node) in influencers ])
    tokens = np.array([network.edges[(node,j)]['tokens'] for node in participants if (i, node) in influencers ])    
    
    influence_sum = np.sum(influence)
    
    if influence_sum>0:
        boosts = np.sum(tokens*influence)/(influence_sum*i_tokens)
    else:
        boosts = 0
    
    return np.sum(boosts)
    
def pad(vec, length,fill=True):
    '''
    Definition:
    Function to pad vectors for moving to 2d

    Parameters:
    vec: numpy array
    length: int
    fill: optional boolean for filling array with zeros

    Returns:
    padded numpy array
    '''
    
    if fill:
        padded = np.zeros(length,)
    else:
        padded = np.empty(length,)
        padded[:] = np.nan
        
    for i in range(len(vec)):
        padded[i]= vec[i]
        
    return padded

def make2D(key, data, fill=False):
    '''
    Definition:
    Function to pad vectors for moving to 2d

    Parameters:
    vec: numpy array
    length: int
    fill: optional boolean for filling array with zeros

    Returns:
    padded numpy array
    '''
    maxL = data[key].apply(len).max()
    newkey = 'padded_'+key
    data[newkey] = data[key].apply(lambda x: pad(x,maxL,fill))
    reshaped = np.array([a for a in data[newkey].values])
    
    return reshaped

def initialize_network(n,m, initial_funds, supply, params):
    '''
    Definition:
    Function to initialize network x object

    Parameters:
    n: initial number of participants
    m: initial number of proposals
    initial_funds: float of funds
    supply: float of supply
    params: dictionary of parameter floats

    Returns:
    initialized network x object for the beginning of the simulation
    '''
    # initilize network x graph
    network = nx.DiGraph()
    # create participant nodes with type and token holding
    for i in range(n):
        network.add_node(i)
        network.nodes[i]['type']= "participant"
      
        # This is an exponential random variable with a shape (loc) and scale parameter to drive the shape of the distributino. 
        # See the two links below to learn more about it. 
        # https://en.wikipedia.org/wiki/Exponential_distribution
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.expon.html
        h_rv = expon.rvs(loc=0.0, scale= supply/n)
        network.nodes[i]['holdings'] = h_rv 
        
        s_rv = np.random.rand() 
        network.nodes[i]['sentiment'] = s_rv
    
    participants = get_nodes_by_type(network, 'participant')
    initial_supply = np.sum([ network.nodes[i]['holdings'] for i in participants])
       
    
    # Generate initial proposals
    for ind in range(m):
        j = n+ind
        network.add_node(j)
        network.nodes[j]['type']="proposal"
        network.nodes[j]['conviction'] = 0
        network.nodes[j]['status'] = 'candidate'
        network.nodes[j]['age'] = 0
        
        # This is a gamma random variable with a shape (loc) and scale parameter to drive the shape of the distributino. 
        # See the two links below to learn more about it. 
        # https://en.wikipedia.org/wiki/Gamma_distribution
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gamma.html
        r_rv = gamma.rvs(3,loc=0.001, scale=(initial_funds * params['beta'])*.05)
        network.nodes[j]['funds_requested'] = r_rv
        
        network.nodes[j]['trigger']= trigger_threshold(r_rv, initial_funds, initial_supply, params['alpha'],params)
        
        for i in range(n):
            network.add_edge(i, j)
            
            rv = np.random.rand()
            # see below for information on the uniform distribution. In this case, the values will be between -1 and 1
            # https://numpy.org/doc/stable/reference/random/generated/numpy.random.uniform.html 
            a_rv = np.random.uniform(-1,1,1)[0]
            network.edges[(i, j)]['affinity'] = a_rv
            network.edges[(i, j)]['tokens'] = 0
            network.edges[(i, j)]['conviction'] = 0
            network.edges[(i, j)]['type'] = 'support'
            
        proposals = get_nodes_by_type(network, 'proposal')
        total_requested = np.sum([ network.nodes[i]['funds_requested'] for i in proposals])
        
        network = initial_conflict_network(network, rate = .25)
        network = initial_social_network(network, scale = 1)
        
    return network


def config_initialization(configs,initial_values):
    '''
    Definition:
    Function to initialize network x object during the config.py

    Parameters:
    configs: cadCAD config object
    initial_values: dictionary of initial network values

    Returns:
    Updates state_variables in cadCAD config object with initialized network x object 


    '''
    # Initialize network x
    for c in configs:
        c.initial_state = deepcopy(c.initial_state)

        print("Params (config.py) : ", c.sim_config['M'])

        c.initial_state['network'] = initialize_network(initial_values['n'],initial_values['m'],
                                                initial_values['funds'],
                                                initial_values['supply'],c.sim_config['M'])
        
        return c.initial_state['network']
    
    
def schema_check(simulation_results,schema_dictionary,cadCAD_columns = ['simulation','subset','run','substep','timestep']):
    '''
    Description:
    Function to check simulation variables types against pre-defined schema

    Parameters:
    simulation_result: cadCAD simulation results dataframe
    schema_dictionary: state schema dictionary
    cadCAD_columns: optional, list of cadCAD columns
    
    Returns:
    {'state': Boolean}
    '''
    schema_check = {}
    for i in simulation_results.columns:
        if i not in cadCAD_columns:
            result = type(simulation_results[str(i)].values[-1]) == type(schema_dictionary[str(i)])
            schema_check[i] = result
    return schema_check       


def trigger_sweep(field, trigger_func,params,supply=10**9, x_extra=.001):
    '''
    Definition:
    Function to plot trigger function under parameter sweep

    Parameters:
    field: String of field to be swept, either effective_supply or alpha
    trigger_func: function of the trigger
    params: dictionary of parameters
    supply: optional float of supply
    x_extra: optional vector value

    Returns:
    Plot of trigger parameter sweep
    '''
    rho = params['rho'][0]
    beta = params['beta'][0]
    xmax=beta- np.sqrt(rho)
    alpha = params['alpha'][0]

    if field == 'effective_supply':
        share_of_funds = np.arange(0,xmax*(1+x_extra),.001)
        total_supply = np.arange(0,supply*10, supply/100) 
        demo_data_XY = np.outer(share_of_funds,total_supply)

        demo_data_Z0=np.empty(demo_data_XY.shape)
        demo_data_Z1=np.empty(demo_data_XY.shape)
        demo_data_Z2=np.empty(demo_data_XY.shape)
        demo_data_Z3=np.empty(demo_data_XY.shape)
        for sof_ind in range(len(share_of_funds)):
            sof = share_of_funds[sof_ind]
            for ts_ind in range(len(total_supply)):
                ts = total_supply[ts_ind]
                tc = ts /(1-alpha)
                trigger = trigger_func(sof, 1, ts, alpha,beta, rho) 
                demo_data_Z0[sof_ind,ts_ind] = np.log10(trigger)
                demo_data_Z1[sof_ind,ts_ind] = trigger
                demo_data_Z2[sof_ind,ts_ind] = trigger/tc #share of maximum possible conviction
                demo_data_Z3[sof_ind,ts_ind] = np.log10(trigger/tc)
        return {'log10_trigger':demo_data_Z0,
                'trigger':demo_data_Z1,
                'share_of_max_conv': demo_data_Z2,
                'log10_share_of_max_conv':demo_data_Z3,
                'total_supply':total_supply,
                'share_of_funds':share_of_funds,
                'alpha':alpha}
    elif field == 'alpha':
        #note if alpha >.01 then this will give weird results max alpha will be >1
        alpha = np.arange(0,1,.001)
        share_of_funds = np.arange(0,xmax*(1+x_extra),.001)
        demo_data_XY = np.outer(share_of_funds,alpha)

        demo_data_Z4=np.empty(demo_data_XY.shape)
        demo_data_Z5=np.empty(demo_data_XY.shape)
        demo_data_Z6=np.empty(demo_data_XY.shape)
        demo_data_Z7=np.empty(demo_data_XY.shape)
        for sof_ind in range(len(share_of_funds)):
            sof = share_of_funds[sof_ind]
            for a_ind in range(len(alpha)):
                ts = supply
                a = alpha[a_ind]
                tc = ts /(1-a)
                trigger = trigger_func(sof, 1, ts, a, beta, rho)
                demo_data_Z4[sof_ind,a_ind] = np.log10(trigger)
                demo_data_Z5[sof_ind,a_ind] = trigger
                demo_data_Z6[sof_ind,a_ind] = trigger/tc #share of maximum possible conviction
                demo_data_Z7[sof_ind,a_ind] = np.log10(trigger/tc)
        
        return {'log10_trigger':demo_data_Z4,
               'trigger':demo_data_Z5,
               'share_of_max_conv': demo_data_Z6,
               'log10_share_of_max_conv':demo_data_Z7,
               'alpha':alpha,
               'share_of_funds':share_of_funds,
               'supply':supply}
        
    else:
        return "invalid field"
    

### Plotting

def snap_plot(nets, size_scale = 1/10, dims = (8,8), savefigs=False):
    '''
    Definition:
    Function to create plot of participants and proposals

    Parameters:
    nets: network x object
    size_scale: optional size scaling parameter
    dims: optional figure dimension
    savefigs: optional boolean for saving figure

    Returns:
    Bipartite graph of participants and proposals at a specific timestep
    '''

    last_net = nets[-1]
        
    last_props=get_nodes_by_type(last_net, 'proposal')
    M = len(last_props)
    last_parts=get_nodes_by_type(last_net, 'participant')
    N = len(last_parts)
    pos = {}
    
    for ind in range(N):
        i = last_parts[ind] 
        pos[i] = np.array([0, 2*ind-N])

    for ind in range(M):
        j = last_props[ind] 
        pos[j] = np.array([1, 2*N/M *ind-N])

    
    if savefigs:
        counter = 0
        length = 10

    plt.ion()
    length = len(nets)

    for net in nets:
        edges = get_edges_by_type(net, 'support')
        max_tok = np.max([net.edges[e]['tokens'] for e in edges])

        E = len(edges)
        
        net_props = get_nodes_by_type(net, 'proposal')
        net_parts = get_nodes_by_type(net, 'participant')
        net_node_label ={}
        
        num_nodes = len([node for node in net.nodes])
        
        node_color = np.empty((num_nodes,4))
        node_size = np.empty(num_nodes)

        edge_color = np.empty((E,4))
        cm = plt.get_cmap('Reds')

        cNorm  = colors.Normalize(vmin=0, vmax=max_tok)
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
    
        net_cand = [j for j in net_props if net.nodes[j]['status']=='candidate']

        for j in net_props:
            node_size[j] = net.nodes[j]['funds_requested']*size_scale
            if net.nodes[j]['status']=="candidate":
                node_color[j] = colors.to_rgba('blue')
                trigger = net.nodes[j]['trigger']      
                conviction = net.nodes[j]['conviction']
                percent_of_trigger = "          "+str(int(100*conviction/trigger))+'%'
                net_node_label[j] = str(percent_of_trigger)
            elif net.nodes[j]['status']=="active":
                node_color[j] = colors.to_rgba('orange')
                net_node_label[j] = ''
            elif net.nodes[j]['status']=="completed":
                node_color[j] = colors.to_rgba('green')
                net_node_label[j] = ''
            elif net.nodes[j]['status']=="failed":
                node_color[j] = colors.to_rgba('gray')
                net_node_label[j] = ''
            elif net.nodes[j]['status']=="killed":
                node_color[j] = colors.to_rgba('black')
                net_node_label[j] = ''

        for i in net_parts:    
            node_size[i] = net.nodes[i]['holdings']*size_scale/10
            node_color[i] = colors.to_rgba('red')
            net_node_label[i] = ''

        included_edges = []
        for ind in range(E):
            e = edges[ind]
            tokens = net.edges[e]['tokens']
            edge_color[ind] = scalarMap.to_rgba(tokens)
            if e[1] in net_cand:
                included_edges.append(e)
            

        iE = len(included_edges)
        included_edge_color = np.empty((iE,4))
        for ind in range(iE):
            e = included_edges[ind]
            tokens = net.edges[e]['tokens']
            included_edge_color[ind] = scalarMap.to_rgba(tokens)
        
    
        plt.clf()
        plt.close()
        plt.figure(figsize=dims)
        nx.draw(net,
            pos=pos, 
            node_size = node_size,
            node_color = node_color, 
            edge_color = included_edge_color, 
            edgelist=included_edges,
            labels = net_node_label,
            font_size = 5)
        plt.title('Tokens Staked by Partipants to Proposals')
        plt.axis('on')
        plt.xticks([])
        plt.yticks([])
        plt.pause(0.2)
        if i == length-1:
            plt.ioff()
        plt.show()

        if savefigs:
            plt.savefig('conviction-voting-cadcad/models/v3/images/snap/'+str(counter)+'.png',bbox_inches='tight')
            counter = counter+1
        plt.show()


def affinities_plot(network, dims = (8, 8)):
    '''
    Definition:
    Function to plot affinities between participants and proposals

    Parameters:
    network: network x object
    dims: optional figure dimensions 

    Returns:
    plot of affinities between participants and proposals
    '''

    last_props=get_nodes_by_type(network, 'proposal')
    M = len(last_props)
    last_parts=get_nodes_by_type(network, 'participant')
    N = len(last_parts)

    affinities = np.empty((N,M))
    for i_ind in range(N):
        for j_ind in range(M):
            i = last_parts[i_ind]
            j = last_props[j_ind]
            affinities[i_ind][j_ind] = network.edges[(i,j)]['affinity']

    fig, ax = plt.subplots(figsize=dims)

    sns.font_scale=0.5
    sns.heatmap(affinities,
                xticklabels=last_props,
                yticklabels=last_parts,
                square=True,
                cbar=True,
                cmap = plt.cm.RdYlGn,
                ax=ax
            )

    plt.title('Affinities between participants and proposals')
    plt.xticks([])
    plt.yticks([])
    plt.ylabel('Participant_id')
    plt.xlabel('Proposal_id')


def trigger_grid(supply_sweep, alpha_sweep):
    '''
    Definition:
    Function to plot the trigger sweeps

    Parameters:
    supply_sweep: dictionary of supply sweep 
    alpha_sweep: dictionary of alpha sweeps

    Returns:
    grid of 2 matplotib plots

    Example:

    trigger_grid(supply_sweep, alpha_sweep)

    '''
    
    fig, axs = plt.subplots(nrows=2, ncols=1,figsize=(20,20))
    axs = axs.flatten()

    share_of_funds = alpha_sweep['share_of_funds']
    Z = alpha_sweep['share_of_max_conv']
    y = alpha_sweep['alpha']
    ylabel = 'alpha'
    supply = alpha_sweep['supply']

    cp0=axs[0].contourf(share_of_funds, y, Z.T,100, cmap='jet', )
    axs[0].axis([share_of_funds[0], share_of_funds[-1], y[0], y[-1]])
    axs[0].set_ylabel(ylabel)
    axs[0].set_xlabel('Share of Funds Requested')
    axs[0].set_xticks(np.arange(0,.175,.025))
    axs[0].set_title('Trigger Function Map - Alpha sweep; Supply ='+str(supply))
    cb0=plt.colorbar(cp0, ax=axs[0],ticks=np.arange(0,1.1,.1))
    cb0.set_label('share of max conviction to trigger')

    
    share_of_funds = supply_sweep['share_of_funds']
    Z = supply_sweep['share_of_max_conv']
    y = supply_sweep['total_supply']
    ylabel = 'Effective Supply'
    alpha = supply_sweep['alpha']

    cp1=axs[1].contourf(share_of_funds, y, Z.T,100, cmap='jet', )
    axs[1].axis([share_of_funds[0], share_of_funds[-1], y[0], y[-1]])
    axs[1].set_ylabel(ylabel)
    axs[1].set_xlabel('Share of Funds Requested')
    axs[1].set_xticks(np.arange(0,.175,.025))
    axs[1].set_title('Trigger Function Map - Supply sweep; alpha='+str(alpha))
    cb1=plt.colorbar(cp1, ax=axs[1], ticks=np.arange(0,1.1,.1))
    cb1.set_label('share of max conviction to trigger')



def shape_of_trigger_in_absolute_terms(requests, conviction_required,max_request,
                                      max_achievable_request,max_achievable_conviction,
                                      min_required_conviction,log=False):
    '''
    Description:
    Plot to the demonstrate the trigger function shape, 
    showing how the amount of conviction required increases as 
    amount of requested (absolute) funds increases. 
    
    Parameters:
    requests: numpy array of requested funds
    conviction_required: numpy array of conviction required to pass proposals
    max_request: float of max request, which is beta*funds
    max_achievable_request: float of r = (\beta -\sqrt\rho)F
    max_achievable_conviction: float of \frac{S}{1-\alpha}
    min_required_conviction: float of y^*(0) = \frac{\rho S}{(1-\alpha)\beta^2
    log: optional boolean of log y scale
    
    
    '''
    plt.figure(figsize=(10, 7))
    plt.plot(requests, conviction_required)
    ax= plt.gca().axis()
    plt.vlines(max_request, 0, ax[3], 'r', '--')
    plt.vlines(max_achievable_request, 0, ax[3], 'g', '--')
    plt.hlines(max_achievable_conviction, 0, max_request, 'g', '--')
    plt.hlines(min_required_conviction, 0, max_request, 'k', '--')
    
    if log == False:
        plt.title("Sample Trigger Function in Absolute Terms; Linear Scale")
        plt.xlabel("Resources Requested")
        plt.ylabel("Conviction Required to Pass") 
    else:
        plt.title("Sample Trigger Function in Absolute Terms; Log Scale")
    plt.xlabel("Resources Requested")
    plt.ylabel("Conviction Required to Pass")
    plt.gca().set_yscale('log')


def shape_of_trigger_in_relative_terms(requests_as_share_of_funds, conviction_required_as_share_of_max
                                       ,max_request, funds, max_achievable_request,
                                       max_achievable_conviction,
                                       min_required_conviction,log=False):
    '''
    Description:
    Plot to demonstrate the trigger function shape, 
    showing how the amount of conviction required increases as the 
    proportion of requested  funds (relative to total funds) increases.
    
    Parameters:
    requests_as_share_of_funds: numpy array of requests as share of funds
    conviction_required_as_share_of_max: numpy array of conviction required as share of maxto pass proposals
    max_request: float of max request, which is beta*funds
    funds: float of funds
    max_achievable_request: float of r = (\beta -\sqrt\rho)F
    max_achievable_conviction: float of \frac{S}{1-\alpha}
    min_required_conviction: float of y^*(0) = \frac{\rho S}{(1-\alpha)\beta^2
    log: optional boolean of log y scale
    
    
    '''
    plt.figure(figsize=(10, 7))
    plt.plot(requests_as_share_of_funds, conviction_required_as_share_of_max)
    ax= plt.gca().axis()
    plt.vlines(max_request/funds, 0, ax[3], 'r', '--')
    plt.vlines(max_achievable_request/funds, 0, ax[3], 'g', '--')
    plt.hlines(1, 0, max_request/funds, 'g', '--')
    plt.hlines(min_required_conviction/max_achievable_conviction, 0, max_request/funds, 'k', '--')

    
    if log == False:
        plt.title("Sample Trigger Function in Relative Terms; Linear Scale")
        plt.xlabel("Resources Requested as a share of Total Funds")
        plt.ylabel("Conviction Required to Pass as share of max achievable")
        plt.gca().set_ylim(0, 1.1) 
    else:
        plt.title("Sample Trigger Function in Relative Terms; Log Scale")
        plt.xlabel("Resources Requested as a share of Total Funds")
        plt.ylabel("Conviction Required to Pass as share of max achievable")
        plt.gca().set_yscale('log')