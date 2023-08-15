# v3文件

## 注意configs相关的都比较乱，要改成exp.configs

**./model/parts/sys_params:** 模型的初值和参数——
除去熟知的beta,rho,alpha，还有
- gamma: expansion of supply per per day
sensitivity
- tmin: unit days; minimum periods passed before a proposal can pass
- min_supp: number of tokens that must be stake for a proposal to be a candidate
- base_completion_rate: expected number of days to complete a proposals.
- base_failure_rate: expected number of days until a proposal will fail
- **base_engagement_rate**: Probability of being active on a certain day if 100% sentiment 
- lowest_affinity_to_support: lowest affinity to required to support a proposal

**./model/partial_state_update_block:** 状态更新模块
-  system.py: driving_process(network&supply),minting_rule
-  participants.py: check_progress(sentiment, network)
-  proposals.py: trigger_function(funds, sentiment, network)
-  participants.py: participants_decisions(token)
-  metrics.py: kpi_calculations

**./model/parts/utils.py:** 
- trigger_threshold
- initial_social_network
  [influence_rv = expon.rvs(loc=0.0, scale=scale)
  if influence_rv > scale+sigmas*scale**2:]影响力服从指数分布
- initial_conflict_network
  [conflict_rv = np.random.rand()
   if conflict_rv < rate :
   network.edges[(i,j)]['conflict'] = 1-conflict_rv]矛盾值服从均匀分布
- gen_new_participant
- gen_new_proposal
- get_nodes_by_type
- get_sentimental(Function to update sentiment)
- get_edges_by_type
- conviction_order
- **social_links**(Function to add influence edges to network)
  [influence_rv = expon.rvs(loc=0.0, scale=scale)]
- **conflict_links**(Function to add conflict edges to network)
  [conflict_rv = np.random.rand()]
- **social_affinity_booster**(Function to create aggregate influence for participant)影响者影响力和token等表象对于参与者affinity的聚合
  [np.sum(tokens * influence)/(influence_sum * i_tokens)]
- pad拉长向量
- make2D
- **initialize_network**
  [h_rv = expon.rvs(loc=0.0, scale= supply/n)]成员资产的分布
  [s_rv = np.random.rand()]成员sentiment的分布
  [r_rv = gamma.rvs(3,loc=0.001, scale=(initial_funds * params['beta'])*.05)]提案request的分布
  [a_rv = np.random.uniform(-1,1,1)[0]]成员对于提案affinity的分布
- config_initialization
- schema_check
- **trigger_sweep**(Function to plot trigger function under parameter sweep)扫参数(effective_supply,alpha)
**plotting**
- snap_plot(return Bipartite graph of participants and proposals at a specific timestep)默认是最近的一个
  [plt.savefig('images/snap/'+str(counter)+'.png',bbox_inches='tight')]
- affinities_plot(plot of affinities between participants and proposals)heat map
- trigger_grid(扫参数结果)
- shape_of_trigger_in_absolute_terms(showing how the amount of conviction required increases as amount of requested (absolute) funds increases. )
- shape_of_trigger_in_relative_terms(showing how the amount of conviction required increases as the proportion of requested  funds (relative to total funds) increases.)

**./model/parts/system:**
- **driving_process**:
    Driving process for adding new participants (their funds) and new proposals.
    return({'new_participant':new_participant, #True/False
            'new_participant_holdings':new_participant_holdings, #funds held by new participant if True
            'new_proposal':new_proposal, #True/False
            'new_proposal_ct': new_proposal_ct, #int
            'new_proposal_requested':new_proposal_requested, #list funds requested by new proposal if True, len =ct
            }) 
- 