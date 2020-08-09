

class ConversationData:
    def __init__(
        self,
        user_id: str = None,
        channel_id: str = None,
        timestamp: str = None,
        prompted_for_username: bool = False
    ):
        self.user_id = user_id
        self.channel_id = channel_id
        self.timestamp = timestamp
        self.prompted_for_username = prompted_for_username
        super().__init__()