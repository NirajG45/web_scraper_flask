from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    data = {}
    if request.method == 'POST':
        url = request.form['url']
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            data['title'] = soup.title.string.strip() if soup.title else 'No Title Found'

            # Meta description
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            data['meta_description'] = meta_tag['content'].strip() if meta_tag and 'content' in meta_tag.attrs else 'No Meta Description Found'

            # Favicon
            icon_tag = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
            if icon_tag and icon_tag.get('href'):
                data['favicon'] = urljoin(url, icon_tag['href'])
            else:
                data['favicon'] = None

            # Headings
            data['h1'] = [h.get_text(strip=True) for h in soup.find_all('h1')]
            data['h2'] = [h.get_text(strip=True) for h in soup.find_all('h2')]
            data['h3'] = [h.get_text(strip=True) for h in soup.find_all('h3')]

            # All links
            links = soup.find_all('a', href=True)
            data['links'] = [urljoin(url, a['href']) for a in links]

            data['success'] = True
        except Exception as e:
            data['error'] = f"Failed to fetch: {str(e)}"
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
