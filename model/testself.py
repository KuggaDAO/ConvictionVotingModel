from run import *
from parts.utils import *
import matplotlib.pyplot as plt
import time
from parts.metrics import *

# run the model and gain the data
'''
df = run()
df = postprocessing(df, sim_ind=-1)
df.to_pickle('conviction-voting-cadcad/models/v3/model/testdf.pkl')
'''

# read the data
df = pd.read_pickle('conviction-voting-cadcad/models/v3/model/testdf.pkl')

nets = df.network.values
length = len(nets)

part = get_nodes_by_type(nets[-1], 'participant')
prop = get_nodes_by_type(nets[-1], 'proposal')
print('number of participants: ',len(part))
print('number of proposals: ',len(prop))

'''
# sentiment
sentiment = []
for i, s in df.iterrows():
    sentiment.append(s['sentiment'])
plt.plot(np.arange(0,length),sentiment, 'o-')
plt.title('sentiment')
plt.show()


# snap of the networks
snap_plot(nets,dims = (9,6),savefigs = True)
'''

# affinities of the networks
affinities_plot(nets[-1],dims = (9,4))
plt.show()

# metrics
fig= plt.subplots(figsize=(8, 8))
ax1 = plt.subplot(221)
ax2 = plt.subplot(222)
ax3 = plt.subplot(223)
ax4 = plt.subplot(224)
fractionOfSupplyForVoting = []
fractionOfSupplyInPool = []
percentageOfActiveProposals = []    
percentageOfCompletedProposals = []
percentageOfKilledProposals = []
percentageOfActiveFundsRequested = []
percentageOfCompletedFundsRequested = []
percentageOfKilledFundsRequested = []
for i, s in df.iterrows():
    dict = kpi_calculations(params=None, step=None, sL=None, s=s)
    fractionOfSupplyForVoting.append(dict['fractionOfSupplyForVoting'])
    fractionOfSupplyInPool.append(dict['fractionOfSupplyInPool'])
    percentageOfActiveProposals.append(dict['fractionOfProposalStages']['percentageOfActive'])
    percentageOfCompletedProposals.append(dict['fractionOfProposalStages']['percentageOfCompleted'])
    percentageOfKilledProposals.append(dict['fractionOfProposalStages']['percentageOfKilled'])
    percentageOfActiveFundsRequested.append(dict['fractionOfFundStages']['percentageOfActiveFundsRequested'])
    percentageOfCompletedFundsRequested.append(dict['fractionOfFundStages']['percentageOfCompletedFundsRequested'])
    percentageOfKilledFundsRequested.append(dict['fractionOfFundStages']['percentageOfKilledFundsRequested'])
l = len(fractionOfSupplyForVoting)
ax1.plot(np.arange(0,l),fractionOfSupplyForVoting, 'o-')
ax2.plot(np.arange(0,l),fractionOfSupplyInPool, 'o-')
ax3.plot(np.arange(0,l),percentageOfActiveProposals, '*-',color = 'orange',label = 'Active')
ax3.plot(np.arange(0,l),percentageOfCompletedProposals, '*-',color = 'green',label = 'Completed')
ax3.plot(np.arange(0,l),percentageOfKilledProposals, '*-',color = 'black',label = 'Killed')
ax4.plot(np.arange(0,l),percentageOfActiveFundsRequested, '+-',color = 'orange',label = 'Active')
ax4.plot(np.arange(0,l),percentageOfCompletedFundsRequested, '+-',color = 'green',label = 'Completed')
ax4.plot(np.arange(0,l),percentageOfKilledFundsRequested, '+-',color = 'black',label = 'Killed')
ax1.set_title('fractionOfSupplyForVoting')
ax2.set_title('fractionOfSupplyInPool')
ax3.set_title('fractionOfProposalNumbersStages')
ax4.set_title('fractionOfFundRequestedStages')
ax3.legend()
ax4.legend()
plt.tight_layout()
plt.show()