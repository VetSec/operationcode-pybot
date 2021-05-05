import json
from time import time
from typing import List

from pybot.endpoints.slack.utils import MODERATOR_CHANNEL

TICKET_OPTIONS = {
    "notStarted": "Not Started",
    "inProgress": "In-progress",
    "waitingOnUser": "Waiting on User",
    "rejected": "Rejected",
    "duplicate": "Mark as Duplicate",
    "complete": "Complete",
}


def now():
    """
    This has to be pulled out into its own method so a mock can
    be injected for testing purposes
    """
    return int(time())


def base_response(action):
    response = {
        "text": action["original_message"].get("text", None),
        "channel": action["channel"]["id"],
        "ts": action["message_ts"],
    }
    return response


def update_ticket_message(action, selected_value):
    user = action["user"]["id"]
    update_message = (
        f"<@{user}> updated status to {selected_value} at "
        f"<!date^{now()}^{{date_num}} {{time_secs}}|Failed to parse time>"
    )
    return {
        "text": update_message,
        "channel": action["channel"]["id"],
        "thread_ts": action["message_ts"],
    }


def updated_ticket_status(action):
    selected_option = action["actions"][0]["selected_options"][0]
    selected_option["text"] = TICKET_OPTIONS[selected_option["value"]]

    updated_attachments = action["original_message"]["attachments"]
    updated_attachments[0]["actions"][0]["selected_options"] = [selected_option]
    response = {**base_response(action), "attachments": updated_attachments}
    return response, selected_option


def ticket_attachments(action):
    user_id = action["user"]["id"]
    request_type = action["submission"]["type"]
    email = action["submission"]["email"]
    details = action["submission"]["details"]
    attachments = [
        {
            "text": "",
            "callback_id": "ticket_status",
            "response_type": "in_channel",
            "fallback": "request details should have been here",
            "fields": [
                {"title": "User", "value": f"<@{user_id}>", "short": True},
                {"title": "Email", "value": f"{email}", "short": True},
                {"title": "Request Type", "value": f"{request_type}", "short": True},
                {"title": "Details", "value": f"{details}", "short": True},
            ],
            "actions": [
                {
                    "name": "status",
                    "text": "Current Status",
                    "type": "select",
                    "selected_options": [
                        {"text": "Not Started", "value": "notStarted"}
                    ],
                    "options": [
                        {"text": text, "value": value}
                        for value, text in TICKET_OPTIONS.items()
                    ],
                }
            ],
        },
        not_claimed_attachment(),
    ]
    return attachments


def greeted_attachment(user_id: str) -> List[dict]:
    return [
        {
            "text": f":100:<@{user_id}> has greeted the new user!:100:\n"
            f"<!date^{now()}^Greeted at {{date_num}} {{time_secs}}|Failed to parse time>",
            "fallback": "",
            "color": "#3AA3E3",
            "callback_id": "greeted",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "reset_greet",
                    "text": "Reset claim",
                    "type": "button",
                    "style": "danger",
                    "value": "reset_greet",
                }
            ],
        }
    ]


def not_greeted_attachment():
    return [
        {
            "text": "",
            "fallback": "Someone should greet them!",
            "color": "#3AA3E3",
            "callback_id": "greeted",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "greeted",
                    "text": "I will greet them!",
                    "type": "button",
                    "style": "primary",
                    "value": "greeted",
                }
            ],
        }
    ]


def direct_messaged_attachment(user_id: str) -> List[dict]:
    return [
        {
            "text": f":100:<@{user_id}> has DMed the new user!:100:\n"
            f"<!date^{now()}^DMed at {{date_num}} {{time_secs}}|Failed to parse time>",
            "fallback": "",
            "color": "#3AA3E3",
            "callback_id": "messaged",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "reset_message",
                    "text": f"Reset DM",
                    "type": "button",
                    "style": "danger",
                    "value": "reset_message",
                }
            ],
        }
    ]


def not_direct_messaged_attachment():
    return [
        {
            "text": "",
            "fallback": "Someone should DM them!",
            "color": "#3AA3E3",
            "callback_id": "messaged",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "messaged",
                    "text": "I will DM them!",
                    "type": "button",
                    "style": "primary",
                    "value": "messaged",
                }
            ],
        }
    ]


def not_claimed_attachment():
    return {
        "text": "",
        "fallback": "not claimed attachment",
        "color": "#3AA3E3",
        "callback_id": "claimed",
        "attachment_type": "default",
        "short": True,
        "actions": [
            {
                "name": "claimed",
                "text": "Claim",
                "type": "button",
                "style": "primary",
                "value": "claimed",
            }
        ],
    }


def claimed_attachment(user_id):
    return {
        "text": f"Claimed by <@{user_id}>\n"
        f"<!date^{now()}^Claimed at {{date_num}} {{time_secs}}|Failed to parse time>",
        "fallback": "",
        "color": "#3AA3E3",
        "callback_id": "claimed",
        "attachment_type": "default",
        "actions": [
            {
                "name": "reset_claim",
                "text": "Reset claim",
                "type": "button",
                "style": "danger",
                "value": "reset_claim",
            }
        ],
    }


def reset_greet_message(user_id):
    return (
        f"Reset by <@{user_id}> at"
        f" <!date^{now()}^ {{date_num}} {{time_secs}}|Failed to parse time>"
    )


