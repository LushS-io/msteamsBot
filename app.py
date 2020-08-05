# Main app begins app
# references rootBot to hand off skills to other bots

# import for async functionality
import asyncio

from adapters import ConsoleAdapter # bot console functionality
# teamsAdapter

# Import Bots
from bots import EchoBot # echoBot
from bots import RootBot
# attachmentBot
# authBot
# dialogBot
# proactiveBot
# teamsFileBot
# sharepointBot
# msGraphBot
# telegramBot
# helpdeskBot

# Create adapters
# multi adapter approach, function on console, web app, teams
CONSOLE_ADAPTER = ConsoleAdapter()
# Web adapter
# Teams adapter

# Create bot
# Root bot references mutli skills
BOT = RootBot()

# Start async loop for continued bot conversation
LOOP = asyncio.get_event_loop()

if __name__ == "__main__":
    try:
        # Greet user, give introduction
        print("Hi I'm SpurBot, I have many skills. Choose from list which one you would like to see.")

        LOOP.run_until_complete(CONSOLE_ADAPTER.process_activity(BOT.on_turn))
    except KeyboardInterrupt:
        pass
    finally:
        LOOP.stop()
        LOOP.close()



