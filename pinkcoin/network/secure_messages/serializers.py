"""
Serializers for secure messages protocol.
"""

from ..base_serializer import Serializer, SerializableMessage
from .. import data_fields


class SecureMessagesInventory(SerializableMessage):
    """
    The Secure Messages: Inventory representation.
    """
    def __init__(self):
        pass

class SecureMessagesInventorySerializer(Serializer):
    """
    The serializer for the Secure Messages Inventory.
    """
    model_class = SecureMessagesInventory


class SecureMessagesPing(SerializableMessage):
    """
    The secure messages: ping command, should always be
    answered with a Pong.
    """
    command = "smsgPing"

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

class SecureMessagesPingSerializer(Serializer):
    """
    The secure messages: ping command serializer.
    """
    model_class = SecureMessagesPing


class SecureMessagesPong(SerializableMessage):
    """
    The secure messages: pong command, usually returned
    when a ping command arrives.
    """
    command = "smsgPong"

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

class SecureMessagePongSerializer(Serializer):
    """
    The secure messages: pong command serializer.
    """
    model_class = SecureMessagesPong


class SecureMessagesDisabled(SerializableMessage):
    """
    The secure messages: disabled command.
    """
    command = "smsgDisabled"

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

class SecureMessageDisabledSerializer(Serializer):
    """
    The secure messages: disabled command serializer.
    """
    model_class = SecureMessagesDisabled


class SecureMessagesIgnore(SerializableMessage):
    """
    The secure messages: ignore command.
    """
    command = "smsgIgnore"

    def __init__(self):
        self.ignore_until = 0

    def __repr__(self):
        return f"<{self.__class__.__name__}, ignore_until=[{self.ignore_until}]>"

class SecureMessageIgnoreSerializer(Serializer):
    """
    The secure messages: ignore command serializer.
    """
    model_class = SecureMessagesIgnore

    ignore_until = data_fields.VariableStringField()
