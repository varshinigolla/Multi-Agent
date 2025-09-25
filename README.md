# 🤖 Multi-Agent Financial Analysis System

A powerful AI-driven financial analysis platform that understands natural language requests and uses specialized AI agents to provide comprehensive financial insights, visualizations, and reports.

## 🌟 What This System Does

Imagine you're a business analyst and you want to understand your company's financial performance. Instead of manually creating charts, calculating metrics, and writing reports, you can simply ask this system in plain English:

- **"Show me profit trends for the last 3 quarters"**
- **"Create charts comparing performance by country"**
- **"Analyze which product segments are most profitable"**
- **"Give me a summary of our financial performance"**

The system will automatically:
1. 🧠 **Plan** which AI agents to use
2. 📊 **Fetch** the relevant financial data
3. 🔍 **Analyze** trends and patterns
4. 📈 **Create** interactive visualizations
5. 📝 **Generate** professional reports

## 🎯 Key Features

### ✨ **Natural Language Processing**
- Ask questions in plain English
- No technical knowledge required
- Intelligent understanding of business requests

### 🤖 **AI Agent Collaboration**
- **4 Specialized Agents** work together seamlessly
- Each agent has a specific role and expertise
- Agents share information and build upon each other's work

### 📊 **Comprehensive Analysis**
- Trend analysis and pattern recognition
- Quarterly and yearly performance comparisons
- Segment, country, and product breakdowns
- Statistical insights and risk assessment

### 📈 **Professional Visualizations**
- Interactive charts and graphs
- Multiple visualization types
- Professional styling and formatting

### 📝 **AI-Powered Reports**
- Executive summaries
- Key insights extraction
- Investment recommendations
- Business-ready documentation

## 🏗️ System Architecture

### The 4 AI Agents

#### 1. 📊 **Data Fetcher Agent**
**What it does:** Retrieves and processes financial data
- Loads data from Excel files
- Applies smart filters based on your request
- Calculates summary statistics
- Provides data breakdowns by segments, countries, products

#### 2. 🔍 **Analyzer Agent**
**What it does:** Performs deep financial analysis
- Identifies trends (upward, downward, stable)
- Compares quarterly performance
- Calculates profit margins and efficiency metrics
- Analyzes performance by business segments
- Provides statistical insights and risk measures

#### 3. 📈 **Visualizer Agent**
**What it does:** Creates interactive charts and graphs
- Profit trend charts with moving averages
- Quarterly comparison charts
- Volume analysis charts
- Professional Plotly visualizations
- Interactive hover details and zoom

#### 4. 📝 **Summarizer Agent**
**What it does:** Generates comprehensive reports using AI
- Executive summaries
- Key insights and recommendations
- Professional business reports
- Investment analysis and conclusions

### The Orchestrator
**What it does:** The "brain" that coordinates everything
- Uses ChatGPT-4 to understand your request
- Plans which agents to use and in what order
- Handles clarification when requests are unclear
- Combines all results into a final report

## 🚀 How to Use

### Prerequisites
- Python 3.7 or higher
- OpenAI API key (for AI-powered features)

### Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd multi-agent-financial-analysis
   ```

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your OpenAI API key**
   - Create a `.env` file in the project folder
   - Add your API key:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

### Running the System

#### Option 1: Web Interface (Recommended for beginners)
```bash
streamlit run app.py
```
- Opens in your web browser
- User-friendly interface
- Real-time agent status
- Interactive visualizations

#### Option 2: Command Line Interface
```bash
python main.py
```
- Text-based interface
- Good for automation
- Shows detailed progress

## 💡 Example Usage

### Example 1: Basic Trend Analysis
**Your request:** "Show me profit trends for the last 3 quarters"

**What happens:**
1. Data Fetcher gets last 3 quarters of data
2. Analyzer calculates trend direction and changes
3. Visualizer creates an interactive trend chart
4. Summarizer writes a professional summary

**You get:**
- Interactive profit trend chart
- Statistical analysis (trend direction, change percentages)
- Professional summary with insights

### Example 2: Segment Performance Comparison
**Your request:** "Compare performance by business segment"

**What happens:**
1. Data Fetcher gets all segment data
2. Analyzer calculates metrics for each segment
3. Visualizer creates comparison charts
4. Summarizer identifies best/worst performing segments

**You get:**
- Segment comparison charts
- Performance metrics for each segment
- Recommendations on which segments to focus on

### Example 3: Comprehensive Analysis
**Your request:** "Give me a complete financial analysis report"

**What happens:**
1. All agents work together
2. Data Fetcher gets comprehensive data
3. Analyzer performs multiple analysis types
4. Visualizer creates various charts
5. Summarizer creates an executive report

**You get:**
- Multiple interactive visualizations
- Detailed financial metrics
- Executive summary
- Key insights and recommendations

## 🎨 User Interface

### Web Interface Features
- **Request Input:** Large text area for your questions
- **Example Requests:** Click to try pre-made examples
- **Real-time Status:** See which agents are working
- **Tabbed Results:**
  - **Summary:** AI-generated insights
  - **Analysis:** Detailed metrics and trends
  - **Charts:** Interactive visualizations
  - **Data:** Raw data preview
  - **Execution:** Agent status and performance

### Command Line Features
- **Interactive Chat:** Type requests and get responses
- **Status Commands:** Check system status
- **Help System:** Built-in guidance
- **Progress Updates:** Real-time agent status

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for AI features
- `OPENAI_MODEL`: AI model to use (default: gpt-4)

### Data Source
- Currently uses: `04-01-Financial Sample Data.xlsx`
- Easy to modify for different data sources
- Supports various data formats

## 🛠️ Troubleshooting

### Common Issues

**1. "OpenAI API Key not found"**
- Make sure you have a `.env` file with your API key
- Check that the key is valid and has credits

**2. "Excel file not found"**
- Ensure `04-01-Financial Sample Data.xlsx` is in the project folder
- Check the file name matches exactly

**3. "No data available"**
- Verify your Excel file has the required columns
- Check that your request matches available data

**4. "Agent failed"**
- Check the error messages in the Execution tab
- Ensure all dependencies are installed
- Try a simpler request first

### Getting Help
- Check the logs for detailed error messages
- Try the example requests first
- Start with simple requests and build complexity

## 🎯 Business Value

### For Business Analysts
- **Time Saving:** No more manual chart creation
- **Consistency:** Standardized analysis approach
- **Insights:** AI-powered pattern recognition
- **Professional Output:** Business-ready reports

### For Managers
- **Quick Insights:** Get answers in plain English
- **Comprehensive Analysis:** Multiple perspectives in one request
- **Visual Reports:** Easy-to-understand charts and graphs
- **Actionable Recommendations:** AI-generated insights

### For Developers
- **Modular Design:** Easy to add new agents
- **Extensible:** Simple to add new data sources
- **Well-Documented:** Clear code structure
- **Error Handling:** Robust error management

## 🔮 Future Enhancements

- **More Data Sources:** Connect to databases, APIs
- **Additional Agents:** Risk analysis, forecasting agents
- **Advanced Visualizations:** 3D charts, dashboards
- **Integration:** Connect to business intelligence tools
- **Customization:** User-specific analysis preferences

## 📚 Learning Resources

### Understanding the Code
- **`main.py`:** Command line interface
- **`app.py`:** Web interface
- **`orchestrator.py`:** Agent coordination logic
- **`agents/`:** Individual agent implementations

### Key Concepts
- **Multi-Agent Systems:** How agents work together
- **Natural Language Processing:** Understanding user requests
- **Financial Analysis:** Common metrics and calculations
- **Data Visualization:** Creating effective charts

## 🤝 Contributing

### Adding New Agents
1. Create a new agent class in `agents/`
2. Inherit from `BaseAgent`
3. Implement required methods
4. Add to the orchestrator

### Adding New Data Sources
1. Extend the Data Fetcher Agent
2. Add new data loading logic
3. Update data format for other agents


## 🆘 

If you encounter issues:
1. Check the troubleshooting section
2. Review error messages in the Execution tab
3. Try the example requests
4. Ensure all dependencies are installed

---

## 💝 Built with Passion

This Multi-Agent Financial Analysis System was crafted with dedication, attention to detail, and a genuine passion for creating intelligent solutions that solve real-world business problems. Every line of code, every feature, and every user experience consideration was designed to make financial analysis accessible, powerful, and delightful to use.

---

## 📞 Get in Touch

**Questions? Suggestions? Want to discuss this project?**

I'd love to hear from you! Whether you're curious about the technical implementation, have ideas for improvements, or just want to chat about AI and financial technology, feel free to reach out.

**Varshini Golla**  
📧 **varshinigolla313@gmail.com**

*Let's connect and explore the future of intelligent financial analysis together!* 🚀

---

**Ready to get started?** Run `streamlit run app.py` and try asking: *"Show me profit trends for the last 3 quarters"* 🚀