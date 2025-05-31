from flask import Flask, render_template, request, send_file, redirect, url_for
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import json
import io

app = Flask(__name__)

# Function to scrape website data
def scrape_website(url):
    data = {}
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    data['url'] = url
    data['title'] = soup.title.string.strip() if soup.title else 'No Title Found'

    meta_tag = soup.find('meta', attrs={'name': 'description'})
    data['meta_description'] = meta_tag['content'].strip() if meta_tag and 'content' in meta_tag.attrs else 'No Meta Description Found'

    icon_tag = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
    if icon_tag and icon_tag.get('href'):
        data['favicon'] = urljoin(url, icon_tag['href'])
    else:
        data['favicon'] = urljoin(url, '/favicon.ico')

    data['h1'] = [h.get_text(strip=True) for h in soup.find_all('h1')]
    data['h2'] = [h.get_text(strip=True) for h in soup.find_all('h2')]
    data['h3'] = [h.get_text(strip=True) for h in soup.find_all('h3')]

    links = soup.find_all('a', href=True)
    data['links'] = [urljoin(url, a['href']) for a in links]

    # Add screenshot URL (using Microlink free API)
    # Change or replace with your preferred screenshot API
    data['screenshot'] = f"https://api.microlink.io?url={url}"

    return data

@app.route('/', methods=['GET', 'POST'])
def index():
    data = {}
    file_format = None
    if request.method == 'POST':
        url = request.form['url']
        file_format = request.form.get('file_format')  # csv or json or None

        try:
            data = scrape_website(url)
            data['success'] = True

            # Save as file if requested
            if file_format == 'csv':
                # Prepare CSV in-memory
                output = io.StringIO()
                writer = csv.writer(output)

                # Write header
                writer.writerow(['Field', 'Value'])
                writer.writerow(['URL', data['url']])
                writer.writerow(['Title', data['title']])
                writer.writerow(['Meta Description', data['meta_description']])
                writer.writerow(['Favicon', data['favicon']])
                writer.writerow(['H1 Headings', '; '.join(data['h1'])])
                writer.writerow(['H2 Headings', '; '.join(data['h2'])])
                writer.writerow(['H3 Headings', '; '.join(data['h3'])])
                writer.writerow(['Links', '; '.join(data['links'])])

                output.seek(0)
                return send_file(io.BytesIO(output.getvalue().encode()), 
                                 mimetype='text/csv', 
                                 download_name='scraped_data.csv', 
                                 as_attachment=True)

            elif file_format == 'json':
                # Prepare JSON in-memory
                json_str = json.dumps(data, indent=4)
                return send_file(io.BytesIO(json_str.encode()), 
                                 mimetype='application/json', 
                                 download_name='scraped_data.json', 
                                 as_attachment=True)

        except Exception as e:
            data['error'] = f"Failed to fetch: {str(e)}"

    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
