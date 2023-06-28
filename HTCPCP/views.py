import textwrap

from coffie.htcpcp.request import HTCPCPRequest
from coffie.htcpcp.response import HTCPCPResponse

from coffie.entity.coffiepot import CoffiePot
from coffie.entity.coffiecup import CoffieCup


def pot(request: HTCPCPRequest) -> HTCPCPResponse:
    """
    コーヒーポットの状態を表示するHTMLを生成する
    """
    if request.method == "GET":
        pot = CoffiePot()
        prop = request.params["prop"]
        html = f"""\
            <html>
            <body>
                <h1>{prop}:{getattr(pot, prop)}</h1>
            </body>
            </html>
        """
        status_code = 200
    else:
        html = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"
        status_code = 405
    body = textwrap.dedent(html).encode()
    return HTCPCPResponse(body=body,status_code=status_code)

def cup(request: HTCPCPRequest) -> HTCPCPResponse:
    """
    コーヒーカップの状態を表示するHTMLを生成する
    """
    if request.method == "PROFIND":
        cup = CoffieCup()
        prop = request.params["prop"]
        html = f"""\
            <html>
            <body>
                <h1>{prop}:{getattr(cup, prop)}</h1>
            </body>
            </html>
        """
        status_code = 200
    else:
        html = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"
        status_code = 405

    body = textwrap.dedent(html).encode()
    return HTCPCPResponse(body=body, status_code=status_code)

def brew_coffie(request: HTCPCPRequest) -> HTCPCPResponse:
    """
    コーヒーを淹れる
    """
    if request.method in ("BREW"):
        if request.headers["Content-Type"] != 'message/coffeepot':
            html = b"<html><body><h1>415 Unsupported Media Type</h1></body></html>"
            status_code = 415
        else:
            request_body = request.body.decode()
            if request_body == 'start':
                accept_additions = ""
                pot = CoffiePot()
                for pair in (request.headers["Accept-Additions"].split("; ")):
                    key, value = pair.split("=")
                    if key not in pot.can_provide_additions:
                        html = b"<html><body><h1>406 Not Acceptable</h1></body></html>"
                        status_code = 406
                        body = textwrap.dedent(html).encode()
                        return HTCPCPResponse(body=body, status_code=status_code)
                    value = value.strip('"')
                    accept_additions += f"<li>{key}:{value}<li>\n"
                html = f"""\
                    <html>
                    <body>
                        <h1>started brew coffie</h1>
                        <ul>
                            {accept_additions}
                        </ul>                
                    </body>
                    </html>
                """
                status_code = 200
            elif request_body == 'stop':
                html = f"""\
                    <html>
                    <body>
                        <h1>stopped brew coffie</h1>
                    </body>
                    </html>
                """
                status_code = 200
            else:
                html = "<html><body><h1>400 Bad Request</h1></body></html>"
                status_code = 400
    else:
        html = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"
        status_code = 405
    
    body = textwrap.dedent(html).encode()
    return HTCPCPResponse(body=body, status_code=status_code)

def brew_tea(request: HTCPCPRequest) -> HTCPCPResponse:
    """
    紅茶を淹れる
    """
    html = b"<html><body><h1>418 I'm a teapot</h1></body></html>"
    status_code = 418
    body = textwrap.dedent(html).encode()
    return HTCPCPResponse(body=body, status_code=status_code)

def stop_milk(request: HTCPCPRequest) -> HTCPCPResponse:
    """
    牛乳の提供を停止させる
    """
    if request.method in ("WHEN"):
        html = f"""\
            <html>
            <body>
                <h1>stopped milk</h1>                    
            </body>
            </html>
        """
        status_code = 200
    else:
        html = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"
        status_code = 405
    
    body = textwrap.dedent(html).encode()
    return HTCPCPResponse(body=body, status_code=status_code)