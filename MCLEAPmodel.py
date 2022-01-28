"""

******* THIS OPEN-SOURCE, UNWARRANTIED CODE IS COVERED BY A GNU GENERAL PUBLIC LICENSE. *******

LEAP finder.
Version: 0.2
Date: 7 April 2021
Updated: 4 December 2021
Author: Scott W. Powell (powellscottw@gmail.com)

Purpose: Find long-dated call options with high realistic potential return on investment based 
on growth assumptions consistent with growth over specified historical time period.
By default, the historical time period is 5 years. Users can change this by modifying the "years"
variable in the main() function located at the bottom of this code.
"Long-dated" is considered any call option with an expiration date at least 1 year from current date.

Data access based on yfinance module by Ran Aroussi (pypi.org/project/yfinance)

"""

import sys

#******************************************************

def findLEAPs(stock):

	from datetime import datetime as dt
	from numpy import array

	# Get tuple of options expiration dates.
	dates = array(stock.options)

	# Get number of days out for each option.
	deltas = [(dt.strptime(i,'%Y-%m-%d').date()-dt.today().date()).days for i in dates]
	 
	return dates[array(deltas)>365]	

#******************************************************

def getoptionsprices(stock,dates):

	from pandas import DataFrame
	from datetime import datetime as dt, timedelta as td
	import numpy as np

	# Initialize a dictionary that will hold one pandas data frame per expiration date.
	options = {}

	# Get the last stock bid price (includes AH trading).
	price = stock.info['regularMarketPrice']	
	print('Current price: $' + str(price))
	
	for i in dates:
	
		# Initialize a pandas data frame.
		data = DataFrame()

		# Load the option chain.
		chain = stock.option_chain(i)		

		# Get the last purchase dates for each strike (calls only).
		purchase = chain.calls.lastTradeDate
	
		# Get the last purchase dates. We'll exclude anything over 60 days old because it is probably too far OTM or ITM to bother with anyway.
		dts = [dt.strptime(str(i),'%Y-%m-%d %H:%M:%S') for i in purchase]
		deltas = np.array([(dt.today().date()-i.date()).days for i in dts])

		# Exclude all ITM calls as well since we generally won't use them for investing in LEAPs.
		# Could also use inTheMoney column.
		strikes = chain.calls.strike		

		# Include data with strike above price and last purchase date within last 60 days.
		cond = (strikes > price) & (deltas <= 60)		

		# Next, get information.
		# Strike price.
		data['Strike Price'] = chain.calls.strike[cond]		
		# Bid price.
		data['Bid Price'] = chain.calls.bid[cond]
		# Ask price.
		data['Ask Price'] = chain.calls.ask[cond]
		# Volume.
		data['Daily Volume'] = chain.calls.volume[cond]

		# Add data frame to the parent dictionary. Reset the indexing.
		options[i] = data.reset_index(drop=True)

	return options

#******************************************************

def simulateMC(stock,years):

	# Conduct 1000 simulations of potential future price of stock using 
	# last 5 years of growth as a predictor for future growth.
	# Predictions will extend to two years beyond the current date.

	import numpy as np
	from pandas import DataFrame
	from datetime import datetime as dt, timedelta as td
	from termcolor import colored

	numsims = 1000	# Controls number of simulations. This can be changed by advanced users.

	# Get weekly history for last 5 years. Exclude this week since it may be unfinished.
	period = {1:"1y",2:"2y",5:"5y"}
	history = stock.history(period=period[years],interval="1wk")[:-1]	
	if len(history) < np.ceil(years*52.17):
		print( colored('Warning','red') + ': Less than ' + str(years)  + ' year(s) of data exists for this stock!') 

	# Remove dividend rows.
	history = history[history.Dividends==0]

	# Compute percent change per week.
	#pct = (history['Close']-history['Open'])/history['Open']
	pct = [(history['Close'][i]-history['Close'][i-1]) / \
		history['Close'][i-1] \
		for i in np.arange(1,len(history))]
	pct = np.array(pct)
	pct = pct[~np.isnan(pct)]

	# For now, assume that gains and losses are normally distributed about the mean.
	mean, stdev = 1+np.mean(pct), np.std(pct)

	# Get the last stock bid price (includes AH trading).	
	price = stock.info['regularMarketPrice']

	# Embedded Monte Carlo function.
	def montecarlo(numsims,weeks):
		from numpy.random import default_rng
		rng = default_rng()
		dummy = np.zeros([numsims,weeks])
		for i in range(numsims):
			dummy[i,0] = price
			for j in np.arange(1,weeks):
				dummy[i,j] = dummy[i,j-1]*(rng.normal(loc=mean,scale=stdev,size=1))
				# dummy[i,j] = dummy[i,j-1]*(np.random.normal(loc=mean,scale=stdev))
		return dummy

	# Let's name the columns based on date instead of number of weeks. This will help later when 
	# we are looking up appropriate column for determining expected values of various dated options.
	columnnames = [dt.strftime(dt.today().date()+td(i*7),"%Y-%m-%d") for i in range(125)]	
	
	# Make a prediction data frame. Simulate out 125 weeks (2 years)..
	return DataFrame(montecarlo(numsims,125),columns=columnnames)

