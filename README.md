# [PyIEC61850_Telebot](https://github.com/muflihnurfaizi/PyIEC61850_Telebot) &middot; ![GitHub license](https://img.shields.io/github/license/muflihnurfaizi/PyIEC61850_Telebot.svg)

PyIEC61850_Telebot is a Python-based program designed to fetch data from Intelligent Electronic Devices (IEDs) in substations using the IEC 61850 protocol. It connects to IEDs through the [libIEC61850 library](https://github.com/mz-automation/libiec61850?tab=readme-ov-file) , compiled with slight modifications for Python. The Telegram bot functionality is built using the [python-telegram-bot library](https://github.com/python-telegram-bot/python-telegram-bot). The system has been tested and successfully implemented on a Raspberry Pi 4.

[Learn how to modified and compile the libIEC61850](https://react.dev/learn).

## Installation

PyIEC61850_Telebot is designed for ease of use, but there are a few initial setup steps:

    1. Compile libIEC61850 with Python to make its functions usable.
    2. Create a config.json file in the project to store configurations.
    3. Set up databaseIED.json and databaseBCU.json to store IED databases.
    4. Install the required modules for PyIEC61850_Telebot.py using pip.
    5. Run PyIEC61850_Telebot.py to get started.

This process ensures smooth interaction with your IEDs!

## Documentation

config.json, **for Telegram Bot TOKEN**

```json
{
  "TELEGRAM_BOT_TOKEN": "xxxxxx"
}
```

databaseIED.json, **for IED's IP and Directory files**

```json
{
  "BAY1": {
    "IED1": {
      "Ied_IP": "192.16.1.12",
      "Ied_Dir": "/COMTRADE"
    },
    "IED2": {
      "Ied_IP": "192.16.1.11",
      "Ied_Dir": "/COMTRADE"
    }
  },
  "BAY2": {
    "IED1": {
      "Ied_IP": "192.16.1.22",
      "Ied_Dir": "/COMTRADE"
    },
    "IED2": {
      "Ied_IP": "192.16.1.21",
      "Ied_Dir": "/COMTRADE"
    }
  }
}
```

databaseBCU.json, **for IED's IP and metering LN**

```json
{
  "BAY1": {
    "BCU": {
      "Ied_IP": "192.16.1.12",
      "LN": "/MEASUREMENTS/A"
    }
  },
  "BAY2": {
    "BCU": {
      "Ied_IP": "192.16.1.22",
      "Ied_Dir": "/MEASUREMENTS/A"
    }
  }
}
```

## Contributing

The primary goal of this repository is to advance this technology, making tasks with IEDs and IEC 61850 easier. For those interested in providing feedback or contributing, feel free to reach out via email to [Muflih](nurfaizimuflih10@gmail.com).

## License

This project is licensed under the terms of the GNU General Public License v3.0. You can view the full license in the [LICENSE](LICENSE) file or at <http://www.gnu.org/licenses/>.
