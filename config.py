# config info

import os
from typing import Dict
from botbuilder.core.skills import BotFrameworkSkill


class DefaultConfig:
    """ Bot configuration """

    PORT = 3980
    APP_ID = os.environ.get(
        "MicrosoftAppID", "35cdaeee-82e0-4f6b-b8b6-48700fc5acfb"
        # SimpleRootBot
    )

    APP_PASSWORD = os.environ.get(
        "MicrosoftAppPassword", "l1TBRXA96Ik29Sp~_49hcr8GDD8n-3J~PO"
        # SimpleRootBot
    )

    # let's make it so that all bot skills are hosted off this endpoint
    SKILL_HOST_ENDPOINT = "https://botskills.troykirin.io/api/skills"

    # list of skills bot is allowed to do
    SKILLS = [
        {
            "id": "EchoBotSkill",
            "app_id": "fddbb187-b979-43a7-aa9a-4630c931184c",
            "skill_endpoint": "https://botskills.troykirin.io/api/messages"
        },
    ]
    # Skill callers to those specified, "*" allows any caller
    # Ex: os.environ.get("AllowedCallers", ["54d3bb6a-3b6d-4ccd-bbfd-cad5c72fb53a"])
    ALLOWED_CALLERS = os.getiron.get("AllowedCallers", ["*"])


class SkillConfig:
    SKILL_HOST_ENDPOINT = DefaultConfig.SKILL_HOST_ENDPOINT
    SKILLS: Dict[str, BotFrameworkSkill] = {
        skill["id"]: BotFrameworkSkill(**skill) for skill in DefaultConfig.SKILLS
    }
