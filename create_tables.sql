-- MealMetrics Database Schema
-- Run this SQL in phpMyAdmin to create all required tables

USE mealmetrics;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Meals table
CREATE TABLE IF NOT EXISTS meals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    image_path VARCHAR(500),
    analysis_text TEXT,
    calories DECIMAL(8,2),
    protein DECIMAL(8,2),
    carbs DECIMAL(8,2),
    fat DECIMAL(8,2),
    fiber DECIMAL(8,2),
    sugar DECIMAL(8,2),
    sodium DECIMAL(8,2),
    meal_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_meal_type (meal_type)
);

-- Daily summaries table
CREATE TABLE IF NOT EXISTS daily_summaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    date DATE NOT NULL,
    total_calories DECIMAL(8,2) DEFAULT 0,
    total_protein DECIMAL(8,2) DEFAULT 0,
    total_carbs DECIMAL(8,2) DEFAULT 0,
    total_fat DECIMAL(8,2) DEFAULT 0,
    total_fiber DECIMAL(8,2) DEFAULT 0,
    total_sugar DECIMAL(8,2) DEFAULT 0,
    total_sodium DECIMAL(8,2) DEFAULT 0,
    meal_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_date (user_id, date),
    INDEX idx_user_id (user_id),
    INDEX idx_date (date)
);

-- User goals table
CREATE TABLE IF NOT EXISTS user_goals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    daily_calories DECIMAL(8,2),
    daily_protein DECIMAL(8,2),
    daily_carbs DECIMAL(8,2),
    daily_fat DECIMAL(8,2),
    daily_fiber DECIMAL(8,2),
    daily_sugar DECIMAL(8,2),
    daily_sodium DECIMAL(8,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_goals (user_id)
);

-- Insert some sample data for testing
INSERT IGNORE INTO users (id, username, first_name, last_name) 
VALUES (123456789, 'test_user', 'Test', 'User');

-- Show tables created
SHOW TABLES;
