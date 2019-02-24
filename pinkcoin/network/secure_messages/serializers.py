"""
Serializers for secure messages.
"""

from ..base_serializer import Serializer, SerializableMessage
# from .. import data_fields


class SecureMessagesInventory(SerializableMessage):
    """
    The Secure Message Inventory representation.
    """
    def __init__(self):
        pass

class SecureMessagesInventorySerializer(Serializer):
    """
    The serializer for the Secure Message Inventory.
    """
    model_class = SecureMessagesInventory


class SecureMessagesPing(SerializableMessage):
    """
    The secure messages ping command, which should always be
    answered with a Pong.
    """
    command = "smsgPing"

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

class SecureMessagesPingSerializer(Serializer):
    """
    The secure messages ping command serializer.
    """
    model_class = SecureMessagesPing

class SecureMessagesPong(SerializableMessage):
    """
    The secure messages pong command, usually returned
    when a ping command arrives.
    """
    command = "smsgPong"

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

class SecureMessagePongSerializer(Serializer):
    """
    The secure messages pong command serializer.
    """
    model_class = SecureMessagesPong
