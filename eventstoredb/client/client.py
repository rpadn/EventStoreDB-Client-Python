from __future__ import annotations

from typing import AsyncGenerator, AsyncIterator, Iterable

from grpclib.client import Channel
from grpclib.exceptions import GRPCError

from eventstoredb.client.types import ClientOptions
from eventstoredb.events import EventData, ReadEvent
from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    PersistentSubscriptionsStub,
)
from eventstoredb.generated.event_store.client.streams import StreamsStub
from eventstoredb.persistent_subscriptions.common import convert_grpc_error_to_exception
from eventstoredb.persistent_subscriptions.create import (
    CreatePersistentSubscriptionOptions,
    create_create_request_options,
)
from eventstoredb.persistent_subscriptions.delete import (
    DeletePersistentSubscriptionOptions,
    create_delete_request_options,
)
from eventstoredb.persistent_subscriptions.subscribe import (
    PersistentSubscription,
    SubscribeToPersistentSubscriptionOptions,
)
from eventstoredb.persistent_subscriptions.update import (
    UpdatePersistentSubscriptionOptions,
    create_update_request_options,
)
from eventstoredb.streams.append import (
    AppendReq,
    AppendResult,
    AppendToStreamOptions,
    convert_append_response,
    create_append_header,
    create_append_request,
)
from eventstoredb.streams.read import (
    ReadStreamOptions,
    convert_read_response,
    create_read_request_options,
)
from eventstoredb.streams.subscribe import (
    SubscribeToStreamOptions,
    Subscription,
    create_stream_subscription_options,
)


class Client:
    def __init__(self, options: ClientOptions) -> None:
        self.options = options
        self._channel: Channel | None = None

    @property
    def channel(self) -> Channel:
        if self._channel is None:
            self._channel = Channel(host=self.options.host, port=self.options.port)
        return self._channel

    async def append_to_stream(
        self,
        stream_name: str,
        events: EventData | Iterable[EventData],
        options: AppendToStreamOptions | None = None,
    ) -> AppendResult:
        async def request_iterator() -> AsyncGenerator[AppendReq, None]:
            yield create_append_header(
                stream_name=stream_name,
                options=options,
            )
            if isinstance(events, EventData):
                yield create_append_request(events)
            else:
                for event in events:
                    yield create_append_request(event)

        client = StreamsStub(channel=self.channel)
        response = await client.append(request_iterator())
        return convert_append_response(stream_name, response)

    async def read_stream(
        self,
        stream_name: str,
        options: ReadStreamOptions | None = None,
    ) -> AsyncIterator[ReadEvent]:
        client = StreamsStub(channel=self.channel)
        request_options = create_read_request_options(
            stream_name=stream_name,
            options=options,
        )
        # TODO raise exception StreamNotFoundError
        async for response in client.read(options=request_options):
            yield convert_read_response(response)

    def subscribe_to_stream(
        self,
        stream_name: str,
        options: SubscribeToStreamOptions | None = None,
    ) -> Subscription:
        client = StreamsStub(channel=self.channel)
        request_options = create_stream_subscription_options(
            stream_name=stream_name,
            options=options,
        )
        it = client.read(options=request_options)
        return Subscription(it)

    async def create_persistent_subscription(
        self,
        stream_name: str,
        group_name: str,
        options: CreatePersistentSubscriptionOptions | None = None,
    ) -> None:
        client = PersistentSubscriptionsStub(channel=self.channel)
        request_options = create_create_request_options(
            stream_name=stream_name,
            group_name=group_name,
            options=options,
        )
        try:
            await client.create(options=request_options)
        except GRPCError as e:
            raise convert_grpc_error_to_exception(e)

    async def update_persistent_subscription(
        self,
        stream_name: str,
        group_name: str,
        options: UpdatePersistentSubscriptionOptions | None = None,
    ) -> None:
        client = PersistentSubscriptionsStub(channel=self.channel)
        request_options = create_update_request_options(
            stream_name=stream_name,
            group_name=group_name,
            options=options,
        )
        try:
            await client.update(options=request_options)
        except GRPCError as e:
            raise convert_grpc_error_to_exception(e)

    async def delete_persistent_subscription(
        self,
        stream_name: str,
        group_name: str,
        options: DeletePersistentSubscriptionOptions | None = None,
    ) -> None:
        client = PersistentSubscriptionsStub(channel=self.channel)
        request_options = create_delete_request_options(
            stream_name=stream_name,
            group_name=group_name,
            options=options,
        )
        try:
            await client.delete(options=request_options)
        except GRPCError as e:
            raise convert_grpc_error_to_exception(e)

    def subscribe_to_persistent_subscription(
        self,
        stream_name: str,
        group_name: str,
        options: SubscribeToPersistentSubscriptionOptions | None = None,
    ) -> PersistentSubscription:
        client = PersistentSubscriptionsStub(channel=self.channel)
        return PersistentSubscription(
            client=client,
            stream_name=stream_name,
            group_name=group_name,
            options=options,
        )
