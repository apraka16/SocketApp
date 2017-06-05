from channels.routing import route
from chat.consumers import ws_disconnect, ws_connect, ws_message, msg_consumer


channel_routing = [
    route("websocket.connect", ws_connect),
    route("websocket.receive", ws_message),
    route("websocket.disconnect", ws_disconnect),
    route("chat-messages", msg_consumer),
]

