#Yahoo Parser with RSI analyzer
Yahoo Parser and 'Relative Strength Index'(RSI) analyzer allow users to identify
overbought and oversold assets among all stocks on NYSE.

##RSI:
>Simply put, relative strength tells you how fast a company’s share price moving
>upward. We compare the past N months performance of a stock to the entire market.
>If, over the past N months, a stock has outperformed M% of all other stocks on the
>market, then it passes the relative strength test.

Main feature is the ability to identify 'hard gainers' not just in stock prices, but also in different financial parameters such as 'Total Revenue', 'Total Cashflow' and others provided by Yahoo Finance.



>The relative strength index is calculated using the following formula:
>RSI = 100 - 100 / (1 + RS)

>Where RS = Average gain of up periods during the specified time frame / Average loss of down periods during the specified time frame/

>The RSI provides a relative evaluation of the strength of a security's recent price performance, thus making it a momentum indicator. RSI values range from 0 to 100. The default time frame for comparing up periods to down periods is 14, as in 14 trading days.

## Requirements:
python3 >= 3.3
python3-pip
beautifulsoup4
