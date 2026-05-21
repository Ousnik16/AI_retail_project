import pandas as pd
from prophet import Prophet

class DemandForecaster:
    def __init__(self, records):
        self.df = pd.DataFrame(records)

    def forecast(self, periods=14):
        model = Prophet(daily_seasonality=True)
        model.fit(self.df)
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)
        return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(periods)
