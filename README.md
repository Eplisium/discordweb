# DiscordWeb Bot

## Overview

DiscordWeb Bot is designed to display Discord user information and recent activity in a web interface. Although development has ended, you can still set it up and customize it for your own server.

## Features

- Display Discord users
- Show recent activity
- User-friendly web interface

## Setup Instructions

### Prerequisites

- Python 3.7+
- `discord.py` library

### Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Eplisium/discordweb
   cd impactweb
   ```

2. **Update Server ID and Get User Functions:**
   Ensure you update the server ID in the index and get users functions. Refer to the [example screenshot](https://prnt.sc/s3iMomavtSXQ).

3. **Edit Configuration:**
   Modify the `wutil/webconfig.py` file to match your settings. Refer to the [configuration screenshot](https://prnt.sc/rT4LUOOBkZfP).

4. **Run the Bot:**
   Using the `web_runner.bat` to start the bot/app. 

### Configuration

Update the `wutil/webconfig.py` file with the necessary settings:
```python
bot_token3 = '*************'  # Enter your token
client_id = ******** # Enter your client id from the O2Auth page in the discord dev page.
client_secret = "*******" # Enter your client secret from the O2Auth page in the discord dev page.
redirect_uris = [ #Set your redirects here from https://prnt.sc/Mv7x4vzUMn_N   PS. Yes I understand the typo. I've accidently done that through out the whole code.
    'http://impactdiscord.ddns.net:5000/callback',
    'http://localhost:5000/callback'
]  
```

## Usage

Once the bot is running, it will display your Discord users and their recent activity through the web interface. Navigate to `http://localhost:5000` in your browser to view the information.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License.

## Acknowledgments

- Special thanks to the contributors and the Discord.py community.

