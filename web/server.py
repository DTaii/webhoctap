import http.server
import socketserver
from pyngrok import ngrok

# Nếu chưa cài đặt auth token của ngrok, hãy cài đặt ở đây:
# ngrok.set_auth_token("YOUR_AUTH_TOKEN")

# Chọn cổng mà bạn muốn chạy server (ví dụ: 5000)
PORT = 5000

# Mở tunnel đến local server trên cổng đã chọn
public_url = ngrok.connect(PORT)
print("Public URL:", public_url)

# Thiết lập handler để phục vụ các file tĩnh trong thư mục hiện tại
Handler = http.server.SimpleHTTPRequestHandler

# Khởi chạy server với socketserver
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server đang chạy tại http://localhost:{PORT}")
    httpd.serve_forever()
