# GPU Profit Calculator

A web-based calculator for analyzing the profitability of GPU-based LLM inference deployments. This tool helps you understand the financial viability of running large language models on GPU infrastructure.

## Features

### Core Calculations
- **Real-time profit analysis** with instant updates as you modify parameters
- **Cost per token** calculation based on GPU infrastructure costs
- **Revenue per token** based on input/output pricing models
- **Profit per token, hour, and day** calculations
- **ROI analysis** over 30-day periods

### Advanced Insights
- **Break-even analysis** showing required TPS for profitability
- **Utilization metrics** comparing current vs. break-even performance
- **Scaling impact** projections for 2x GPU count and 2x TPS scenarios
- **Visual indicators** for profitable vs. unprofitable scenarios

### Input Parameters
- **GPU Cost per Hour**: Infrastructure cost per GPU per hour
- **GPU Count**: Number of GPUs in your deployment
- **Input/Output TPS**: Tokens per second for input and output processing
- **Input/Output Pricing**: Revenue per million tokens for input and output

## Usage

### Running the Calculator

1. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn jinja2
   ```

2. **Run the server**:
   ```bash
   python gpu_profit_calculator.py
   ```

3. **Access the calculator**:
   Open your browser and navigate to `http://localhost:8001`

### Example Scenarios

#### Scenario 1: 8x H100 Deployment
- **GPU Cost**: $2.00/hour per H100
- **GPU Count**: 8
- **Input TPS**: 1000 tokens/sec
- **Output TPS**: 2000 tokens/sec
- **Input Price**: $0.28/M tokens
- **Output Price**: $0.88/M tokens

**Results**: ~$1,200/day profit potential

#### Scenario 2: Cost-Effective Deployment
- **GPU Cost**: $1.50/hour per GPU
- **GPU Count**: 4
- **Input TPS**: 500 tokens/sec
- **Output TPS**: 1000 tokens/sec
- **Input Price**: $0.20/M tokens
- **Output Price**: $0.60/M tokens

**Results**: ~$400/day profit potential

## Key Metrics Explained

### Profitability Metrics
- **Total TPS**: Combined input and output tokens per second
- **Tokens/hour**: Total token processing capacity per hour
- **Cost/hour**: Total GPU infrastructure cost per hour
- **Revenue/token**: Average revenue generated per token processed
- **Cost/token**: Infrastructure cost per token processed
- **Profit/token**: Net profit per token (revenue - cost)

### Business Metrics
- **Profit/hour**: Hourly profit from the deployment
- **Profit/day**: Daily profit projection
- **ROI (30 days)**: Return on investment over 30 days (assuming $20k per H100)

### Break-even Analysis
- **Break-even TPS**: Minimum tokens per second needed to cover costs
- **Current utilization**: Percentage of break-even capacity being utilized

### Scaling Impact
- **2x GPU count**: Projected daily profit with double the GPU infrastructure
- **2x TPS**: Projected daily profit with double the throughput

## Use Cases

### 1. Infrastructure Planning
- Evaluate different GPU configurations before deployment
- Compare cloud vs. on-premise cost structures
- Plan scaling strategies based on projected demand

### 2. Pricing Strategy
- Set competitive pricing while maintaining profitability
- Understand the impact of price changes on margins
- Optimize input/output pricing ratios

### 3. Performance Optimization
- Identify optimal TPS targets for maximum profitability
- Understand the relationship between throughput and costs
- Plan capacity utilization strategies

### 4. Investment Analysis
- Calculate ROI for GPU infrastructure investments
- Compare different model deployment strategies
- Assess the financial viability of new model deployments

## Technical Details

### Calculation Methodology
```
Total TPS = Input TPS + Output TPS
Tokens per Hour = Total TPS × 3600
Cost per Hour = GPU Cost × GPU Count
Cost per Token = Cost per Hour ÷ Tokens per Hour

Revenue per Token = ((Input TPS × Input Price) + (Output TPS × Output Price)) ÷ Total TPS ÷ 1,000,000
Profit per Token = Revenue per Token - Cost per Token
Profit per Hour = Profit per Token × Tokens per Hour
Profit per Day = Profit per Hour × 24
```

### Assumptions
- **GPU Investment**: $20,000 per H100 GPU (used for ROI calculations)
- **Linear scaling**: Assumes perfect scaling with additional GPUs
- **Continuous operation**: 24/7 deployment assumption
- **Market pricing**: Uses current market rates for token pricing

## Integration with LLM Valuation Calculator

This calculator complements the [LLM Valuation Calculator](llm_valuation.py) by providing:
- **Financial analysis** vs. technical capacity analysis
- **Profitability focus** vs. throughput optimization
- **Business planning** vs. deployment planning

Use both calculators together to:
1. Determine optimal model selection with the LLM Valuation Calculator
2. Analyze profitability with the GPU Profit Calculator
3. Make informed deployment decisions

## Future Enhancements

- **Multi-model comparison**: Compare profitability across different models
- **Dynamic pricing**: Real-time market price integration
- **Advanced scaling**: Non-linear scaling models for large deployments
- **Risk analysis**: Monte Carlo simulations for uncertainty
- **Export functionality**: PDF reports and data export options

## Contributing

Feel free to submit issues and enhancement requests. The calculator is designed to be easily extensible for additional features and calculations. 