import json

from twin import calcom, pushover

TOOL_SCHEMAS = [
    {
        "name": "list_available_slots",
        "description": (
            "Look up available 15-minute slots on Jean's calendar. "
            "Call this when the visitor wants to book a call. "
            "Returns a list of upcoming open slots. Present 3-5 of them "
            "to the visitor and let them pick one before calling create_booking."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "days_ahead": {
                    "type": "integer",
                    "description": "How many days into the future to search (default 14, max 30).",
                    "minimum": 1,
                    "maximum": 30,
                },
                "timezone": {
                    "type": "string",
                    "description": (
                        "IANA timezone name to display slots in, e.g. 'America/New_York', "
                        "'Europe/Paris', 'Asia/Tokyo'. Ask the visitor for their timezone "
                        "if you don't know it. Default 'UTC' if truly unknown."
                    ),
                },
            },
            "required": ["timezone"],
        },
    },
    {
        "name": "send_notification",
        "description": (
            "Send a Pushover notification to Jean (the real person, on her phone) to let her know "
            "something interesting happened in this chat. Use this when: "
            "(a) a visitor shows up and sent their first message, so Jean knows someone is there, "
            "(b) a visitor shares their email and gives consent for Jean to follow up,"
            "(c) a booking has just been created (send a short summary),  "
            "Do NOT send for trivial chitchat or every turn — be selective. "
            "Always include the visitor's name and email in the message if you have them."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The notification body. 1-3 sentences. Include name/email/context.",
                },
                "title": {
                    "type": "string",
                    "description": "Short title for the notification, e.g. 'New booking', 'Lead captured', 'Interesting chat'. Default 'Digital Twin'.",
                },
            },
            "required": ["message"],
        },
    },
    {
        "name": "create_booking",
        "description": (
            "Book a confirmed 15-minute call on Jean's calendar. "
            "Only call this AFTER the visitor has chosen a specific slot from list_available_slots "
            "AND you have confirmed their name, email, and the slot back to them. "
            "Cal.com sends both the visitor and Jean a confirmation email automatically."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "start_iso": {
                    "type": "string",
                    "description": "ISO-8601 start time of the chosen slot, exactly as returned by list_available_slots.",
                },
                "invitee_name": {
                    "type": "string",
                    "description": "Visitor's full name.",
                },
                "invitee_email": {
                    "type": "string",
                    "description": "Visitor's email address. Must be a valid email — they'll receive the calendar invite here.",
                },
                "timezone": {
                    "type": "string",
                    "description": "Visitor's IANA timezone, same one used for list_available_slots.",
                },
                "topic": {
                    "type": "string",
                    "description": "Short summary of what the visitor wants to discuss. Helps Jean prepare.",
                },
            },
            "required": ["start_iso", "invitee_name", "invitee_email", "timezone"],
        },
    },
]


def _run_list_available_slots(args: dict) -> str:
    timezone = args.get("timezone", "UTC")
    days_ahead = args.get("days_ahead", 14)
    try:
        slots = calcom.list_available_slots(
            days_ahead=days_ahead,
            timezone_name=timezone,
            max_slots=10,
        )
    except calcom.CalComError as e:
        return json.dumps({"error": str(e), "fallback_url": calcom.public_booking_url()})

    return json.dumps({
        "timezone": timezone,
        "slots": slots,
        "count": len(slots),
        "fallback_url": calcom.public_booking_url(),
    })


def _run_create_booking(args: dict) -> str:
    try:
        booking = calcom.create_booking(
            start_iso=args["start_iso"],
            invitee_name=args["invitee_name"],
            invitee_email=args["invitee_email"],
            timezone_name=args.get("timezone", "UTC"),
            topic=args.get("topic", ""),
        )
    except calcom.CalComError as e:
        return json.dumps({
            "error": str(e),
            "fallback_url": calcom.public_booking_url(),
            "message": "Booking failed. Offer the visitor the fallback URL so they can book manually.",
        })
    except KeyError as e:
        return json.dumps({"error": f"Missing required argument: {e}"})

    return json.dumps({
        "success": True,
        "booking": booking,
        "message": (
            "Booking confirmed. A confirmation email with the meeting link has been sent "
            "to the visitor's email. Jean has been notified."
        ),
    })


def _run_send_notification(args: dict) -> str:
    message = args.get("message", "").strip()
    if not message:
        return json.dumps({"error": "Notification message is empty."})
    title = args.get("title") or "Digital Twin"
    try:
        pushover.send_notification(message, title=title)
    except pushover.PushoverError as e:
        return json.dumps({"error": str(e)})
    return json.dumps({"success": True, "delivered": True})


DISPATCH = {
    "list_available_slots": _run_list_available_slots,
    "create_booking": _run_create_booking,
    "send_notification": _run_send_notification,
}


def run_tool(name: str, args: dict) -> str:
    handler = DISPATCH.get(name)
    if handler is None:
        return json.dumps({"error": f"Unknown tool: {name}"})
    return handler(args)
