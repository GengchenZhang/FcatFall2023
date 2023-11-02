# FcatFall2023
Brandeis FcatFall2023

query for price

PREFIX ns1: <http://www.semanticweb.org/sichengyun/ontologies/2023/6/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?date ?price
WHERE {
    ?btc ns1:BTC_date ?date ;
         ns1:BTC_price ?price .
    FILTER (?date >= "2022-12-02"^^xsd:date && ?date <= "2023-05-01"^^xsd:date)
}
ORDER BY ?date



# Attempt to fetch the prices
prices_results = list(g.triples((None, rdflib.term.URIRef('http://www.semanticweb.org/sichengyun/ontologies/2023/6/BTC_date'), None)))

from datetime import datetime

# Correcting the error and filtering the results for the desired date range
filtered_prices = sorted([(str(date_obj), float(price_obj.toPython())) for subj, _, date_obj in prices_results for _, _, price_obj in g.triples((subj, rdflib.term.URIRef('http://www.semanticweb.org/sichengyun/ontologies/2023/6/BTC_price'), None)) if date_obj >= rdflib.term.Literal("2022-12-02", datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#date')) and date_obj <= rdflib.term.Literal("2023-05-01", datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#date'))])

filtered_prices[:5]  # Display the first 5 prices for review
import matplotlib.pyplot as plt
import pandas as pd

# Convert the filtered prices into a DataFrame
df = pd.DataFrame(filtered_prices, columns=['Date', 'Price'])
df['Date'] = pd.to_datetime(df['Date'])

# Compute the daily returns
df['Daily Return'] = df['Price'].pct_change()

# Calculate the rolling 30-day volatility
df['Volatility'] = df['Daily Return'].rolling(window=30).std()

# Plotting the volatility
plt.figure(figsize=(14, 7))
plt.plot(df['Date'], df['Volatility'], label='30-day Rolling Volatility', color='blue')
plt.title('Bitcoin 30-day Rolling Volatility (Feb 1, 2023 - May 1, 2023)')
plt.xlabel('Date')
plt.ylabel('Volatility')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
