import os
import re
import traceback
from datetime import datetime
from socket import socket
from threading import Thread
from typing import Tuple

from coffie.htcpcp.request import HTCPCPRequest
from coffie.htcpcp.response import HTCPCPResponse
from urls import url_patterns


class WorkerThread(Thread):
    # 実行ファイルのあるディレクトリ
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # 静的配信するファイルを置くディレクトリ
    STATIC_ROOT = os.path.join(BASE_DIR, "static")

    # 拡張子とMIME Typeの対応
    MIME_TYPES = {
        "html": "text/html; charset=UTF-8",
        "css": "text/css",
        "png": "image/png",
        "jpg": "image/jpg",
        "gif": "image/gif",
    }

    # ステータスコードとステータスラインの対応
    STATUS_LINES = {
        200: "200 OK",
        400: "400 Bad Request",
        404: "404 Not Found",
        405: "405 Method Not Allowed",
        406: "406 Not Acceptable",
        415: "415 Unsupported Media Type",
        416: "418 I'm a teapot",
        501: "501 Not Implemented"
    }

    def __init__(self, client_socket: socket, address: Tuple[str, int]):
        super().__init__()

        self.client_socket = client_socket
        self.client_address = address

    def run(self) -> None:
        """
        クライアントと接続済みのsocketを引数として受け取り、
        リクエストを処理してレスポンスを送信する
        """

        try:

            # クライアントから送られてきたデータを取得する
            request_bytes = self.client_socket.recv(4096)

            # クライアントから送られてきたデータをファイルに書き出す
            with open("server_recv.txt", "wb") as f:
                f.write(request_bytes)

            # HTCPCPリクエストをパースする
            request = self.parse_htcpcp_request(request_bytes)
        
            # HTCPCPプロトコル以外には501を返す
            if request.htcpcp_version[:request.htcpcp_version.find("/")] != "HTCPCP":
                return
            else:
                # pathにマッチするurl_patternを探し、見つかればviewからレスポンスを生成する
                for url_pattern in url_patterns:
                    match = url_pattern.match(request.path)
                    if match:
                        request.params.update(match.groupdict())
                        view = url_pattern.view
                        response = view(request)
                        break

                # pathがそれ以外のときは、404生成する
                # pathがそれ以外のときは、静的ファイルからレスポンスを生成する
                else:
                    response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
                    content_type = "text/html;"
                    response = HTCPCPResponse(body=response_body, content_type=content_type, status_code=404)

            # レスポンスラインを生成
            response_line = self.build_response_line(response)

            # レスポンスヘッダーを生成
            response_header = self.build_response_header(response, request)

            # レスポンス全体を生成する
            response_bytes = (response_line + response_header + "\r\n").encode() + response.body

            # クライアントへレスポンスを送信する
            self.client_socket.send(response_bytes)

        except Exception:
            # リクエストの処理中に例外が発生した場合はコンソールにエラーログを出力し、
            # 処理を続行する
            print("=== Worker: リクエストの処理中にエラーが発生しました ===")
            traceback.print_exc()

        finally:
            # 例外が発生した場合も、発生しなかった場合も、TCP通信のcloseは行う
            print(f"=== Worker: クライアントとの通信を終了します remote_address: {self.client_address} ===")
            self.client_socket.close()

    def parse_htcpcp_request(self, request: bytes) -> HTCPCPRequest:
        """
        生のHTCPCPリクエストを、HTCPCPRequestクラスへ変換する
        """
        # リクエスト全体を
        # - リクエストライン(1行目)
        # - リクエストヘッダー(2行目〜空行)
        # - リクエストボディ(空行〜)
        # にパースする
        request_line, remain = request.split(b"\r\n", maxsplit=1)
        request_header, request_body = remain.split(b"\r\n\r\n", maxsplit=1)

        # リクエストラインを文字列に変換してパースする
        method, path, htcpcp_version = request_line.decode().split(" ")

        # リクエストヘッダーを辞書にパースする
        headers = {}
        for header_row in request_header.decode().split("\r\n"):
            key, value = re.split(r": *", header_row, maxsplit=1)
            headers[key] = value

        return HTCPCPRequest(method=method, path=path, htcpcp_version=htcpcp_version, headers=headers, body=request_body)

    def get_static_file_content(self, path: str) -> bytes:
        """
        リクエストpathから、staticファイルの内容を取得する
        """

        # pathの先頭の/を削除し、相対パスにしておく
        relative_path = path.lstrip("/")
        # ファイルのpathを取得
        static_file_path = os.path.join(self.STATIC_ROOT, relative_path)

        with open(static_file_path, "rb") as f:
            return f.read()

    def build_response_line(self, response: HTCPCPResponse) -> str:
        """
        レスポンスラインを構築する
        """
        status_line = self.STATUS_LINES[response.status_code]
        return f"HTCPCP/1.1 {status_line}\r\n"

    def build_response_header(self, response: HTCPCPResponse, request: HTCPCPRequest) -> str:
        """
        レスポンスヘッダーを構築する
        """

        # Content-Typeが指定されていない場合はpathから特定する
        if response.content_type is None:
            # pathから拡張子を取得
            if "." in request.path:
                ext = request.path.rsplit(".", maxsplit=1)[-1]
            else:
                ext = ""
            # 拡張子からMIME Typeを取得
            # 知らない対応していない拡張子の場合はoctet-streamとする
            response.content_type = self.MIME_TYPES.get(ext, "application/octet-stream")

        response_header = ""
        response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
        response_header += "Host: CoffiePot/0.1\r\n"
        response_header += f"Content-Length: {len(response.body)}\r\n"
        response_header += "Connection: Close\r\n"
        response_header += f"Content-Type: {response.content_type}\r\n"
        # コーヒーURIのデータにはカフェインは含まれない
        if request.method == "GET":
            response_header += "Caffeine-Content: None\r\n"

        return response_header