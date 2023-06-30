from cmath import pi
from data_processing import day_to_state
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

# shares normalization factor
# 1000 EUR per lot since that is what it is
HMAX_NORMALIZE = 1000
HOLD_LIMIT = 100000
DEBT_LIMIT = 100000
# initial amount of money we have in our account
INITIAL_ACCOUNT_BALANCE = 1000000
# transaction fee: 1/1000 reasonable percentage
TRANSACTION_FEE_PERCENT = 0.001
REWARD_SCALING = 1e-4
print('Enter Forex Environment')

print('Enter Forex Environment')
class ForexEnv():
    """Trading environment"""
    def __init__(self, df=pd.read_csv('forex_data_2000.csv'),day = 2):
        self.day = day
        self.df = df
        self.action_space = [-20, 20]
        # load data from a pandas dataframe
        self.data = self.df.loc[self.day-2: self.day,:] #Passing the data of 3 days for feature extraction and that sort
        self.day_state = day_to_state(self.data)
        self.terminate = False
        self.day_open_rate = self.df.loc[self.day,:][2]            
        # initalize state
        self.state = (self.day_state, 0) #[price_group, holdings]
        # initialize reward
        self.reward = 0
        self.cost = 0
        # memorize all the total balance change
        self.balance = INITIAL_ACCOUNT_BALANCE
        self.asset_memory = [INITIAL_ACCOUNT_BALANCE]
        self.rewards_memory = []
        self.trades = 0
        #self.reset()
    def close_sells(self): #aka buy all sold units
        if 0 <= HOLD_LIMIT and self.balance//self.day_open_rate >= self.state[1]:
            self.balance += self.day_open_rate * self.state[1] * (1 - TRANSACTION_FEE_PERCENT)
            self.cost += self.day_open_rate * self.state[1] * TRANSACTION_FEE_PERCENT
            self.state = (self.state[0], 0)
            self.trades += 1
        return

    def close_buys(self): #aka sell all bought units
        if self.state[1] > DEBT_LIMIT:
            self.balance += self.day_open_rate * self.state[1]
            self.state = (self.state[0], 0)
            self.trades += 1
        return


    def _buy(self, action):
        if self.state[1] + HMAX_NORMALIZE*action <= HOLD_LIMIT and self.balance//self.day_open_rate >= HMAX_NORMALIZE*action:
            self.state = (self.state[0], self.state[1] + HMAX_NORMALIZE*action)
            self.balance -= self.day_open_rate * HMAX_NORMALIZE * action * (1 + TRANSACTION_FEE_PERCENT)
            self.cost += self.day_open_rate * HMAX_NORMALIZE * action * TRANSACTION_FEE_PERCENT
            self.trades+=1
        return
    
    def _sell(self, action):
        if self.state[1] >= DEBT_LIMIT:
            self.state = (self.state[0], self.state[1] + HMAX_NORMALIZE * action)
            self.balance -= self.day_open_rate * HMAX_NORMALIZE * action
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
            return (0, 0), 0 #dummy state

        else:
            action
            #actions = (actions.astype(int))
            
            begin_total_asset = self.asset_memory[-1]
            #print("begin_total_asset:{}".format(begin_total_asset))

            #taking the action
            if action == pi and self.state[1] < 0:
                self.close_sells()
            elif action == -pi and self.state[1] > 0 :
                self.close_buys()
            elif action > pi:
                self._buy(action)
            elif action < -pi:
                self._sell(action)

            self.day += 1
            self.data = self.df.loc[self.day-2: self.day,:] #Passing the data of 3 days for feature extraction and that sort
            self.day_state = day_to_state(self.data)
            self.day_open_rate = self.df.loc[self.day,:][2]        
            self.state =  (self.day_state, self.state[-1])
            
            end_total_asset = self.state[1] * self.day_open_rate + self.balance
            self.asset_memory.append(end_total_asset) 
            self.reward = end_total_asset - begin_total_asset            
            self.rewards_memory.append(self.reward)
            self.reward = self.reward * REWARD_SCALING
            self.action_space = [-20, 20]
            if self.state[1] < 0:
                self.action_space = [-20, pi]
            if self.state[1] > 0:
                self.action_space = [20, -pi]
        return self.state, self.reward

    def reset(self):
        self.day = 2
        # load data from a pandas dataframe
        self.data = self.df.loc[self.day-2: self.day,:] #Passing the data of 3 days for feature extraction and that sort
        self.day_state = day_to_state(self.data)
        self.day_open_rate = self.df.loc[self.day,:][2] 
        self.terminate = False             
        # initalize state
        self.state = (self.day_state, 0)
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