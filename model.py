from environment import ForexEnv
from collections import defaultdict
import pickle
import random
import pandas as pd
class Model():
    def __init__(self, load = None) -> None:
        self.Q = []
        if load != None:
            with open(load, 'rb') as handle:
                self.Q_values = defaultdict(lambda: 0, pickle.load(handle))
        else:
            self.Q_values = defaultdict(lambda: 0, {})
    def Q_learning(self, environment: ForexEnv, iterations = 1000, alpha = 0.5, exploration = 0.5, discount = 0.5, debug = False):
        for _ in range(iterations):
            print("Iteration ", _)
            current_state = environment.reset()
            while True:
                action = self.choose_action(environment, exploration=exploration, debug=debug)
                next_state, reward = environment.step(action)
                if environment.terminate: #have to check right after the step
                    break
                v_value = max([self.Q_values[(next_state, actionx)] for actionx in environment.action_space])
                sample = reward + discount * v_value
                if (current_state, action) not in self.Q_values:
                    self.Q_values[(current_state, action)] = 0
                self.Q_values[(current_state, action)] = self.Q_values[(current_state, action)]*(1-alpha) + sample * alpha
                current_state = next_state
            if debug == False:
                q_data = pd.DataFrame(self.Q)
                q_data.to_csv('a.csv', mode='a', index=False, header=False)
            exploration /= 1.02
            # change from 1.02
            #decrease exploration

    
    def choose_action(self, environment: ForexEnv, exploration: float, debug = False):
        if self.flip_coin(exploration):
            return self._random_move(environment)
        else:
            return self._best_move(environment, debug)
    
    def _random_move(self, environment: ForexEnv):
        return random.choice(environment.action_space)
    
    def _best_move(self, environment: ForexEnv, debug = False):
        best_value = -999
        best_actions = []
        for action in environment.action_space:
            if (environment.state, action) in self.Q_values: 
                if self.Q_values[(environment.state, action)] == best_value:
                    best_actions.append(action)
                elif self.Q_values[(environment.state, action)] > best_value:
                    best_actions = [action]
                    best_value = self.Q_values[(environment.state, action)]
        if best_actions:
            if debug:
                self.Q.append([self.Q_values[(environment.state, i)] for i in best_actions])
            return random.choice(best_actions)
        return self._random_move(environment)
    
    def flip_coin(self, p: float):
        r = random.random()
        return r < p
