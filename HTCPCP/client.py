import socket
import re
import urllib.parse
from urllib.parse import urlparse

class Client:
  """
  TCP通信を行うクライアントを表すクラス
  """
  def check_ip_address_or_url(self,input_string: str) -> str:
    coffee_schemes = ["koffie",r"q%C3%A6hv%C3%A6",r"%D9%82%D9%87%D9%88%D8%A9","akeita","koffee","kahva","kafe" ,r"caf%C3%E8",r"%E5%92%96%E5%95%A1","kava",
                      "k%C3%A1va","kaffe","coffee","kafo","kohv","kahvi","%4Baffee",r"%CE%BA%CE%B1%CF%86%CE%AD",r"%E0%A4%95%E0%A5%8C%E0%A4%AB%E0%A5%80",
                      r"%E3%82%B3%E3%83%BC%E3%83%92%E3%83%BC",r"%EC%BB%A4%ED%94%BC",r"%D0%BA%D0%BE%D1%84%D0%B5",r"%E0%B8%81%E0%B8%B2%E0%B9%81%E0%B8%9F"]
    decoded_schemes = [urllib.parse.unquote(scheme) for scheme in coffee_schemes]
    # IPアドレスの正規表現パターン
    ip_address_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    
    scheme_pattern = '|'.join([re.escape(scheme) for scheme in decoded_schemes])

    url_pattern = r'^({})://([\w.-]+)\.([a-zA-Z]{{2,6}})(/[\w.-]*)*/?$'.format(scheme_pattern)
    
    # 入力文字列がIPアドレスのパターンにマッチするかチェック
    if re.match(ip_address_pattern, input_string):
        print("IP Address")
    
    # 入力文字列がURLのパターンにマッチするかチェック
    elif re.match(url_pattern, input_string):
        print("URL")
    
    # IPアドレスでもURLでもない場合
    else:
        print("Neither IP Address nor URL")

  def connect_to_url(url: str) -> None:
    parsed_url = urlparse(url)
    host: str = parsed_url.hostname
    port: int = parsed_url.port
    if not port:
        if parsed_url.scheme == "http":
            port = 80
        elif parsed_url.scheme == "https":
            port = 443

    try:
        ip_address: str = socket.gethostbyname(host)
        sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip_address, port))
        print("接続が成功しました。")
        sock.close()
    except socket.gaierror:
        print("ホスト名の解決に失敗しました。")

if __name__ == '__main__':
  input_string = input("接続先:")
  client = Client()
  client.check_ip_address_or_url(input_string)