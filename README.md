# 📈 Algorithmic Trading Strategy Project - Doji Pattern & Bollinger Bands with Advanced Optimizations

## 🔍 Overview
This project is a deep dive into **algorithmic trading**, focusing on backtesting and optimizing **Doji-based trading strategies** using multiple **technical indicators**. The strategy was iteratively refined through systematic testing to improve profitability and minimize risks.

Through **data-driven experimentation**, I developed a **robust, dynamic trading model** that integrates:
- **Multiple Candlestick pattern recognition**
- **Volumetric confirmation (OBV)**
- **ATR-based position sizing**
- **Adaptive thresholds**
- **Advanced risk management techniques**  

**Note:** Detailed Project Report consisting of entire methodollogy and research is uploaded in the Repository.

## ⚡ Features & Strategy Development

### 🔹 **1. Multiple Technical Indicators Integration**
- **MACD** - Used for trend direction and momentum.
- **RSI** - To filter overbought/oversold market conditions.
- **ADX** - To confirm trend strength and avoid false signals.
- **OBV (On-Balance Volume)** - For Volume Analysis to validate signal strength with volume data.
- **ATR (Average True Range)** - Used for **dynamic position sizing** and setting **stop-loss/take-profit levels**.

### 🔹 **2. Multi-Candlestick Pattern Recognition**
Recognised a wide variety of candlestick pattern besides basic Doji pattern like:-
- **Gravestone Doji**
- **Dragonfly Doji**
- **Hammer & Inverted Hammer**
for improved **signal generation**

### 🔹 **3. Dynamic Optimization**
- **Adaptive thresholds** to account for market volatility.
- **ATR-based position sizing** for risk-adjusted trade allocation.

### 🔹 **4. Risk Management Enhancements**
Implemented **dynamic stop-loss** and **take-proifit levels** using **ATR-based trailing stop-loss**, effectively reducing drawdowns and locking in profits.

### 🔹 **5. Innovative Bucket Strategy**
Devised a structured 4-bucket approach to optimize each component of the trading process:
1. **Bucket 1: Signal Refinement** - Used volume confirmation, multiple candlestick recognition & multi-timeframe analysis.
2. **Bucket 2: Risk Management** - Experimented with different stop-loss/take-profit levels, concluding that ATR-based trailing stop-loss worked best.
3. **Bucket 3: Position Sizing** - Compared static vs. dynamic sizing.
4. **Bucket 4: Parameter Tuning** - Fine-tuned Bollinger Bands, lookback periods and MACD settings

## 📊 Backtesting Results
- The strategy was iteratively improved across **multiple datasets and time periods** to avoid overfitting.
- Significant improvements were made by refining **entry-exit logic, signal filtering, and dynamic trade allocation**.

## 🛠️ Technologies Used
- **Python**
- **Blueshift API**

## 📌 Key Takeaways & Learnings
- Understood the role of **multiple technical indicators** in trading.
- Experimented with **risk-adjusted trade allocation** via **ATR-based position sizing**.
- Developed a structured **strategy refinement framework** using a **bucket-based optimization** approach.
- Gained **hands-on experience** in **backtesting, debugging, and optimizing algorithmic trading strategies**.

## 🎯 Future Improvements
- Explore **machine learning-based signal classification**.
- Test the strategy on **different asset classes** (stocks, crypto, forex).
- Automate strategy deployment using **broker APIs**.

## 💡 Acknowledgments
This project was initially inspired by a structured trading challenge and further refined through **independent research and experimentation**.