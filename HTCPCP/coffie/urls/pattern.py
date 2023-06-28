import re
from re import Match
from typing import Callable, Optional

from coffie.htcpcp.request import HTCPCPRequest
from coffie.htcpcp.response import HTCPCPResponse


class URLPattern:
    pattern: str
    view: Callable[[HTCPCPRequest], HTCPCPResponse]

    def __init__(self, pattern: str, view: Callable[[HTCPCPRequest], HTCPCPResponse]):
        self.pattern = pattern
        self.view = view

    def match(self, path: str) -> Optional[Match]:
        """
        pathがURLパターンにマッチするか判定する
        マッチした場合はMatchオブジェクトを返し、マッチしなかった場合はNoneを返す
        """
        # URLパターンを正規表現パターンに変換する
        # ex) '/user/<user_id>/profile' => '/user/(?P<user_id>[^/]+)/profile'
        pattern = re.sub(r"<(.+?)>", r"(?P<\1>[^/]+)", self.pattern)
        return re.match(pattern, path)