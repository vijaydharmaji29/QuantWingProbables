import numpy as np
import math
import time


class OptionPricing:

    def __init__(self, S0, E, T, rf, sigma, iterations):
        self.S0 = S0
        self.E = E
        self.T = T
        self.rf = rf
        self.sigma = sigma
        self.iterations = iterations

    def call_option_simulation(self):

        option_data = np.zeros([self.iterations, 2])
        rand = np.random.normal(0, 1, [1, self.iterations])
        stock_price = self.S0 * np.exp(self.T * (self.rf - 0.5 * self.sigma ** 2) + self.sigma * np.sqrt(self.T) * rand)
        option_data[:, 1] = stock_price - self.E


        average = np.sum(np.amax(option_data, axis=1)) / float(self.iterations)

        return np.exp(-1.0 * self.rf * self.T) * average

    def put_option_simulation(self):

        option_data = np.zeros([self.iterations, 2])
        rand = np.random.normal(0, 1, [1, self.iterations])

        stock_price = self.S0 * np.exp(self.T * (self.rf - 0.5 * self.sigma ** 2) + self.sigma * np.sqrt(self.T) * rand)

        option_data[:, 1] = self.E - stock_price

        average = np.sum(np.amax(option_data, axis=1)) / float(self.iterations)

        return np.exp(-1.0 * self.rf * self.T) * average


if __name__ == "__main__":
    S0 = 100  # underlying stock price at t=0
    E = 100  # strike price
    T = 1  # expiry
    rf = 0.05  # risk-free rate
    sigma = 0.2  # volatility of the underlying stock
    iterations = 1000000  # number of iterations in the Monte-Carlo simulation

    model = OptionPricing(S0, E, T, rf, sigma, iterations)
    print("Call option price with Monte-Carlo approach: ", model.call_option_simulation())
    print("Put option price with Monte-Carlo approach: ", model.put_option_simulation())
