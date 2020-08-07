

# The root bot / consumer skill bot that will call other bots depending on
# user response.
from typing import List

from botbuilder.core import(
    ActivityHandler,
    ConversationState,
    MessageFactory,
    TurnContext,
    CardFactory
)

from botbuilder.core.skills import BotFrameworkSkill
from botbuilder.schema import(
    ActivityTypes,
    ChannelAccount,
    HeroCard,
    CardAction,
    ActionTypes
)
from botbuilder.integration.aiohttp.skills import SkillHttpClient  # skill to speak to web client via http

# ---- Dialogs ----
from botbuilder.dialogs import Dialog

from config import DefaultConfig, SkillConfiguration


# variable to hold the active skill
ACTIVE_SKILL_PROPERTY_NAME = "activeSkillProperty"
TARGET_SKILL_ID = "RootBot"


# Different than TeamsActivityHandler
class RootBot(ActivityHandler):
    def __init__(
        self,
        conversation_state: ConversationState,
        skills_config: SkillConfiguration,
        skill_client: SkillHttpClient,
        config: DefaultConfig,
        dialog: Dialog
    ):
        # instantiate class variables
        self._bot_id = config.APP_ID
        self._skill_client = skill_client
        self._skills_config = skills_config
        self._conversation_state = conversation_state
        self._active_skill_property = conversation_state.create_property(
            ACTIVE_SKILL_PROPERTY_NAME
        )

    async def on_turn(self, turn_context):
        # Forward all activities except EndOfConversation to active skill
        if turn_context.activity.type != ActivityTypes.end_of_conversation:  # if activity is not end of converysation
            active_skill: BotFrameworkSkill = await self._active_skill_property.get(turn_context)

            if active_skill:
                # if active skill is true, meaning there is an active skill then forward activity to it
                await self.__send_to_skill(turn_context, active_skill)
                return
        await super().on_turn(turn_context)  # inherit the context from previous turn

    async def on_message_activity(self, turn_context: TurnContext):
        TARGET_SKILL_ID = "RootBot"

        if "EchoSkillBot" in turn_context.activity.text:
            # Begin forwarding Activities to the skill
            await turn_context.send_activity(
                MessageFactory.text("Got it, connecting you to the skill ...")
            )

            TARGET_SKILL_ID = "EchoSkillBot"
            # SET skill to the target skill going for
            skill = self._skills_config.SKILLS[TARGET_SKILL_ID]
            # save active skill in state
            await self._active_skill_property.set(turn_context, skill)

            # Send the activity to the skill
            await self.__send_to_skill(turn_context, skill)

        if "TeamsFileBot" in turn_context.activity.text:
            await turn_context.send_activity(
                MessageFactory.text("Okay, connecting you with TeamsUploadBot...")
            )
            TARGET_SKILL_ID = "TeamsFileBot"
            skill = self._skills_config.SKILLS[TARGET_SKILL_ID]

            # save active skill in state
            await self._active_skill_property.set(turn_context, skill)

            # Send the activity to the skill
            await self.__send_to_skill(turn_context, skill)

        if "AttachmentBot" in turn_context.activity.text:
            await turn_context.send_activity(
                MessageFactory.text("Okay, connecting you to AttachmentBot... ")
            )

            TARGET_SKILL_ID = "AttachmentBot"
            skill = self._skills_config.SKILLS[TARGET_SKILL_ID]
            await self.__send_to_skill(turn_context, skill)

        else:
            # just respond
            # if text sent is not one of the bots name from list

            if turn_context.activity.text != TARGET_SKILL_ID:
                await turn_context.send_activity(
                    MessageFactory.text(
                        "I'm just the orchestrator bot." +
                        "Say a \"skill\" and I'll patch you through"
                    )
                )
                await self._display_options(turn_context)

    async def on_end_of_conversation_activity(self, turn_context):
        # forget skill called (invocation)
        await self._active_skill_property.delete(turn_context)

        # Message to send indicating end of activity
        eoc_activity_message = f"Received {ActivityTypes.end_of_conversation}.\n\nCode: {turn_context.activity.code}"
        if turn_context.activity.text:
            eoc_activity_message = (
                eoc_activity_message + f"\n\nText: {turn_context.activity.text}"
            )

        if turn_context.activity.value:
            eoc_activity_message = (
                eoc_activity_message + f"\n\nValue: {turn_context.activity.value}"
            )

        # on the next turn send activity of the message
        # await turn_context.send_activity(eoc_activity_message)

        # back to root bot
        await turn_context.send_activity(
            MessageFactory.text(
                'Back in Orchestrator Bot. Say a "skill" and I\'ll patch you through to the bot.'
            )
        )

        # resend hero card
        await self._display_options(turn_context)

        await self._conversation_state.save_changes(turn_context, force=True)

    # members added is a list of channel accounts
    async def on_members_added_activity(
        self, members_added: List[ChannelAccount], turn_context: TurnContext
    ):
        # Check member against current member list
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    MessageFactory.text("Hello and Welcome!")  # say greeting
                )
                await self._display_options(turn_context)

    async def _display_options(self, turn_context: TurnContext):
        """
        Create a HeroCard with options for the user to interact with the bot.
        :param turn_context:
        :return:
        """

        # Note that some channels require different values to be used in order to get buttons to display text.
        # In this code the emulator is accounted for with the 'title' parameter, but in other channels you may
        # need to provide a value for other parameters like 'text' or 'displayText'.

        await turn_context.send_activity(
            MessageFactory.text("I can do a couple things...")
        )

        await turn_context.send_activity(
            MessageFactory.text("Don't worry I'm still learning and growing!")
        )

        await turn_context.send_activity(
            MessageFactory.text("One of my friends can echo what you say, it's kind of neat...")
        )

        await turn_context.send_activity(
            MessageFactory.text("If you are using Teams on a Mac, PC, or the Web App you can send my buddy John an attachment. He will get that to Sharepoint for you!")
        )

        await turn_context.send_activities(
            [
                MessageFactory.text("Also..."),
                MessageFactory.text("If you happen to be talking to me from a web app or Telegram...my good friend Sophie can assist you."),
                MessageFactory.text("She can also move files into Sharepoint!")
            ]
        )

        card = HeroCard(
            text="Who would you like to speak to?",
            buttons=[
                CardAction(
                    type=ActionTypes.im_back, title="Echo", value="EchoSkillBot"
                ),
                CardAction(
                    type=ActionTypes.im_back, title="John", value="TeamsFileBot"
                ),
                CardAction(
                    type=ActionTypes.im_back, title="Sophie", value="AttachmentBot"
                ),
            ],
        )

        reply = MessageFactory.attachment(CardFactory.hero_card(card))
        await turn_context.send_activity(reply)

    async def _display_end_skill(self, turn_context: TurnContext):
        card = HeroCard(
            text="Are you done using skill?, otherwise continue...",
            buttons=[
                CardAction(
                    type=ActionTypes.im_back, title="End Skill",
                    value="end"
                ),
            ]
        )

    async def __send_to_skill(
        self, turn_context: TurnContext, target_skill: BotFrameworkSkill
    ):
        # note: always save changes before calling a skill so that any activity generate by the skill
        # will have access to current accurate state

        await self._conversation_state.save_changes(turn_context, force=True)

        # route the activity to the skill
        await self._skill_client.post_activity_to_skill(
            self._bot_id,
            target_skill,
            self._skills_config.SKILL_HOST_ENDPOINT,
            turn_context.activity,
        )
