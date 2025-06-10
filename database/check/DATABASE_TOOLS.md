# MealMetrics Database Tools

This directory contains several tools to help you monitor and manage your MealMetrics database.

## 🔍 Quick Database Check Tools

### 1. **Quick Check (Recommended)**
```bash
# Windows
check_users.bat

# Linux/Mac
./check_users.sh

# Or directly with Python
python quick_db_check.py
```

**What it shows:**
- Total users, meals, and calories
- All users with their activity status
- Recent meals for each user
- Today's activity summary

**Sample Output:**
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
```

### 2. **Detailed Check**
```bash
python check_all_users.py
```

**What it shows:**
- Comprehensive user statistics
- Detailed meal history
- Activity patterns
- Pending meals

**Options:**
```bash
# Simple list only
python check_all_users.py --simple

# Export to JSON
python check_all_users.py --export users_data.json
```

## 📊 What You Can Monitor

### **User Activity**
- 🟢 **Active today** - User logged meals today
- 🟡 **Active recently** - User active within 7 days  
- 🔴 **Inactive** - User hasn't been active for a while

### **User Statistics**
- Total meals logged
- Total calories tracked
- Days with data
- Average calories per day
- Date range of activity
- Recent meal history

### **Database Health**
- Total users in system
- Overall meal count
- Total calories tracked
- Today's activity
- Pending meals count

## 🛠️ Advanced Database Operations

### **Direct SQLite Access**
```bash
# Open database directly
sqlite3 mealmetrics.db

# Common queries
.tables                          # Show all tables
SELECT * FROM users;             # Show all users
SELECT * FROM meals LIMIT 10;    # Show recent meals
```

### **User-Specific Queries**
```sql
-- Get specific user's data
SELECT * FROM meals WHERE user_id = 1383294957;

-- Get user's daily summaries
SELECT * FROM daily_summaries WHERE user_id = 1383294957;

-- Count meals per user
SELECT user_id, COUNT(*) as meal_count 
FROM meals 
GROUP BY user_id 
ORDER BY meal_count DESC;
```

### **Activity Analysis**
```sql
-- Most active users
SELECT u.username, COUNT(m.id) as meals
FROM users u
LEFT JOIN meals m ON u.user_id = m.user_id
GROUP BY u.user_id
ORDER BY meals DESC;

-- Daily activity
SELECT date, COUNT(*) as meals, SUM(calories) as total_calories
FROM meals
GROUP BY date
ORDER BY date DESC;

-- Recent activity (last 7 days)
SELECT u.username, COUNT(m.id) as meals
FROM users u
JOIN meals m ON u.user_id = m.user_id
WHERE m.timestamp >= datetime('now', '-7 days')
GROUP BY u.user_id;
```

## 🔒 Data Privacy & Security

### **User Data Isolation**
Each user's data is completely isolated:
- All queries filter by `user_id`
- No user can access another user's data
- Clearing data only affects the specific user

### **Safe Operations**
```sql
-- ✅ SAFE: Delete specific user's data
DELETE FROM meals WHERE user_id = 123456789;

-- ❌ DANGEROUS: Delete all data (never do this)
DELETE FROM meals;  -- This would delete ALL users' data!
```

### **Backup Before Operations**
```bash
# Create backup
cp mealmetrics.db mealmetrics_backup_$(date +%Y%m%d).db

# Or export to SQL
sqlite3 mealmetrics.db .dump > backup.sql
```

## 📈 Monitoring Best Practices

### **Regular Checks**
1. **Daily**: Check today's activity
2. **Weekly**: Review user engagement
3. **Monthly**: Analyze growth and usage patterns

### **Key Metrics to Watch**
- **Active Users**: Users who logged meals recently
- **Retention**: Users returning after first use
- **Engagement**: Average meals per user per day
- **Data Quality**: Meals with reasonable calorie estimates

### **Troubleshooting**
```bash
# Check database integrity
sqlite3 mealmetrics.db "PRAGMA integrity_check;"

# Check database size
ls -lh mealmetrics.db

# Optimize database
sqlite3 mealmetrics.db "VACUUM;"
```

## 🚀 Quick Start

1. **Navigate to MealMetrics directory**
   ```bash
   cd /path/to/MealMetrics
   ```

2. **Run quick check**
   ```bash
   # Windows
   check_users.bat
   
   # Linux/Mac
   ./check_users.sh
   ```

3. **View results**
   - See all users and their activity
   - Check today's meal logging
   - Monitor database health

## 📝 Example Use Cases

### **Check if bot is working**
```bash
python quick_db_check.py
# Look for recent activity and new users
```

### **Monitor user engagement**
```bash
python check_all_users.py
# Check activity status and meal logging patterns
```

### **Export data for analysis**
```bash
python check_all_users.py --export data.json
# Analyze data in external tools
```

### **Database maintenance**
```bash
sqlite3 mealmetrics.db "VACUUM;"
# Optimize database performance
```

---

**These tools help you maintain a healthy, active MealMetrics bot with proper user engagement monitoring!** 📊🤖
