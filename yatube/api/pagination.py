from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class CustomPagination(LimitOffsetPagination):
    def get_paginated_response(self, data):
        if len(self.request.query_params) == 0:
            return Response(data)
        return super().get_paginated_response(data)
