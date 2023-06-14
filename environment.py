from data_processing import get_price_group
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

# shares normalization factor
# 1000 EUR per lot since that is what it is
HMAX_NORMALIZE = 1000
HOLD_LIMIT = 10000
# initial amount of money we have in our account
INITIAL_ACCOUNT_BALANCE=1000000
# transaction fee: 1/1000 reasonable percentage
TRANSACTION_FEE_PERCENT = 0.001
REWARD_SCALING = 1e-4
print('Enter Forex Environment')

print('Enter Forex Environment')
class ForexEnv():
    """Trading environment"""
    def __init__(self, df,day = 0):
        self.day = day
        self.df = df
        self.action_space = [-1, 0 , 1]
        # load data from a pandas dataframe
        self.data = self.df.loc[self.day,:] #data should be array, with data[2] being the open price. Screw me over.
        self.price_group = get_price_group(self.data[1])
        self.terminate = False             
        # initalize state
        self.state = (self.price_group, 0) #[price_group, holdings]
        # initialize reward
        self.reward = 0
        self.cost = 0
        # memorize all the total balance change
        self.balance = INITIAL_ACCOUNT_BALANCE
        self.asset_memory = [INITIAL_ACCOUNT_BALANCE]
        self.rewards_memory = []
        self.trades = 0
        #self.reset()

    def _buy(self, action):
        if self.state[1] + HMAX_NORMALIZE*action <= HOLD_LIMIT and self.balance//self.data[2] >= HMAX_NORMALIZE*action:
            self.state = (self.state[0], self.state[1] + HMAX_NORMALIZE*action)
            self.balance -= self.data[2]*HMAX_NORMALIZE*action*(1+TRANSACTION_FEE_PERCENT)
            self.cost += self.data[2]*HMAX_NORMALIZE*action*TRANSACTION_FEE_PERCENT
            self.trades+=1
        return
    
    def _sell(self, action):
        if self.state[1] > 0:
            self.state = (self.state[0], self.state[1] + HMAX_NORMALIZE*action)
            self.balance -= self.data[2]*HMAX_NORMALIZE*action*(1-TRANSACTION_FEE_PERCENT)
            self.cost -= self.data[2]*HMAX_NORMALIZE*action*TRANSACTION_FEE_PERCENT
            self.trades+=1
        return
    
    def step(self, action):
        """Performing a step
        Parameters
        ----------
        action : int
            -1 to sell, 0 to hold, 1 to buy. This is to easily fit the Q-value.
           Later on, the value may fluctuate, allowing for more flexibility 
        Returns
        -------
        self.state: list
            the state of the environment after the step
        self.reward: int
            the reward of the step
        """
        # print("Day ",self.day)
        self.terminate = (self.day >= len(self.df.index.unique())-1) #If day > len, then terminate = true

        if self.terminate:
            plt.plot(self.asset_memory,'r')
            plt.savefig('account_value_train.png')
            plt.close()
            end_total_asset = self.asset_memory[-1]
            
            print("end_total_asset:{}".format(end_total_asset))
            df_total_value = pd.DataFrame(self.asset_memory)
            df_total_value.to_csv('account_value_train.csv')
            df_total_value.columns = ['account_value']
            df_total_value['daily_return']=df_total_value.pct_change(1)
            #sharpe = (252**0.5)*df_total_value['daily_return'].mean()/df_total_value['daily_return'].std()
            #print("Sharpe: ",sharpe)
            #print("=================================")
            #df_rewards = pd.DataFrame(self.rewards_memory)
            return (0, 0), 0 #dummy state

        else:
            action
            #actions = (actions.astype(int))
            
            begin_total_asset = self.asset_memory[-1]
            #print("begin_total_asset:{}".format(begin_total_asset))

            #taking the action
            if action > 0 :
                self._buy(action)
            elif action < 0:
                self._sell(action)

            self.day += 1
            self.data = self.df.loc[self.day,:]
            self.price_group = get_price_group(self.data[2])         
            #load next state
            # print("stock_shares:{}".format(self.state[29:]))
            self.state =  (self.price_group, self.state[1])
            
            end_total_asset = self.state[1]*self.data[2] + self.balance
            self.asset_memory.append(end_total_asset)
            #print("end_total_asset:{}".format(end_total_asset))
            
            self.reward = end_total_asset - begin_total_asset            
            # print("step_reward:{}".format(self.reward))
            self.rewards_memory.append(self.reward)
            self.reward = self.reward*REWARD_SCALING
        return self.state, self.reward

    def reset(self):
        self.day = 0
        # load data from a pandas dataframe
        self.data = self.df.loc[self.day,:]
        self.price_group = get_price_group(self.data[2])
        self.terminate = False             
        # initalize state
        self.state = (self.price_group, 0)
        # initialize reward
        self.reward = 0
        self.cost = 0
        # memorize all the total balance change
        self.balance = INITIAL_ACCOUNT_BALANCE
        self.asset_memory = [INITIAL_ACCOUNT_BALANCE]
        self.rewards_memory = []
        self.trades = 0 
        return self.state
    
    def render(self):
        return self.state