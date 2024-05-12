#+======== 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 117 ========+
#              +---+\    /      /\_
#copper be like|:-/  |--{=|=|==|
#              +---+/   |____   \
#                                |_




from http.server import HTTPServer, BaseHTTPRequestHandler
import html_handler
import database_managment
import templater
import urllib.parse
import os
product_card = r'<div class="product-card"><img src="{: src :}" alt="Something" style="width: 100%; height: 320px;"><h1>{: header :}</h1><p>{: description :}</p><p>{: price :}</p><button id="{: bttn_id :}">Add to cart</button></div>'

def shop_page(x):
    products = list()
    
    for product in database_managment.products_table.get_records(rows = True):
      header = product[1][1]
      description = product[2][1]
      quantity = product[3][1]
      price = product[4][1]
      src = product[5][1]
      products.append({"header":header, "description":description, "src":src, "price":price})

    default_html_page = html_handler.HTMLElementsHandler('index.html')
    html_code = default_html_page.get_html_code()
    code = templater.Template(html_code)
    code = code.render()
    default_html_page.set_html_code(code)
    for index, product in enumerate(products):
      code = templater.Template(product_card)
      code = code.render(header=product['header'], description=product['description'], src=product['src'], bttn_id = index + 1, price=f"{product["price"]}$")
      default_html_page.push_into_element(element_id="product-cards-container", code_fragment=code)
    print(default_html_page.get_html_code())
    x.wfile.write(default_html_page.get_html_code().encode())

def login_page(x):
  login_page = html_handler.HTMLElementsHandler("login.html")
  html_code = login_page.get_html_code()

  x.wfile.write(html_code.encode())


def not_find(x, default_html_page):
  html_code = default_html_page.get_html_code()
  code = templater.Template(html_code)
  code = code.render(path2="index", path='home')
  default_html_page.set_html_code(code)

  x.wfile.write(default_html_page.get_html_code().encode())


html_web_pages = {"login":login_page, "shop": shop_page}


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    print(self.path, self.path.endswith(".css"))
    if self.path.endswith(".css"):
        self.handle_css_request()
    elif self.path.endswith(".png"):
        self.handle_image_reqeust()
    elif self.path.endswith(".js"):
        self.handle_js_request()
    else:
        self.handle_html_request()

  def handle_css_request(self):
    print("\nCSS HANDLER REQUEST\n")
    try:
        print(os.path.join(os.getcwd(), self.path[1:]), os.getcwd(), self.path)
        with open(os.path.join(os.getcwd(), self.path[1:]), 'rb') as f:
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            self.wfile.write(f.read())
    except FileNotFoundError:
        print(self.path)
        self.send_error(404, "File not found")

  def handle_image_reqeust(self):
    print("\nIMAGE HANDLER REQUEST\n")
    try:
      with open(os.path.join(os.getcwd(), self.path[1:]), 'rb') as f:
        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.end_headers()
        self.wfile.write(f.read())
      pass
    except FileNotFoundError:
      self.send_response(200)
      with open('./items/errorimage.png', 'rb') as f:
        self.send_header('Content-type', 'image/png')
        self.end_headers()
        self.wfile.write(f.read())

  def handle_js_request(self):
    print("\nJS HANDLER REQUEST\n")
    try:
      with open(os.path.join(os.getcwd(), self.path[1:]), 'rb') as f:
        self.send_response(200)
        self.send_header('Content-type', 'text/js')
        self.end_headers()
        self.wfile.write(f.read())
    except FileNotFoundError:
      self.send_error(404, "File not found")

  def handle_html_request(self):
    print("\nHTML HANDLER REQUEST\n")
    self.send_response(200)
    self.send_header('content-type', 'text/html')
    self.end_headers()
    
    page_handled = False
    default_html_page = html_handler.HTMLElementsHandler('index.html')

    for key, value in html_web_pages.items():
        if self.path[1:] == key:
            page_handled = True
            value(self)
    
    if not page_handled:
        not_find(self, default_html_page)
    
  def do_POST(self):
    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length)
    data = urllib.parse.parse_qs(post_data.decode('utf-8'))
    print(self.path)
    print(data, 123)
    print(post_data)
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()

    print([f"{key}: {value}" for key, value in data.items()])


def main():
  PORT = 8000
  server = HTTPServer(('', PORT), SimpleHTTPRequestHandler)
  print(f"Server running on port {PORT}")
  server.serve_forever()


if __name__ == "__main__":
  main()
