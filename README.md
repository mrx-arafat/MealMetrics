# MealMetrics - AI-Powered Calorie Tracking Telegram Bot

MealMetrics is an intelligent Telegram bot that helps you track your daily calorie intake by analyzing photos of your meals. Simply send a photo of your food, and the AI will estimate the calories and give you the option to log it to your daily intake.

## Features

- 📸 **Photo Analysis**: Send meal photos for instant calorie estimation
- 🤖 **AI-Powered**: Uses Google Gemini 2.5 Flash for accurate food recognition
- ✅ **User Choice**: Log or cancel meals after review
- 📊 **Daily Tracking**: Automatic daily calorie and meal counting
- 📈 **Statistics**: View daily, weekly, and monthly summaries
- 💾 **Database Storage**: SQLite database for reliable data persistence
- 🔒 **Multi-User**: Supports multiple users with individual tracking

## How It Works

1. **Send a Photo**: Take a clear photo of your meal and send it to the bot
2. **AI Analysis**: The bot analyzes the image and estimates calories
3. **Review & Confirm**: Check the analysis and choose to log or cancel
4. **Track Progress**: View your daily intake and statistics

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (from @BotFather)
- OpenRouter API key with access to Google Gemini

### Installation

1. **Clone or download** this project to your local machine

2. **Install dependencies**:
   ```bash
   cd MealMetrics
   pip install -r requirements.txt
   ```

3. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

4. **Configure your .env file**:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   OPENROUTER_API_KEY=sk-or-v1-your_openrouter_api_key_here
   OPENROUTER_MODEL=google/gemini-2.5-flash-preview:thinking
   DATABASE_PATH=mealmetrics.db
   MAX_IMAGE_SIZE_MB=10
   SUPPORTED_IMAGE_FORMATS=jpg,jpeg,png,webp
   ```

### Getting API Keys

#### Telegram Bot Token
1. Message @BotFather on Telegram
2. Send `/newbot` and follow the instructions
3. Copy the bot token to your .env file

#### OpenRouter API Key
1. Sign up at [OpenRouter.ai](https://openrouter.ai/)
2. Go to your API Keys section
3. Create a new API key
4. Copy the key to your .env file

### Running the Bot

```bash
python main.py
```

The bot will start and display a success message. You can now interact with it on Telegram!

## Usage

### Commands

- `/start` - Initialize the bot and show welcome message
- `/help` - Show help information and tips
- `/menu` - Display the main menu
- `/today` - Show today's calorie summary
- `/stats` - View statistics options

### Basic Workflow

1. Start a conversation with your bot on Telegram
2. Send `/start` to initialize
3. Take a photo of your meal and send it
4. Wait for the AI analysis (5-10 seconds)
5. Review the estimated calories and food breakdown
6. Click "✅ Log Meal" to save or "❌ Cancel" to discard
7. View your daily progress with `/today` or `/stats`

## Tips for Better Accuracy

- **Good Lighting**: Take photos in natural or bright lighting
- **Clear View**: Include the entire meal in the frame
- **Standard Plates**: Use regular-sized plates/bowls when possible
- **Avoid Shadows**: Minimize shadows on the food
- **Multiple Angles**: For complex meals, consider taking multiple photos

## Project Structure

```
MealMetrics/
├── main.py                 # Main bot entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── README.md              # This file
├── bot/                   # Bot handlers and logic
│   ├── handlers.py        # Message and callback handlers
│   ├── keyboards.py       # Inline keyboard layouts
│   └── states.py          # Conversation states and constants
├── ai/                    # AI analysis components
│   ├── vision_analyzer.py # Food image analysis
│   └── prompts.py         # AI prompts for analysis
├── database/              # Database management
│   ├── models.py          # Database models and manager
│   └── operations.py      # Meal operations and queries
└── utils/                 # Utility functions
    ├── config.py          # Configuration management
    └── helpers.py         # Helper functions
```

## Database Schema

The bot uses SQLite with the following tables:

- **users**: User information and activity tracking
- **meals**: Individual meal records with calories and timestamps
- **daily_summaries**: Daily calorie totals and meal counts
- **pending_meals**: Temporary storage for meals awaiting confirmation

## Troubleshooting

### Common Issues

1. **Bot doesn't respond**:
   - Check your bot token in .env
   - Ensure the bot is running
   - Verify internet connection

2. **Image analysis fails**:
   - Check OpenRouter API key and credits
   - Try a clearer photo
   - Ensure image format is supported

3. **Database errors**:
   - Check file permissions in the bot directory
   - Ensure SQLite is properly installed

### Logs

The bot creates a `mealmetrics.log` file with detailed logging information to help diagnose issues.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve MealMetrics!

## License

This project is open source. Feel free to use and modify as needed.

## Disclaimer

Calorie estimates are approximations based on AI analysis of food photos. Results may vary and should not be considered as exact nutritional information. Always consult with healthcare professionals for specific dietary needs.
