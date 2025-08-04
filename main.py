import streamlit as st
from data_fetcher import fetch_and_visualize
from ai_reporter import get_openai_report
from crypto_list import crypto_symbols 

st.set_page_config(page_title="CoinGenius : AI Financial Reporter", layout="centered")
st.title("💰 CoinGenius: Your Crypto & Stock Reporter")

st.markdown("> Get a data-driven crypto insight with an AI-generated tip!")


symbol = st.selectbox("🔍 Select a Cryptocurrency", crypto_symbols)

run = st.button("Get Insight")

if run and symbol:
    try:
        with st.spinner('🔄 Fetching and crunching your data...'):
            data, img_buf, source_note = fetch_and_visualize(symbol)

            if data.empty or 'Close' not in data.columns or data['Close'].empty:
                st.error(f"⚠️ No closing price data found for symbol '{symbol}'.")
            else:
                latest_price = float(data['Close'].iloc[-1])
                investment_tip, price_trend_summary = get_openai_report(symbol, data, stylish=True)

                st.metric(label="Latest Closing Price", value=f"${latest_price:,.2f}")

                with st.expander("📈 Trend Chart & Summary (click to expand)"):
                    st.image(img_buf, caption=f"{symbol.upper()} (6 months price trend)", use_column_width=True)
                    st.caption(price_trend_summary)
                    st.caption(f"📊 {source_note}")

                st.markdown("---")
                st.subheader("🧠 AI Investment Suggestion")

                if investment_tip.strip():
                    st.markdown(f"""
                        <div style="background: #e3ecf7; padding: 1em; border-radius: 10px; color:#183153;">
                            {investment_tip}
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("🤖 AI did not return a suggestion. Try again or use a different symbol.")

    except Exception as e:
        st.error(f"⚠️ {str(e)}")