#******************************************************

def multiplier(options,prediction):

	import numpy as np
	from datetime import datetime as dt

	# Loop through each option.
	for i in list(options.keys()):
		optiondate = dt.strptime(i,'%Y-%m-%d').date()		
	
		# Find the date in the prediction data frame that most closely matches optiondate.
		predictiondates = (np.array([dt.strptime(i,'%Y-%m-%d').date() for i in prediction.columns]))
		I = np.argmin(np.abs(optiondate-predictiondates))

		# Convert prediction date back to string and get various simulated outcomes.
		outcomes = prediction[dt.strftime(predictiondates[I],"%Y-%m-%d")]

		# Compute expected value.
		ev = np.round(np.median(outcomes),2)

		# Add column to dataframe for each option.
		options[i]['Implied Expiration Value'] = np.maximum(0,ev-options[i]['Strike Price'])
		options[i]['Implied Factoral Gain'] = np.round(options[i]['Implied Expiration Value']/options[i]['Ask Price'],2)

	return options

#******************************************************

def liststock(ticker,years):

	import yfinance as yf

	try:
		# Create object for ticker.
		stock = yf.Ticker(ticker)

		# Get the dates of LEAPs for the stock ticker.
		dates = findLEAPs(stock)
		
		# Get the latest bid/ask/strike prices and recent volume on each LEAP.
		# Will only show strike prices with purchase in last 60 days.
		# (This helps avoid analysis of illiquid options.))
		options = getoptionsprices(stock,dates)

		# Next, simulate the future price of each stock using Monte Carlo approach based on historical data.
		prediction = simulateMC(stock,years)	
	
		# Finally, compute expected value for the various options and add to options tables.	
		options = multiplier(options,prediction)		

		return options

	except:
		#sys.exit('Invalid ticker name entered.')
		return None	
	
#******************************************************

def prettyprint(options,ticker):

	# Print out the pandas dataframes in a user-readable format. 
	# (This would look way nicer in Jupyter Notebook, but will just format for CLI for now.)

	for i in options:
		print('\nLEAP call option information for ' + str.upper(ticker) + ' for ' + i)
		print(options[i].to_string(index=False))
	

#******************************************************

def quit():

	sys.exit('Exiting at user request.')

#******************************************************

# def complete():

# 	sys.exit('App completed and is exiting.')

#******************************************************

def prompt():
	
	# Get user input for ticker or ask to quit.

	print('\nEnter ticker for stock to get LEAPS information for it, or enter q to exit.')
	val = input()

	if val == 'q':
		quit()
	else:
		return val

#******************************************************

def run(ticker,years):

	# Get pandas tables of LEAP information, including potential growth.
	print('\nGetting options information and making predictions...')
	options = liststock(ticker,years)

	if options is None:
		print('\nSomething went wrong. Perhaps an invalid ticker was entered. \
			If the error repeatedly occurs, there may be a problem with the Yahoo \
			Finance API and you may need to wait and try again later.')
	else:
		prettyprint(options,ticker)
		# complete()

#******************************************************

def main():
	
	# Number of years of historical data used to make predictions. 
	# Needs to be 1, 2, 5, or 10 to play well with yfinance module.
	# Could make this user-inputted variable if desired but chose
	# to minimize user input in the CLI and leave this for advanced users.
	years = 5

	while True:
		ticker = prompt()
		run(ticker,years)

#******************************************************

if __name__ == '__main__':
	main()
