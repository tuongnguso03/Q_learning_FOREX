from environment import ForexEnv
import random
class Model():
    def __init__(self) -> None:
        self.Q_values = dict()
        self.V_values = dict()
    def Q_learning(self, environment: ForexEnv, iterations = 1000, alpha = 0.5, exploration = 0.5, discount = 0.5):
        for _ in range(iterations):
            current_state = environment.reset()
            if current_state not in self.V_values:
                self.V_values[current_state] = 0
            while not environment.terminate:
                action = self.choose_action(environment, exploration)
                next_state, reward = environment.step(action)
                if next_state not in self.V_values:
                    self.V_values[next_state] = 0
                sample = reward + discount*self.V_values[next_state]
                if (current_state, action) not in self.Q_values:
                    self.Q_values[(current_state, action)] = 0
                self.Q_values[(current_state, action)] = self.Q_values[(current_state, action)]*(1-alpha) + sample*alpha
                #updating V-value
                self.V_values[current_state] = max(self.Q_values[(current_state, action)], self.V_values[current_state])
                current_state = next_state
            exploration /= 1.2 #decrease exploration

    
    def choose_action(self, environment: ForexEnv, exploration: float):
        if self.flip_coin(exploration):
            return self._random_move(environment)
        else:
            return self._best_move(environment)
    
    def _random_move(environment: ForexEnv):
        return random.choice(environment.action_space)
    
    def _best_move(self, environment: ForexEnv):
        best_actions = []
        for action in environment.action_space:
            if (environment.state, action) in self.Q_values and self.Q_values[(environment.state, action)] >= self.V_values[(environment.state)]:
                best_actions.append(action)
        if best_actions:
            return random.choice(best_actions)
        return self._random_move(environment)
    
    def flip_coin(p):
        r = random.random()
        return r < p
