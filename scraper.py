from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    data = {}
    if request.method == 'POST':
        url = request.form['url'].strip()

        # Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Page Title
            data['title'] = soup.title.string.strip() if soup.title else 'No Title Found'

            # Meta Description
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            data['meta_description'] = meta_tag['content'].strip() if meta_tag and 'content' in meta_tag.attrs else 'No Meta Description Found'

            # Favicon
            icon_tag = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
            if icon_tag and icon_tag.get('href'):
                data['favicon'] = urljoin(url, icon_tag['href'])
            else:
                parsed = urlparse(url)
                data['favicon'] = f"{parsed.scheme}://{parsed.netloc}/favicon.ico"

            # Headings
            data['h1'] = [h.get_text(strip=True) for h in soup.find_all('h1')]
            data['h2'] = [h.get_text(strip=True) for h in soup.find_all('h2')]
            data['h3'] = [h.get_text(strip=True) for h in soup.find_all('h3')]

            # All links (unique and cleaned)
            links = [urljoin(url, a['href'].strip()) for a in soup.find_all('a', href=True)]
            unique_links = list(dict.fromkeys([link for link in links if link.startswith(('http', 'https'))]))
            data['links'] = unique_links

            data['success'] = True
        except requests.exceptions.RequestException as e:
            data['error'] = f"Error fetching the URL: {str(e)}"
        except Exception as e:
            data['error'] = f"An unexpected error occurred: {str(e)}"

    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
