# MealMetrics Database Check Tools

This folder contains tools to monitor and analyze your MealMetrics database users and their data.

## 🚀 Quick Start

### **From This Directory (database/check):**

#### **Windows:**
```bash
# Double-click this file:
.\check_users.bat

# Or run manually:
python quick_db_check.py
python check_all_users.py
```

#### **Linux/Mac:**
```bash
# Run the shell script:
./check_users.sh

# Or run manually:
python quick_db_check.py
python check_all_users.py
```

#### **From MealMetrics Root Directory:**
```bash
# Run from root:
python database/check/quick_db_check.py
python database/check/check_all_users.py
```

---

## 📁 Files in This Folder

### **1. `quick_db_check.py`** ⚡
**Quick overview of all users and their activity**

**Features:**
- Database overview (total users, meals, calories)
- All users with activity status
- Recent meals for each user
- Today's activity summary

**Usage:**
```bash
python quick_db_check.py
```

### **2. `check_all_users.py`** 📊
**Detailed analysis with export options**

**Features:**
- Comprehensive user statistics
- Detailed meal history
- Activity patterns analysis
- JSON export capability

**Usage:**
```bash
# Detailed view
python check_all_users.py

# Simple list only
python check_all_users.py --simple

# Export to JSON
python check_all_users.py --export users_data.json
```

### **3. `DATABASE_TOOLS.md`** 📖
**Complete documentation and advanced usage guide**

---

## 📊 Sample Output

```
📊 DATABASE OVERVIEW
👥 Total Users: 3
🍽️ Total Meals: 2
🔥 Total Calories: 750

👥 ALL USERS:
 1. Arafat (@arafat7xox)
    ID: 1383294957
    Activity: 🟢 Today
    Meals: 2 | Calories: 750 | Days: 1
    Recent meals:
      • Mango juice - 100 cal (06/10 03:01)
      • Indian curry plate - 650 cal (06/10 02:51)

 2. Khaled Hasan Irfan (@khaledirfan)
    ID: 2046141570
    Activity: 🟢 Today
    Meals: 0 | Calories: 0 | Days: 0
    No meals logged yet
```

---

## 🎯 Use Cases

### **Monitor Bot Health**
```bash
python quick_db_check.py
```
Check if users are actively logging meals

### **User Engagement Analysis**
```bash
python check_all_users.py
```
See detailed user activity patterns

### **Export Data for Analysis**
```bash
python check_all_users.py --export data.json
```
Export user data for external analysis

### **Daily Monitoring**
```bash
# Quick daily check
python quick_db_check.py | grep "📅 TODAY"
```

---

## 🔒 Privacy & Security

- ✅ **Read-only operations** - These tools only read data, never modify
- ✅ **User isolation verified** - Each user's data is completely separate
- ✅ **Safe to run** - No risk of affecting user data or bot operation

---

## 🛠️ Troubleshooting

### **Import Errors**
```bash
# Make sure you're running from MealMetrics root:
cd /path/to/MealMetrics
python database/check/quick_db_check.py

# Or from this directory with proper imports:
cd database/check
python quick_db_check.py
```

### **Database Not Found**
```bash
# Check if database exists in MealMetrics root:
ls -la *.db

# Common database names:
# - mealmetrics.db
# - database.db
```

### **Permission Issues**
```bash
# Make sure database file is readable:
chmod 644 mealmetrics.db

# Make shell script executable (Linux/Mac):
chmod +x ../../check_users.sh
```

---

## 📈 Advanced Usage

### **Custom Queries**
```bash
# Direct SQLite access:
sqlite3 ../../mealmetrics.db

# Common queries:
SELECT COUNT(*) FROM users;
SELECT * FROM meals WHERE date = date('now');
```

### **Automated Monitoring**
```bash
# Add to cron job for daily reports:
0 9 * * * cd /path/to/MealMetrics && python database/check/quick_db_check.py > daily_report.txt
```

### **Data Export**
```bash
# Export all data:
python check_all_users.py --export full_backup.json

# Simple user list:
python check_all_users.py --simple > user_list.txt
```

---

## 🔗 Related Files

- **`../../check_users.bat`** - Windows batch script (run from root)
- **`../../check_users.sh`** - Linux/Mac shell script (run from root)
- **`DATABASE_TOOLS.md`** - Complete documentation

---

**These tools help you maintain a healthy, monitored MealMetrics bot!** 📊🤖
