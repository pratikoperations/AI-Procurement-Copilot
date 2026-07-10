"""Chart helper module placeholder for Build 0.2."""

import plotly.express as px


def supplier_price_chart(df):
    """Return a supplier price bar chart."""
    return px.bar(
        df,
        x="Supplier",
        y="Quoted Unit Price USD",
        title="Quoted Unit Price by Supplier",
        text_auto=".4f",
    )
