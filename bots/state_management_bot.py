# State management bot object
class StateManagementBot(ActivityHandler):
    # params of conversation state and user state when instantiated
    def __init__(self, conversation_state: ConversationState, user_state: UserState):
        if conversation_state is None:
            # throw error
            raise TypeError(
                "[StateManagementBot]: Missing parameter. conversation_state is required but None was given"
            )
        if user_state is None:
            # throw error
            raise TypeError(
                "[StateManagementBot]: Missing parameter. user_state is required but None was given"
            )
        self.conversation_state = conversation_state
        self.user_state = user_state
