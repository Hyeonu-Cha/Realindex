import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load CSV files
id_map = pd.read_csv("IDMap.csv")
portfolio_holdings = pd.read_csv("PortfolioHoldings.csv")
benchmark_holdings = pd.read_csv("BenchmarkHoldings.csv")
carbon_data = pd.read_csv("CarbonData.csv")

# Merging files
portfolio_df = portfolio_holdings.merge(id_map, left_on='Ticker', right_on='ticker', how='left').merge(carbon_data, left_on='sedol', right_on='SEDOL', how='left')
benchmark_df = benchmark_holdings.merge(id_map, on='ticker', how='left').merge(carbon_data, left_on='sedol', right_on='SEDOL', how='left')

# Handle Mismatched value
# Drop rows with NaN values
benchmark_df.dropna(subset=['EMISSIONS_SCOPE_1', 'EMISSIONS_SCOPE_2', 'REVENUE_USD'], inplace=True)
portfolio_df.dropna(subset=['EMISSIONS_SCOPE_1', 'EMISSIONS_SCOPE_2', 'REVENUE_USD'], inplace=True)

#revenue to Millon
portfolio_df['REVENUE_USD'] = portfolio_df['REVENUE_USD'] / 1e6
benchmark_df['REVENUE_USD'] = benchmark_df['REVENUE_USD'] / 1e6


# Calculate Weights for Portfolio
TotalMarketCap = portfolio_df['Units'] * portfolio_df['Price'].sum()
portfolio_df['Weight'] = portfolio_df['Units'] * portfolio_df['Price'] / TotalMarketCap 

# Calculate WACI for Portfolio and Benchmark
portfolio_df['WACI'] = portfolio_df['Weight'] * (portfolio_df['EMISSIONS_SCOPE_1'] + portfolio_df['EMISSIONS_SCOPE_2']) / portfolio_df['REVENUE_USD']
benchmark_df['WACI'] = benchmark_df['IndexWeight'] * (benchmark_df['EMISSIONS_SCOPE_1'] + benchmark_df['EMISSIONS_SCOPE_2']) / benchmark_df['REVENUE_USD']

portfolio_WACI = portfolio_df['WACI'].sum()
benchmark_WACI = benchmark_df['WACI'].sum()


# Output the results
print(f"\nPortfolio WACI: {portfolio_WACI:.2f}")
print(f"Benchmark WACI: {benchmark_WACI:.2f}")

# Group by CategoryGroup and sum up WACI
portfolio_grouped = portfolio_df.groupby('CategoryGroup')['WACI'].sum()
benchmark_grouped = benchmark_df.groupby('CategoryGroup')['WACI'].sum()


print("\nCategory Group Breakdown:")
print(f"{'Category Group':<20} | {'Portfolio weighted average':<30} | {'Contribution to Portfolio WACI':<30} | {'Benchmark weighted average':<30} | {'Contribution to Benchmark WACI':<30}")

for category in portfolio_grouped.index:
    portfolio_value = portfolio_grouped[category]
    benchmark_value = benchmark_grouped.get(category, 0)
    print(f"{category:<20} | {portfolio_value:30.2f} | {portfolio_value/portfolio_WACI*100:30.2f}% | {benchmark_value:30.2f} | {benchmark_value/benchmark_WACI*100 if benchmark_WACI != 0 else 0:30.2f}%")

# #print all
# # Calculate total revenue (or the sum of all revenues)
# total_revenue = benchmark_df['REVENUE_USD'].sum()

# # Calculate weight based on revenue
# benchmark_df['Weight_by_Revenue'] = benchmark_df['REVENUE_USD'] / total_revenue

# # Calculate the difference between the given index weight and calculated weight
# benchmark_df['Weight_Difference'] = benchmark_df['Weight_by_Revenue'] - benchmark_df['IndexWeight']

# # Display the comparison
# print(benchmark_df[['ISSUER_NAME', 'IndexWeight', 'Weight_by_Revenue', 'Weight_Difference']])



#print(benchmark_df)
#print(portfolio_df)

# Bar graph visualization
categories = portfolio_grouped.index
plt.bar(categories, portfolio_grouped, alpha=0.7, label='Portfolio')
plt.bar(categories, benchmark_grouped, alpha=0.7, label='Benchmark', bottom=portfolio_grouped)
plt.xlabel('Category Group')
plt.ylabel('WACI')
plt.title('Category Group WACI Breakdown')
plt.legend()
plt.show()

print("\nAssumptions:")
print("- 1. There is no missing data but there can be mismatched Tickers between data.")
print("- 2. In case of mismatched data (NaN values), these rows are not considered.")
print("- 3. The weight for portfolio is the multiplication of Units and Price for each stock, but benchmark's weight is from the IndexWeight column.")

