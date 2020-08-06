# Main app begins app
# references rootBot to hand off skills to other bots

# import for async functionality
import asyncio

# system imports
import sys
import traceback
from datetime import datetime

# Core imports
from aiohttp import web
from aiohttp.web import Request, Response
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    ConversationState,
    MemoryStorage,
    TurnContext,
    BotFrameworkAdapter,
)

# Imports for integration
from botbuilder.core.integration import (
    aiohttp_channel_service_routes,
    aiohttp_error_middleware
)

# Imports for bot skill hand off
from botbuilder.core.skills import SkillHandler
from botbuilder.schema import Activity, ActivityTypes
from botframework.connector.auth import (
    AuthenticationConfiguration,
    SimpleCredentialProvider
)
# from bots.root.root_bot import ACTIVE_SKILL_PROPERTY_NAME
# from skill_http_client import SkillHttpClient
from bots.root.skill_conversation_id_factory import SkillConversationIdFactory
from bots.authentication import AllowedSkillsClaimsValidator
from bots.root import RootBot
from config import DefaultConfig, SkillConfig

from adapters import ConsoleAdapter  # bot console functionality
# teamsAdapter

# # Import Bots
# from bots import RootBot  # rootBot to call other skills
from bots.skills import EchoBot  # echoBot
# attachmentBot
# authBot
# dialogBot
# proactiveBot
# teamsFileBot
# sharepointBot
# msGraphBot
# telegramBot
# helpdeskBot

CONFIG = DefaultConfig()
SKILL_CONFIG = SkillConfig()

# Whitelist skills from skill_config - skills allowed to be called
ALLOWED_CALLER_IDS = {s.app_id for s in [*SKILL_CONFIG.SKILLS.values()]}
CLAIMS_VALIDATOR = AllowedSkillsClaimsValidator(ALLOWED_CALLER_IDS)
AUTH_CONFIG = AuthenticationConfiguration(
    claims_validator=CLAIMS_VALIDATOR.validate_claims
)

# Create adapters
# multi adapter approach, function on console, web app, teams
CONSOLE_ADAPTER = ConsoleAdapter()

# Web adapter
SETTINGS = BotFrameworkAdapterSettings(
    app_id=CONFIG.APP_ID,
    app_password=CONFIG.APP_PASSWORD,
    auth_configuration=AUTH_CONFIG
)
WEB_ADAPTER = BotFrameworkAdapter(SETTINGS)

STORAGE = MemoryStorage()
# TODO: CosmosDB

CONVERSATION_STATE = ConversationState(STORAGE)
ID_FACTORY = SkillConversationIdFactory(STORAGE)
CREDENTIAL_PROVIDER = SimpleCredentialProvider(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
CLIENT = SkillHttpClient(CREDENTIAL_PROVIDER, ID_FACTORY)

# Teams adapter
# TODO: Teams adapter
#
#

# CATCH all for errors
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log .vs. app insights.
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    # TODO: Switch to app insights
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")
    await context.send_activity(
        "To continue to run this bot, please fix the bot source code."
    )

    # Send a trace activity if we're talking to the Bot Framework Emulator
    if context.activity.channel_id == "emulator":
        # Create a trace activity that contains the error object
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )
        await context.send_activity(trace_activity)

    # Inform the active skill that the conversation is ended so that it has
    # a chance to clean up.
    # Note: ActiveSkillPropertyName is set by the RooBot while messages are being
    # forwarded to a Skill.
    active_skill_id = await CONVERSATION_STATE.create_property(ACTIVE_SKILL_PROPERTY_NAME).get(context)
    if active_skill_id:
        end_of_conversation = Activity(
            type=ActivityTypes.end_of_conversation, code="RootSkillError"
        )
        TurnContext.apply_conversation_reference(
            end_of_conversation,
            TurnContext.get_conversation_reference(context.activity),
            is_incoming=True
        )

        await CONVERSATION_STATE.save_changes(context, True)
        await CLIENT.post_activity(
            CONFIG.APP_ID,
            SKILL_CONFIG.SKILLS[active_skill_id],
            SKILL_CONFIG.SKILL_HOST_ENDPOINT,
            end_of_conversation,
        )

    # Clear out state
    await CONVERSATION_STATE.delete(context)

WEB_ADAPTER.on_turn_error = on_error

# # Create bot
# Root bot references multi skills
BOT = RootBot(CONVERSATION_STATE, SKILL_CONFIG, CLIENT, CONFIG)

SKILL_HANDLER = SkillHandler(
    WEB_ADAPTER, BOT, ID_FACTORY, CREDENTIAL_PROVIDER, AuthenticationConfiguration()
)

# Listen for incoming responses on /api/messages
async def messages(req: Request) -> Response:
    # Main bot message handler
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=415)  # TODO: what is 415

    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    try:
        await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
        return Response(status=201)  # TODO: what is 201
    except Exception as exception:
        raise exception


APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)
APP.router.add_routes(aiohttp_channel_service_routes(SKILL_HANDLER, "/api/skills"))

# Start async loop for continued bot conversation
LOOP = asyncio.get_event_loop()

if __name__ == "__main__":
    try:
        # Greet user, give introduction
        print("Hi I'm SpurBot, I have many skills. Choose from list which one you would like to see.")

        web.run_app(APP, host="localhost", port=CONFIG.PORT)  # TODO: Change host to Azure / deploy from Raspberry Pi
    except Exception as error:
        raise error
