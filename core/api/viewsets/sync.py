from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from core.services.sync.push.dispatcher import handle_push
from core.services.sync.pull.builder import build_pull_response
from core.services.sync.common.time import safe_parse_dt


class SyncViewSet(ViewSet):

    @action(detail=False, methods=["post"])
    def push(self, request):
        handle_push(request.user, request.data)
        return Response({"status": "ok"})

    @action(detail=False, methods=["post"])
    def pull(self, request):
        last_sync = safe_parse_dt(request.data.get("last_sync"))

        data = build_pull_response(request.user, last_sync)

        return Response(data)
