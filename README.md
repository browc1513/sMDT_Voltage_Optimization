# **sMDT Voltage Optimization**

## **📌 Project Overview**
This repository is dedicated to the **analysis of the Gaseous Ionization Curve for the sMDT (small-diameter Muon Drift Tube)** and the determination of its **optimal operating voltage range** for effective muon detection. The study involves processing raw scintillator data, calculating signal areas, analyzing event durations, and visualizing the detector’s response across different voltage levels.

## **🔬 Research Objectives**
✔ **Extract the Gaseous Ionization Curve** of the sMDT.  
✔ **Determine the optimal voltage range** for stable muon detection.  
✔ **Analyze signal characteristics** such as pulse duration and integration area.  
✔ **Visualize the detector’s response** across different voltage settings.  

## **📁 Repository Structure**
```
sMDT_Voltage_Optimization/
│── data/                 # Raw CSV files containing signal data
│── figures/              # Generated plots & visualizations
│── scripts/              # Python scripts for analysis
│── results/              # Processed data & computed results
│── README.md             # Project documentation
│── .gitignore            # Exclude unnecessary files
│── requirements.txt      # Python dependencies
```

## **📊 Key Analysis Methods**
- **Event Counting**: Identifying discrete muon detection events using voltage thresholds.  
- **Signal Integration (Riemann Sums)**: Calculating the area under each detected event pulse.  
- **Event Duration Analysis**: Measuring the time difference between the rise and fall of a signal.  
- **Histogram & KDE Analysis**: Visualizing the distribution of signal areas and durations.  

## **⚙️ How to Use This Repository**
### **1️⃣ Clone the repository**
```sh
git clone https://github.com/YOUR-USERNAME/sMDT_Voltage_Optimization.git
```

### **2️⃣ Navigate to the project folder**
```sh
cd sMDT_Voltage_Optimization
```

### **3️⃣ Install dependencies**
```sh
pip install -r requirements.txt
```

### **4️⃣ Run analysis scripts**
```sh
python scripts/Scintillator_Event_Duration.py
python scripts/Scintillator_Event_Areas.py
python scripts/Scintillator_Signal_Density.py
```

## **📌 Expected Outcomes**
🔹 A well-defined **Ionization Curve** for the sMDT.  
🔹 Identification of the **voltage range that maximizes muon detection efficiency**.  
🔹 Insights into **pulse characteristics** and **detector performance** at varying voltages.  

## **📞 Contact & Contributions**
If you are interested in this work or have suggestions for improvement, feel free to **submit an issue** or **fork the repository**. Contributions are welcome!