def suggestion_dialog(trigger_id):
    return {
        "callback_id": "suggestion_modal",
        "title": "Help topic suggestion",
        "submit_label": "Submit",
        "trigger_id": trigger_id,
        "elements": [
            {
                "type": "text",
                "label": "Suggestion",
                "name": "suggestion",
                "placeholder": "Underwater Basket Weaving",
            }
        ],
    }


def report_dialog(action):
    trigger_id = action["trigger_id"]

    user = action["message"].get("user") or action["message"].get(
        "username"
    )  # for bots
    message_data = {
        "text": action["message"]["text"],
        "user": user,
        "channel": action["channel"],
    }
    return {
        "callback_id": "report_dialog",
        "state": json.dumps(message_data),
        "title": "Report details",
        "submit_label": "Submit",
        "trigger_id": trigger_id,
        "elements": [
            {
                "type": "textarea",
                "label": "Details",
                "name": "details",
                "placeholder": "",
                "required": False,
            }
        ],
    }


def build_report_message(slack_id, details, message_details):
    message = f"<@{slack_id}> sent a report with details: {details}"

    attachment = [
        {
            "fields": [
                {
                    "title": "User",
                    "value": f"<@{message_details['user']}>",
                    "short": True,
                },
                {
                    "title": "Channel",
                    "value": f"<#{message_details['channel']['id']}|{message_details['channel']['name']}>",
                    "short": True,
                },
                {"title": "Message", "value": message_details["text"], "short": False},
            ]
        },
        not_claimed_attachment(),
    ]

    return {"text": message, "channel": MODERATOR_CHANNEL, "attachments": attachment}


def mentor_details_dialog(action, cur_details):
    trigger_id = action["trigger_id"]
    ts = action["message"]["ts"]

    return {
        "callback_id": "mentor_details_submit",
        "state": json.dumps({"ts": ts, "channel": action["channel"]["id"]}),
        "title": "Additional Details",
        "submit_label": "Submit",
        "trigger_id": trigger_id,
        "elements": [
            {
                "type": "textarea",
                "label": "Details",
                "name": "details",
                "placeholder": "",
                "required": False,
                "value": cur_details,
            }
        ],
    }


def new_suggestion_text(user_id: str, suggestion: str) -> str:
    return f":exclamation:<@{user_id}> just submitted a suggestion for a help topic:exclamation:\n-- {suggestion}"


HELP_MENU_RESPONSES = {
    "slack": "Slack is an online chatroom service that the VetSec community uses.\n"
    "It can be accessed online, via https://vetsec.slack.com/ or via\n"
    "desktop or mobile apps, located at https://slack.com/downloads/. In addition to\n"
    "chatting, Slack also allows us to share files, audio conference and even program\n"
    "our own bots! Here are some tips to get you started:\n"
    "  - You can customize your notifications per channel by clicking the gear to the\n"
    "    left of the search box\n"
    "  - Join as many channels as you want via the + next to Channels in the side bar.",
    "python": "Python is a widely used high-level programming language used for general-purpose programming.\n"
    "It's very friendly for beginners and is great for everything from web development to \n"
    "data science.\n\n"
    "Here are some python resources:\n"
    "    VetSec Programming Room: <#CEJ1U2N5T|programming>\n"
    "    Python's official site: https://www.python.org/\n"
    "    Learn Python The Hard Way: https://learnpythonthehardway.org/book/\n"
    "    Automate The Boring Stuff: https://automatetheboringstuff.com/",
    "mentor": "The VetSec mentorship program aims to pair you with an experienced professional in order to"
    " further your Cyber or career goals. When you sign up for our mentorship program you'll fill"
    " out a form with your interests. You'll then be paired up with an available mentor that best meets"
    " those interests.\n\n"
    "If you're interested in getting paired with a mentor, please fill out our sign up form"
    " here: #Need Link Here.\n    ",                                                        ## Need link to mentoree page
    "javascript": "Javascript is a high-level programming language used for general-purpose programming.\n"
    "In recent years it has exploded in popularity and with the popular node.js runtime\n"
    "environment it can run anywhere from the browser to a server.\n\n"
    "Here are some javascript resources:\n    Operation Code Javascript Room: <#C04CJ8H2S|javascript>\n"
    "    Javascript Koans: https://github.com/mrdavidlaing/javascript-koans\n"
    "    Eloquent Javascript: http://eloquentjavascript.net/\n"
    "    Node School: http://nodeschool.io/\n"
    "    Node University: http://node.university/courses",
    "ruby": "Ruby is one of the most popular languages to learn as a beginner.\n"
    "While it can be used in any situation it's most popular for it's\n"
    "web framework 'Rails' which allows people to build websites quickly \n"
    "and easily.\n\n"
    "Here are some ruby resources:\n"
    "    VetSec Programming Room: <#CEJ1U2N5T|programming>\n"
    "    Try Ruby Online: http://tryruby.org/\n"
    "    Learn Ruby The Hard Way: http://ruby.learncodethehardway.org/book\n"
    "    Learn To Program: http://pine.fm/LearnToProgram/\n"
    "    Ruby Koans: http://rubykoans.com/",
}
