# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: monitoring.proto
# plugin: python-betterproto
from dataclasses import dataclass
from typing import AsyncIterator, Dict

import betterproto
import grpclib
from betterproto.grpc.grpclib_server import ServiceBase


@dataclass(eq=False, repr=False)
class StatsReq(betterproto.Message):
    use_metadata: bool = betterproto.bool_field(1)
    refresh_time_period_in_ms: int = betterproto.uint64_field(4)


@dataclass(eq=False, repr=False)
class StatsResp(betterproto.Message):
    stats: Dict[str, str] = betterproto.map_field(
        1, betterproto.TYPE_STRING, betterproto.TYPE_STRING
    )


class MonitoringStub(betterproto.ServiceStub):
    async def stats(
        self, *, use_metadata: bool = False, refresh_time_period_in_ms: int = 0
    ) -> AsyncIterator["StatsResp"]:

        request = StatsReq()
        request.use_metadata = use_metadata
        request.refresh_time_period_in_ms = refresh_time_period_in_ms

        async for response in self._unary_stream(
            "/event_store.client.monitoring.Monitoring/Stats",
            request,
            StatsResp,
        ):
            yield response


class MonitoringBase(ServiceBase):
    async def stats(
        self, use_metadata: bool, refresh_time_period_in_ms: int
    ) -> AsyncIterator["StatsResp"]:
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_stats(self, stream: grpclib.server.Stream) -> None:
        request = await stream.recv_message()

        request_kwargs = {
            "use_metadata": request.use_metadata,
            "refresh_time_period_in_ms": request.refresh_time_period_in_ms,
        }

        await self._call_rpc_handler_server_stream(
            self.stats,
            stream,
            request_kwargs,
        )

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/event_store.client.monitoring.Monitoring/Stats": grpclib.const.Handler(
                self.__rpc_stats,
                grpclib.const.Cardinality.UNARY_STREAM,
                StatsReq,
                StatsResp,
            ),
        }
