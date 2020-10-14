import argparse
import random


class Agent:
    def __init__(self, is_highway, epsilon):
        self.choice_history = []
        self.is_highway = is_highway
        self.expected_costs = {"uu": 0, "dd": 0}
        if self.is_highway:
            self.expected_costs["ud"] = 0
        self.epsilon = epsilon
        self.iterations = 0

    def choose_path(self):
        choice = ""
        if random.uniform(0, 1) <= self.epsilon:
            random_result = random.uniform(0, 1)
            if self.is_highway:
                if random_result < 0.3:
                    choice = "uu"
                elif random_result < 0.6:
                    choice = "ud"
                else:
                    choice = "dd"
            else:
                if random_result < 0.5:
                    choice = "uu"
                else:
                    choice = "dd"
        else:
            if self.expected_costs["uu"] < self.expected_costs["dd"]:
                if self.is_highway:
                    if self.expected_costs["ud"] < self.expected_costs["uu"]:
                        choice = "ud"
                    else:
                        choice = "uu"
                else:
                    choice = "uu"
            else:
                if self.is_highway:
                    if self.expected_costs["ud"] < self.expected_costs["dd"]:
                        choice = "ud"
                    else:
                        choice = "dd"
                else:
                    choice = "dd"

        self.choice_history.append(choice)
        self.iterations += 1

        return choice

    def update_beliefs(self, payoff, choice=None):
        if choice is not None:
            self.expected_costs[choice] = (self.expected_costs[choice] * (self.iterations - 1) + payoff) \
                / self.iterations
        else:
            self.expected_costs["uu"] = (self.expected_costs["uu"] * (self.iterations - 1) + payoff[
                "uu"]) / self.iterations
            self.expected_costs["dd"] = (self.expected_costs["dd"] * (self.iterations - 1) + payoff[
                "dd"]) / self.iterations
            if self.is_highway:
                self.expected_costs["ud"] = (self.expected_costs["ud"] * (self.iterations - 1) + payoff["ud"]) \
                    / self.iterations

        return self.expected_costs


class Game:
    def __init__(self, number_of_agents, is_highway, epsilon, path_costs, max_iterations, complete_information):
        self.agents = []
        for i in range(number_of_agents):
            self.agents.append(Agent(is_highway, epsilon))
        self.iterations = 0
        self.is_highway = is_highway
        self.path_costs = path_costs
        self.max_iterations = max_iterations
        self.payoffs = []
        self.complete_information = complete_information

    def iterate(self):
        round_choices = {"uu": 0, "dd": 0}
        if self.is_highway:
            round_choices["ud"] = 0

        for agent in self.agents:
            agent_choice = agent.choose_path()
            round_choices[agent_choice] += 1

        round_choices["u2"] = round_choices["uu"]
        round_choices["d1"] = round_choices["dd"]
        if self.is_highway:
            round_choices["u1"] = round_choices["uu"] + round_choices["ud"]
            round_choices["d2"] = round_choices["dd"] + round_choices["ud"]
        else:
            round_choices["u1"] = round_choices["uu"]
            round_choices["d2"] = round_choices["dd"]

        round_payoffs = {}
        round_payoffs["uu"] = self.path_costs["u1"] * \
            round_choices["u1"] + self.path_costs["u2"]
        round_payoffs["dd"] = self.path_costs["d1"] + \
            self.path_costs["d2"] * round_choices["d2"]
        if self.is_highway:
            round_payoffs["ud"] = self.path_costs["u1"] * round_choices["u1"] +\
                self.path_costs["d2"] * round_choices["d2"]

        total_payoff = 0
        for agent in self.agents:
            previous_choice = agent.choice_history[-1]

            agent_payoff = round_payoffs[previous_choice]
            total_payoff += agent_payoff

            if self.complete_information:
                agent.update_beliefs(round_payoffs)
            else:
                agent.update_beliefs(agent_payoff, previous_choice)

        self.payoffs.append(total_payoff)
        self.iterations += 1

    def play_game(self):
        while self.iterations < self.max_iterations:
            self.iterate()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the congestion game with the given parameters")
    parser.add_argument("num_agents", type=int,
                        help="Number of agents to run the congestion game with")
    parser.add_argument("is_highway", type=bool,
                        help="Whether or not to include the super highway")
    parser.add_argument("epsilon", type=float, help="Value to make epsilon")
    parser.add_argument("max_iterations", type=int,
                        help="Max number of iterations for the game")
    parser.add_argument("complete_info", type=bool,
                        help="Whether or not agents have perfect information")

    return parser.parse_args()


def main():
    args = parse_args()

    path_costs = {"u1": 1/100, "u2": 25, "d1": 25, "d2": 1/100}

    best_choice = {"uu": 0, "ud": 0, "dd": 0}
    total = 0
    games = []
    for i in range(10):
        games.append(Game(args.num_agents, args.is_highway, args.epsilon,
                          path_costs, args.max_iterations, args.complete_info))
        games[i].play_game()
        for agent in games[i].agents:
            best_choice[min(agent.expected_costs,
                            key=agent.expected_costs.get)] += 1
            total += 1

    for key, value in best_choice.items():
        to_print = key + ": " + str(value / total)
        print(to_print)


if __name__ == "__main__":
    main()
