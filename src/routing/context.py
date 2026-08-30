from typing import Protocol

from pydantic import BaseModel, Field

from routing.models import EntityReference, Message, WorkflowState


class ConversationContext(BaseModel):
    user_id: str
    conversation_id: str
    recent_messages: list[Message] = Field(default_factory=list)
    conversation_summary: str | None = None
    entity_memory: list[EntityReference] = Field(default_factory=list)
    workflow: WorkflowState | None = None


class ContextStore(Protocol):
    def load(self, user_id: str, conversation_id: str) -> ConversationContext | None: ...

    def save(self, context: ConversationContext) -> None: ...


class InMemoryContextStore:
    def __init__(self):
        self._contexts: dict[tuple[str, str], ConversationContext] = {}

    def load(self, user_id: str, conversation_id: str) -> ConversationContext | None:
        return self._contexts.get((user_id, conversation_id))

    def save(self, context: ConversationContext) -> None:
        self._contexts[(context.user_id, context.conversation_id)] = context


class MongoContextStore:
    """Persist context using the project's existing MongoDB configuration."""

    def __init__(self, database: str = "pharaoh", collection: str = "conversation_context"):
        self.database = database
        self.collection = collection

    def _collection(self):
        from utils.mongo_helper import get_mongo_client

        client = get_mongo_client()
        return client, client[self.database][self.collection]

    def load(self, user_id: str, conversation_id: str) -> ConversationContext | None:
        client, collection = self._collection()
        try:
            document = collection.find_one({"user_id": user_id, "conversation_id": conversation_id}, {"_id": 0})
            return ConversationContext.model_validate(document) if document else None
        finally:
            client.close()

    def save(self, context: ConversationContext) -> None:
        client, collection = self._collection()
        try:
            collection.replace_one(
                {"user_id": context.user_id, "conversation_id": context.conversation_id},
                context.model_dump(mode="json"),
                upsert=True,
            )
        finally:
            client.close()
