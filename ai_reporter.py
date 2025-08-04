import openai
import os
from dotenv import load_dotenv
import pandas as pd
import re

load_dotenv()  

def get_openai_report(symbol, data, stylish=False):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    if 'Close' not in data.columns:
        raise ValueError("No 'Close' column found in data.")

    close_series = data['Close']
    if isinstance(close_series, pd.DataFrame):
        close_series = close_series.squeeze()

    last_30 = close_series.tail(30)

    if last_30.empty:
        raise ValueError("No closing price data available for analysis.")

    last_30_prices = last_30.tolist()
    prompt = (
        f"Analyze the 6-month closing price trend for {symbol.upper()}."
        f" Here are the last 30 days of closing prices: {last_30_prices}.\n"
        "First, give me a one-sentence data summary of the trend (upward, downward, sideways)."
        " Then, provide a concise investment tip. Output two sections: 1) Trend Summary 2) Investment Suggestion."
    )

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )
    except Exception as e:
        raise RuntimeError(f"OpenAI API call failed: {e}")

    ai_response = completion['choices'][0]['message']['content']

    if stylish:
        
        parts = re.split(r"\b2[\).:-]\s*", ai_response, maxsplit=1)

        if len(parts) == 2:
            trend_summary = re.sub(r"^1[\).:-]?\s*", "", parts[0]).strip()
            investment_tip = parts[1].strip()
        else:
           
            lines = ai_response.strip().splitlines()
            trend_summary = ""
            investment_tip = ""

            for line in lines:
                lower = line.lower()
                if "trend" in lower or "price" in lower:
                    trend_summary += line.strip() + " "
                elif "invest" in lower or "consider" in lower or "buy" in lower or "sell" in lower:
                    investment_tip += line.strip() + " "

            trend_summary = trend_summary.strip() or "📊 Unable to determine trend clearly."
            investment_tip = investment_tip.strip() or "💡 The AI recommends waiting for more stable signals before investing."

        return investment_tip, trend_summary

    return ai_response
