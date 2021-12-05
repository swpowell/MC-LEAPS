<b>Monte Carlo LEAP Call Viewer</b>

This code was designed and tested for use in the command line. No warranty is provided for the code. It has only been tested on Mac and LINUX operating systems.

In the terminal, to run the code enter

>> python MCLEAPmodel.py

The code will prompt you to enter a ticker symbol (the requested ticker) or to enter q to quit. If you enter a ticker symbol, information will be pulled from Yahoo! Finance to predict the future price (expected value) of the requested ticker at various LEAP expiration dates. Expected value is computed as the mean of 1000 Monte Carlo simulations of future price for the ticker, which is based on performance of the requested ticker over the past 5 years by default (although advanced users can change the time interval considered by altering a line in the function main().) 

After a user requests information for a ticker, code will print to the terminal all available calls at out-of-the-money strike prices for the requested ticker at least 365 days into the future. The last column of the printed output contains the expected "multiplier", or the mean multiple gain expected from the 1000 Monte Carlo simulations. For example, if the purchase price of an option is $10, and the expected value of the option at LEAP expiration is $20, the final column will print 2.00.

Current option price is estimated as the current ASK price.

A conda python environment is included in MCLEAPS.yml. It contains the requisite packages to run the code. If you have anaconda installed, you may install this environment.

The minimum dependencies are the following (install these manually if you cannot install the environment provided):
- yfinance (pip install yfinance)
- numpy 
- pandas
- termcolor (pip install termcolor)
