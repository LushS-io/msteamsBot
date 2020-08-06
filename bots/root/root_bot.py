

# The root bot / consumer skill bot that will call other bots depending on
# user response.
from typing import List

from botbuilder.core import(
    ActivityHandler,
    ConversationState,
    MessageFactory,
    TurnContext
)

from botbuilder.core.skills import BotFrameworkSkill
from botbuilder.schema import ActivityTypes, ChannelAccount
from botbuilder.integration.aiohttp.skills import SkillHttpClient  # skill to speak to web client via http

from config import DefaultConfig, SkillConfig

# variable to hold the active skill
ACTIVE_SKILL_PROPERTY_NAME = "activeSkillProperty"
TARGET_SKILL_ID = "EchoBotSkill"


# Different than TeamsActivityHandler
class RootBot(ActivityHandler):
    def __init__(
        self,
        conversation_state: ConversationState,
        skills_config: SkillConfig,
        skill_client: SkillHttpClient,
        config: DefaultConfig,
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
        if "skill" in turn_context.activity.text:
            # Begin forwarding Activities to the skill
            await turn_context.send_activity(
                MessageFactory.text("Got it, connecting you to the skill ...")
            )

            # SET skill to the target skill going for
            skill = self._skills_config.SKILLS[TARGET_SKILL_ID]
            # save active skill in state
            await self._active_skill_property.set(turn_context, skill)

            # Send the activity to the skill
            await self.__send_to_skill(turn_context, skill)
        else:
            # just respond
            await turn_context.send_activity(
                MessageFactory.text(
                    "I'm just the orchestrator bot." +
                    "Say \"skill\" and I'll patch you through"
                )
            )

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
        await turn_context.send_activity(eoc_activity_message)

        # back to root bot
        await turn_context.send_activity(
            MessageFactory.text(
                'Back in Orchestrator Bot. Say "skill" and I\'ll patch you through to the bot.'
            )
        )

        await self._conversation_state.save_changes(turn_context, force=True)

    # members added is a list of channel accounts
    async def on_members_added_activity(
        self, members_added: List[ChannelAccount], turn_context: TurnContext
    ):
            for member in members_added:  # Check member against current member list
                if member.id != turn.context.activity.recipient.id:  # if the recipientID is not on the list then...
                    await turn_context.send_activity(
                        MessageFactory.text("Hello and Welcome!")  # say greeting
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
