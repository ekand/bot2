# [dev]
DEV_MODE = True  # set False for production
LOAD_DEBUG_COMMANDS = True  # set False for production.
# Alternately, if DEV_MODE is False, no need to specify the rest of the dev section
DEV_GUILD_ID = 123456798
DEV_CHANNEL_ID = 987654321
DEV_USER_ID = 123456789
# [general]
USE_SENTRY = False  # set True for production
DELETE_UNUSED_APPLICATION_CMDS = False  # Set True temporarily, as needed
SYNC_INTERACTIONS = True  # todo research whether this is needed
ACTIVITY = "interactions.py"  # "Playing <ACTIVITY>"
MONGO_MODE = 'atlas'  # localhost or atlas
MONGO_COLLECTIONS = [
    "birthdayCollection",
    "server_birthday_event_opt_in_collection",
]

# [feature_flags]
# Enable or disable features
# True: enabled
# False: disabled
FEATURE_FLAGS = {
    "birthday_event": True,
    "code_quote": True,
    "error": True,
    "hello_cam": True,
    "latency": True,
    "meeting_scheduler": False,
    "ping": True,
    "roles": False,
    "sleepy": False,
    "time_passed": False,
}
