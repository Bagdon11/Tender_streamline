# Project Cost Breakdown System

## Overview
The Tender Management Application now includes a comprehensive **Project Cost Breakdown System** that allows you to track, calculate, and manage all project-related expenses. This feature helps create accurate tender costings and professional budget breakdowns for New Zealand construction and service projects.

## Cost Categories

### 1. **Labor Costs**
- **Project Manager Rate** ($/hour or $/month)
- **Site Supervisor Rate** ($/hour)
- **Skilled Tradesperson Rate** ($/hour)
- **General Laborer Rate** ($/hour)
- **Administrative Staff Costs** ($/month)
- **Overtime Rates** ($/hour)
- **Holiday/Leave Provisions** (%)
- **ACC (Accident Compensation)** (% of wages)
- **KiwiSaver Employer Contributions** (% of wages)

### 2. **Equipment & Materials**
- **Heavy Machinery Rental** ($/day)
- **Tools & Small Equipment** ($/month)
- **Vehicle Fleet Costs** ($/month)
- **Fuel & Transportation** ($/week)
- **Raw Materials Budget** ($)
- **Safety Equipment & PPE** ($/person)
- **Technology & Software Licenses** ($/month)

### 3. **Operational Costs**
- **Office Rent** ($/month)
- **Site Office/Facilities Rent** ($/month)
- **Utilities** (Electricity, Water, Internet) ($/month)
- **Phone & Communication** ($/month)
- **Insurance Premiums** ($/year)
- **Professional Services** (Legal, Accounting) ($/month)
- **Marketing & Business Development** ($/month)
- **Training & Certification** ($/year)

### 4. **Project-Specific Costs**
- **Permits & Consent Fees** ($)
- **Environmental Compliance Costs** ($)
- **Quality Assurance/Testing** ($)
- **Sub-contractor Costs** ($/project)
- **Contingency Fund** (% of total)
- **Risk Management Provisions** ($)
- **Bond & Guarantee Costs** ($)

### 5. **Overhead & Profit**
- **General Overhead** (% of project cost)
- **Administration Overhead** (% of project cost)
- **Profit Margin** (% of total cost)
- **GST/Tax Considerations** (% where applicable)

## Features

### 📊 **Cost Calculator**
- **Automatic totaling** of all cost categories
- **Percentage-based calculations** for overhead and profit
- **Professional breakdown display** with subtotals
- **Real-time cost estimation**

### 💾 **Data Persistence**
- **Save all cost data** to company profiles
- **Load previous costings** for similar projects
- **Version tracking** with creation and update dates
- **Company-specific cost templates**

### 📋 **PDF Integration**
- **Automatic form field recognition** for cost-related fields
- **Smart mapping** of cost categories to PDF forms
- **Auto-fill suggestions** for tender applications
- **Professional cost breakdown generation**

## How to Use

### 1. Access Project Costs
1. Open **Manage Database**
2. Select or create a company
3. Go to the **"Project Costs"** tab

### 2. Enter Cost Information
1. Fill in relevant cost fields for your project type
2. Use appropriate units ($/hour, $/month, %, etc.)
3. Enter percentages without the % symbol (e.g., "15" for 15%)
4. Leave blank any fields that don't apply to your project

### 3. Calculate Total Costs
1. Click **"Calculate Total Project Cost"**
2. Review the detailed breakdown popup
3. Verify calculations and percentages
4. Adjust values if needed and recalculate

### 4. Save and Use
1. Click **"Save Project Costs"**
2. Use data in PDF auto-fill for tender applications
3. Modify for different project types
4. Export calculations for budget presentations

## Cost Calculation Logic

### **Base Calculation:**
```
Subtotal = Labor + Equipment + Operational + Project-Specific Costs
Overhead Amount = Subtotal × (Overhead Percentage ÷ 100)
Contingency Amount = Subtotal × (Contingency Percentage ÷ 100)
Profit Amount = (Subtotal + Overhead + Contingency) × (Profit Percentage ÷ 100)

TOTAL = Subtotal + Overhead + Contingency + Profit
```

### **Example Calculation:**
- Labor Costs: $50,000
- Equipment: $20,000
- Operational: $15,000
- Project-Specific: $10,000
- **Subtotal: $95,000**
- Overhead (15%): $14,250
- Contingency (10%): $9,500
- Profit (12.5% of $118,750): $14,844
- **TOTAL: $133,594**

## New Zealand Specific Considerations

### **Employment Costs**
- **ACC levies** calculated as percentage of wages
- **KiwiSaver contributions** (minimum 3% employer contribution)
- **Holiday pay provisions** (8% minimum for annual leave)
- **Public holiday rates** (time and a half)

### **Compliance Costs**
- **Building consent fees** for construction projects
- **Resource consent costs** for environmental projects
- **Health and safety compliance** requirements
- **Quality assurance standards** (NZS specifications)

### **Tax Considerations**
- **GST registration** requirements (15% on services)
- **PAYE obligations** for employees
- **Provisional tax** for larger projects
- **FBT implications** for company vehicles/benefits

## PDF Auto-Fill Integration

The project costs automatically integrate with PDF form filling:

- **Rate fields** → Hourly/daily rates auto-populate
- **Cost estimates** → Budget fields in tender forms
- **Percentage fields** → Overhead and profit margins
- **Total calculations** → Project value estimations

## Tips for Accurate Costing

### **Research Market Rates**
- Check industry standards for your region
- Include seasonal rate variations
- Account for skill level differences
- Consider union vs non-union rates

### **Include All Overheads**
- Office costs, insurance, equipment depreciation
- Administrative time and management
- Training and professional development
- Marketing and business development

### **Plan for Contingencies**
- Weather delays (especially for outdoor work)
- Material price fluctuations
- Scope changes and variations
- Regulatory requirement changes

### **Profit Margin Considerations**
- Industry standards (typically 8-20%)
- Project complexity and risk level
- Market competition factors
- Long-term business sustainability

This comprehensive cost breakdown system ensures professional, accurate tender submissions and helps maintain profitable project margins while remaining competitive in the New Zealand market.