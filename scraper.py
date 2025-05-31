from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    data = {}
    if request.method == 'POST':
        url = request.form['url']
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            data['title'] = soup.title.string if soup.title else 'No Title Found'
            data['h1'] = [h.get_text(strip=True) for h in soup.find_all('h1')]
            data['h2'] = [h.get_text(strip=True) for h in soup.find_all('h2')]
            data['h3'] = [h.get_text(strip=True) for h in soup.find_all('h3')]
            data['success'] = True
        except Exception as e:
            data['error'] = f"Failed to fetch: {str(e)}"
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
