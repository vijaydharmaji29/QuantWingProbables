from scipy import stats
from numpy import log, exp, sqrt

class OptionPricing:

    def __init__(self, S, E, T, rf, sigma):
        self.S = S
        self.E = E
        self.T = T
        self.rf = rf
        self.sigma = sigma

    def call_option_price(self):
        # calculating d1, d2
        d1 = (log(self.S / self.E) + (self.rf + self.sigma * self.sigma / 2.0) * self.T) / (self.sigma * sqrt(self.T))
        d2 = d1 - self.sigma * sqrt(self.T)
        #calculating price of the option
        return self.S*stats.norm.cdf(d1)-E*exp(-self.rf*self.T)*stats.norm.cdf(d2)


    def put_option_price(self):
        # calculating d1, d2
        d1 = (log(self.S / self.E) + (self.rf + self.sigma * self.sigma / 2.0) * self.T) / (self.sigma * sqrt(self.T))
        d2 = d1 - self.sigma * sqrt(self.T)
        #calculating price of the option
        return -self.S*stats.norm.cdf(-d1)+E*exp(-self.rf*self.T)*stats.norm.cdf(-d2)


if __name__ == '__main__':
    S0 = 100 # underlying stock price at t=0
    E = 100 # strike price
    T = 1 # expiry 1year=365days
    rf = 0.05 # risk-free rate
    sigma = 0.2 # volatility of the underlying stock

    model = OptionPricing(S0, E, T, rf, sigma)

    print("Call option price according to Black-Scholes model: ", model.call_option_price())
    print("Put option price according to Black-Scholes model: ", model.put_option_price())

