# Bot to handle file attachments sent through teams

from datetime import datetime
import os

import requests  # http requests
from botbuilder.core import TurnContext, MessageFactory
from botbuilder.core.teams import TeamsActivityHandler
from botbuilder.schema import (
    Activity,
    ChannelAccount,
    ActivityTypes,
    ConversationAccount,  # account within a channel
    Attachment,
)

from botbuilder.schema.teams import (
    FileDownloadInfo,
    FileConsentCard,
    FileConsentCardResponse,
    FileInfoCard,
)
from botbuilder.schema.teams.additional_properties import ContentType

# bot class for file uplaods with teams
class TeamsFileUploadBot(TeamsActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        # in this case, send message download to OneDrive
        message_with_file_download = (
            False
            if not turn_context.activity.attachments
            else turn_context.activity.attachments[0].content_type == ContentType.FILE_DOWNLOAD_INFO
        )

        if message_with_file_download:
            # save file locally
            file = turn_context.activity.attachments[0]
            file_download = FileDownloadInfo.deserialize(file.content)
            file_path = "files/" + file.name

            response = requests.get(file_download.download_url, allow_redirects=True)

            open(file_path, "wb").write(response.content)

            reply = self._create_reply(
                turn_context.activity, f"Complete downloading <b>{file.name}</b>", "xml"
            )

            await turn_context.send_activity(reply)
        else:
            # message was not an attachment

            # send user a message that uploadBot function is to upload, otherwise, say end or stop to go back to orchestrator

            reply = MessageFactory.text("I can recieve attachments and send them to Sharepoint. \n If you need other assistance, you can say 'end' or 'stop'.")
            # TODO: create reply method?

            await turn_context.send_activities(reply)

    async def _send_file_card(
        self, turn_context: TurnContext, filename: str, file_size: int
    ):
        """
        Send a filecard to get permission from user to upload the file.
        """

    def _create_reply(self, activity, text=None, text_format=None):
        return Activity(
            type=ActivityTypes.message,
            timestamp=datetime.utcnow(),
            from_property=ChannelAccount(
                id=activity.recipient.id, name=activity.recipient.name
            ),
            recipient=ChannelAccount(
                id=activity.from_property.id, name=activity.from_property.name
            ),
            reply_to_id=activity.id,
            service_url=activity.service_url,
            channel_id=activity.channel_id,
            conversation=ConversationAccount(
                is_group=activity.conversation.is_group,
                id=activity.conversation.id,
                name=activity.conversation.name,
            ),
            text=text or "",
            text_format=text_format or None,
            locale=activity.locale,
        )

