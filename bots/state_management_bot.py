import asyncio

from botbuilder.core import(
    ActivityHandler,
    TurnContext,
    ConversationState,
    UserState,
    MessageFactory
)

from botbuilder.schema import (
    HeroCard
)

from storage.conversation_data import ConversationData
from storage.user_profile import UserProfile


# A State management bot
class StateManagementBot(ActivityHandler):
    # On creation, ask for the conversation_state and user_state
    def __init__(self, conversation_state: ConversationState, user_state: UserState):
        # Missing conversation_state
        if conversation_state is None:
            # throw error msg
            raise TypeError(
                "[StateManagementBot]: Missing parameter. conversation_state is required but None was given"
            )
        if user_state is None:
            # throw error msg
            raise TypeError(
                "[StateManagementBot]: Missing parameter. user_state is required but None was given"
            )
        # create object member variables
        self.conversation_state = conversation_state
        self.user_state = user_state

        # create object member accessing functions
        self.conversation_state_accessor = self.conversation_state.create_property("ConversationData")

        self.user_profile_accessor = self.user_state.create_property("UserProfile")

    # Member function: when bot receives any activity
    async def on_message_activity(self, turn_context: TurnContext):
        # get the user profile and conversation data
        user_profile = await self.user_profile_accessor.get(turn_context, UserProfile)
        conversation_data = await self.conversation_state_accessor.get(turn_context, ConversationData)

        # no userProfile name detected
        if user_profile.name is None:

            # if prompt for username has not been made
            if conversation_data.prompted_for_username is False:
                # have bot send message asking for name
                await turn_context.send_activity(
                    f"What shall I call you?"
                )
                # change conversation data flag, prompting for username to True
                conversation_data.prompted_for_username = True

            # bot does see a username
            else:
                # look at incoming activity text, save name
                user_profile.name = turn_context.activity.text

                # awknowledge name received
                await turn_context.send_activity(
                    MessageFactory.text(f"{user_profile.name}, \n What a wonderful name!")
                )

        # Bot has a name to work with
        else:
            # Add message details to the conversation data.
            conversation_data.timestamp = self.__datetime_from_utc_to_local(
                turn_context.activity.timestamp
            )
            conversation_data.channel_id = turn_context.activity.channel_id

            # Display state data.
            await turn_context.activity(
                f"{user_profile.name} sent {turn_context.activity.text}"
            )
            await turn_context.activity(
                f"Message received at: {conversation_data.timestamp}"
            )
            await turn_context.activity(
                f"Message received from: {conversation_data.channel_id}"
            )

    # on every turn, do the following
    async def on_turn(self, turn_context: TurnContext):
        # inherit everything from the turn_context
        await super().on_turn(turn_context)

        # save conversation state
        await self.conversation_state.save_changes(turn_context)
        # save user_state
        await self.user_state.save_changes(turn_context)
