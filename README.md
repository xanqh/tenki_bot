# tenki_bot

This LINE bot is designed to retrieve weather forecasts for registered locations. The bot is built using the LINE Messaging API and Python.

## How to Use

1. Please [register the BOT](https://liff.line.me/1645278921-kWRPP32q/?accountId=568bghfo).
2. Send the name of the location you want to register to the bot.
3. Send a message to the bot containing the keyword "天気"
4. The bot will respond with the weather forecast for the registered location.

## Checking the List of Registrable Locations

Sending "地域一覧" (list of regions) will display the available list of locations you can register.

## Checking How to Use

Sending "使い方" (how to use) will provide instructions on how to interact with the bot.

## Getting Started

To get started with this LINE Bot, follow these steps:

1. Clone the repository:

```bash
git clone https://github.com/xanqh/tenki_bot.git
```

2. Install the necessary dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your LINE Bot by creating a channel on the [LINE Developers Console](https://developers.line.biz/console/).

4. Set the environment variables:
- `CH_SECRET`: Your LINE Bot channel secret.
- `CH_TOKEN`: Your LINE Bot channel access token.

5. Perform a local test:

```bash
python app.py
```

6. If deploying on Heroku, create a new application, and add the access token, channel secret, and database URL to the application settings.

7. Update the settings in the code and your cloned bot is ready for use.

## Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
