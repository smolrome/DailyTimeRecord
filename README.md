# Advanced Time Record System

![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A sophisticated desktop application for tracking work hours, breaks, and productivity with advanced reporting features.

---

## 🚀 Features

- 🕒 Clock in/out functionality with real-time tracking  
- ☕ Break management with customizable break types  
- 📊 Comprehensive time analytics and visualization  
- 👤 Multi-user support with authentication  
- 🌙 Light/dark theme support  
- 📅 Calendar integration for past record entry  
- 📈 Productivity statistics and reports  
- 💾 Data export to CSV/JSON  
- 🖨️ Printable summaries  
- 🔒 Secure user data storage  

---

## 📦 Requirements

- Python 3.7+
- Required packages:
  - `tkinter`
  - `tkcalendar`
  - `matplotlib`
  - `pillow`
  - `requests`

---

## 🛠️ Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/smolrome/DailtyTimeRecord.git
   cd DailtyTimeRecord
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   python DTR.py
   ```

---

## 💡 Usage

### 🔐 Login/Register

- New users can register with a username and password  
- Existing users can log in with their credentials  

### 🖥️ Main Interface

- Clock in/out with the main buttons  
- Start/end breaks as needed  
- View real-time work duration calculations  

### 📁 Records Management

- View all time records in a sortable table  
- Right-click records to edit or delete  
- Add notes to specific records  

### 📊 Reports & Analytics

- Generate daily/weekly/monthly reports  
- View time distribution charts  
- Export data to CSV or JSON  

### ⚙️ Settings

- Toggle between light/dark mode  
- Configure work hour thresholds  
- Set backup preferences  

---

## 📂 File Structure

```
time-record-system/
├── DTR.py                # Main application file
├── users/                # User data directory
│   ├── username1/        # Individual user folders
│   │   ├── records.json  # Time records
│   │   └── settings.json # User preferences
│   └── users.dat         # User credentials database
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

---

## 🖼️ Screenshots

> Create a `screenshots` folder and include actual screenshots of the following:

- **Login Screen** — Login and registration interface  
- **Main Interface** — Main application with time tracking  
- **Analytics** — Time distribution analytics  

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository  
2. Create your feature branch:  
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. Commit your changes:  
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. Push to the branch:  
   ```bash
   git push origin feature/AmazingFeature
   ```
5. Open a Pull Request  

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 📬 Contact

Jerome Pedrosa — jeromepedrosa3@gmail.com  
Project Link: [https://github.com/smolrome/DailyTimeRecord](https://github.com/smolrome/DailyTimeRecord)
