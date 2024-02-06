# tenki_bot

This is a simple LINE Bot that provides weather forecast information based on user input. The bot is built using the LINE Messaging API and Python.

## Features

- Retrieves weather forecast information when the user mentions "天気" or "予報."

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

5. Run the application:

```bash
python app.py
```

## Usage

- Mention "天気" or "予報" to get weather forecast information.

## Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
