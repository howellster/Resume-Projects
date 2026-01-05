# cache functions calls like scraping for ticker symbols or stock info
# if needed to save results only accessible within a session use session state
# session state for stock info, cache for ticker info
# cache a function by decorating it with st.cache_data
#  set a time to live (ttl) parameter ex. ttl=datetime.timedelta(hours=1)
# show_spinner = "Fetching data..."
# use input widgets to get a certain number of rows from a cached object
# experimental_allow_widgets = True
# num_rows = st.slider("Number of rows to get
# session state shares variables between reruns for each user session
# use a session_state slider for graphs of returns over 1-10 years and on_change
# use session_state on click with on change
# col, col,2 buff, beta columns with col1 = thing
# make stock groupings by industry
# have a choice for what the user wants to compare
import yfinance as yf
import altair as alt
from dateutil.relativedelta import relativedelta
import pandas as pd
# first page will be individual investments, second page will be ETFs
import streamlit as st
from requests import session

st.set_page_config(page_title="Investment Comparison App",
                   layout="wide",
                   initial_sidebar_state="auto"
                   )
st.title("Investment Comparison")
st.markdown("""Compare different investments using yfinance data""")

col1,col2,col3= st.columns([1,2,1])
horizon_choices = {
    "5 days": "5d",
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "3 Years": "3y",
    "5 Years":"5y",
    "10 Years": "10y",
    "Max": "max"
}
ticks = {
"Tech": ("AAPL","NVDA","MSFT","AVGO"),
"Communication": ("GOOG","META","TCEHY","NFLX","TMUS"),
"Consumer Discretionary": ("AMZN","TSLA","BABA","LVMUY","HD"),
"Banking":("JPM","BAC","WFC","C","USB"),
"Commercial Real Estate":("CBRE","JLL","CWK","PLD"),
"Energy":("2222.SR","XOM","CVX","SHEL","BP"),
"Financials":("BRK-B","BLK"),
"Credit":("V","MA"),
"Health Care":("LLY","JNJ","ABBV","UNH","ROG.SW"),
"Consumer Staples":("WMT","COST","PG","KO","PEP"),
"Industrials":("GE","CAT","RTX","HON","UNP"),
"Utilities":("NEE","SO","DUK","D","AEP"),
"Materials": ("LIN","BHP","RIO","AI.PA","SHW")
}
com_cryp = {
'Commodities': ("GC=F","SI=F","CL=F"),
"Crypto": ('BTC-USD', "ETH-USD"),
}


# defines columns and headers
with col1:
    st.subheader("Stocks")
with col2:
    st.subheader("Commodities and Crypto")
with col1.container(border=True,height="content",vertical_alignment="top"):
    industry_display = st.multiselect("Inudstries",options=ticks.keys())
    industry=st.session_state.industry = industry_display
t=[]
for thing in industry:
    for company in ticks[thing]:
        t.append(company)
# container for our ticker options and time horizon
with col1.container(border=True,height = "stretch",vertical_alignment="top"):
    tick_options = st.multiselect("Tickers",options=t,)
    tickers = st.session_state.tickers = tick_options
    horizon = st.pills(
        "Time period",
        options=list(horizon_choices.keys()),
        default="1 Year")
    period = st.session_state.period = horizon_choices[horizon]


with col2.container(border=True,height="stretch",vertical_alignment="top"):
    commod_crypto = st.multiselect("Alternatives",options=com_cryp)
    alternatives = st.session_state.alternatives = commod_crypto
# we add choices to a session state and grab them using lists 
c = []
store = []
for thing in alternatives:
    for alternative in com_cryp[thing]:
        c.append(alternative)
with col2.container(border= True, height= "stretch", vertical_alignment="top"):
    alternative_options = st.multiselect("Commodities and Crypto",options=c)
    alternative_selected = st.session_state.alternative_selected = alternative_options
for thing in alternative_selected:
    store.append(thing)
# grabbing data for alternative investments like commodities and crypto
alternative_data = yf.download(store,period=period)["Close"]
alternative_data.index = pd.to_datetime(alternative_data.index)
alternative_data.index = alternative_data.index.strftime("%Y-%m-%d")
price_data= pd.DataFrame()
for ticker in tickers:
    price_data[f"{ticker}"]=yf.Ticker(ticker).history(f"{period}")["Close"]
# grabbing data for stocks
price_data.reset_index = price_data.index.strftime("%Y-%m-%d")
price_data.index=price_data.reset_index
# combine the two dataframes
concat = pd.concat([price_data,alternative_data],axis=1)
# normalize the prices
normalized = concat.div(concat.iloc[0])
# transform the data into the form expected by altair for visualization
new=normalized.reset_index().melt('Date',var_name="company",value_name="normalized price")
dividend_data = pd.DataFrame()
for ticker in tickers:
    raw = yf.Ticker(f"{ticker}").dividends
    raw.index = raw.index.year
    div = raw[~raw.index.duplicated(keep="first")]
    dividend_data[f"{ticker}"]= div
# dividend data
new_div=dividend_data.reset_index().melt(id_vars="Date",var_name="company",value_name="dividend")
# defines a container for chart selection
with col2.container(border=True,width="stretch",height="stretch",gap="medium"):
    chart_choice = st.selectbox(options=['price','dividend'],label="Select Chart",placeholder="Select chart type")
    price=alt.Chart(new).mark_line().encode(x='Date:T', y='normalized price:Q', color='company:N')
    dividend = alt.Chart(new_div).mark_trail().encode(x='Date:T',y='dividend:Q',color='company:N')
    maybe = {'price':price,'dividend':dividend}
    chart = st.session_state.chart = chart_choice
    st.write(chart)
    st.altair_chart(maybe[chart],use_container_width=True)
with col3:
    st.markdown("Leaderboard")
    # sort the leaderboard based on average returns over the period
    av = {}
    for thing in concat:
        first = concat[f"{thing}"][0]
        last = concat[f"{thing}"][-1]
        if True == pd.isna(concat[f"{thing}"][-1]):
            last = concat[f"{thing}"][-3]
        av[f"{thing}"] = (last - first) / first
# sorts the leaderboard
    sort = sorted(av.items(), key=lambda x: x[1], reverse=True)
    for k,v in sort:
        v = round(v * 100,ndigits=3)
        st.write(k,v)

