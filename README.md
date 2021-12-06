<b>Monte Carlo LEAP Call Viewer</b>

This code was designed and tested for use in the command line. No warranty is provided for the code. It has only been tested on Mac and LINUX operating systems.

In the terminal, to run the code enter

> python MCLEAPmodel.py

The code will prompt you to enter a ticker symbol (the requested ticker) or to enter q to quit. If you enter a ticker symbol, information will be pulled from Yahoo! Finance to predict the future price (expected value) of the requested ticker at various LEAP expiration dates. Expected value is computed as the mean of 1000 Monte Carlo simulations of future price for the ticker, which is based on performance of the requested ticker over the past 5 years by default (although advanced users can change the time interval considered by altering a line in the function main().) 

After a user requests information for a ticker, code will print to the terminal all available calls at out-of-the-money strike prices for the requested ticker at least 365 days into the future. The last column of the printed output contains the expected "multiplier", or the mean multiple gain expected from the 1000 Monte Carlo simulations. For example, if the purchase price of an option is $10, and the expected value of the option at LEAP expiration is $20, the final column will print 2.00.

Current option price is estimated as the current ASK price.

A conda python environment is included in MCLEAPS.yml. It contains the requisite packages to run the code. If you have anaconda installed, you may install this environment.

The minimum dependencies are the following (install these manually or using the Python environment manager of your choice if you cannot install the environment provided):
- yfinance 
- numpy 
- pandas 
- termcolor

<i>Starting from scratch</i>

This software runs from the terminal only. For it to operate, you first need a Python installation. You can test this by opening the terminal and entering (capital V)

> python -V 

If you get a version number, then you have Python installed. If not, install Python from here: https://www.python.org/downloads/. 

After you verify Python installation, you need to install software dependencies to run the script. If you do not need or want to make a special Python environment (see below), you can use pip to install the required packages by the following: 

> pip install yfinance pandas numpy termcolor 

If you wish to do so, Google "creating a Python virtual environment" to learn more about what a virtual environment is and how to create a Python environment. This will be useful if you intend to use Python more in the future. Alternatively, you could install a Python distribution like Anaconda that comes with a package manager like conda.

<i>Downloading the code</i>

The preferred way to download the code is to navigate to a directory on your machine in the terminal and use the following command to grab the code:

> git clone https://github.com/swpowell/MC-LEAPS.git

If this doesn't work, you probably need to install git. You can find details on how to do so here: https://github.com/git-guides/install-git
