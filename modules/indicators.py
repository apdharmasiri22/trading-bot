import pandas_ta as ta

def add_indicators(df):
    """
    මෙම ෆන්ක්ෂන් එක මගින් Dataframe එකට 
    Indicators තීරු (Columns) එකතු කරනු ලබයි.
    """
    # 1. EMA 200 (Trend එක බලන්න)
    df.ta.ema(length=200, append=True)
    
    # 2. RSI (Momentum එක බලන්න)
    df.ta.rsi(length=14, append=True)
    
    # 3. Bollinger Bands (Volatility එක බලන්න)
    df.ta.bbands(length=20, append=True)
    
    return df
