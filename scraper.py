
import json
import os
import requests
from bs4 import BeautifulSoup

def scrape_linktree_data(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    script_tag = soup.find('script', {'id': '__NEXT_DATA__'})

    if not script_tag:
        raise ValueError("Could not find the __NEXT_DATA__ script tag.")

    json_data = json.loads(script_tag.string)

    account_data = json_data['props']['pageProps']['account']

    profile_picture_url = account_data['profilePictureUrl']
    username = account_data['username']
    social_links = account_data['socialLinks']
    links = account_data['links']

    return {
        'profile_picture_url': profile_picture_url,
        'username': username,
        'social_links': social_links,
        'links': links
    }

def download_profile_picture(url, output_dir='public'):
    filename = os.path.join(output_dir, 'profile_picture.jpg')
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
    else:
        print(f"Failed to download profile picture. Status code: {response.status_code}")

def generate_html(data, output_dir='public'):
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['username']}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <aside class="sidebar">
            <div class="profile">
                <img src="profile_picture.jpg" alt="Profile Picture" class="profile-img">
                <h1 class="profile-name">@{data['username']}</h1>
            </div>
        </aside>
        <main class="main-content">
"""
    for link in data['links']:
        html_content += f'            <a href="{link["url"]}" class="link-card" target="_blank">{link["title"]}</a>\n'
    html_content += """
        </main>
    </div>
</body>
</html>
"""
    with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)

def generate_css(output_dir='public'):
    css_content = """
body {
    font-family: "San Francisco Pro", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    margin: 0;
    background-color: #f0f2f5;
    color: #1c1e21;
}

.container {
    display: flex;
    max-width: 1200px;
    margin: 0 auto;
}

.sidebar {
    width: 300px;
    padding: 2rem;
    background-color: #fff;
    border-right: 1px solid #dddfe2;
    height: 100vh;
    position: fixed;
}

.profile {
    text-align: center;
}

.profile-img {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    margin-bottom: 1rem;
}

.profile-name {
    font-size: 1.5rem;
    margin: 0;
}

.main-content {
    margin-left: 300px;
    padding: 2rem;
    width: 100%;
}

.link-card {
    display: block;
    background-color: #fff;
    padding: 1.5rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    text-decoration: none;
    color: #1c1e21;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
    transition: all 0.3s cubic-bezier(.25,.8,.25,1);
}

.link-card:hover {
    box-shadow: 0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22);
}
"""
    with open(os.path.join(output_dir, 'style.css'), 'w', encoding='utf-8') as f:
        f.write(css_content)

if __name__ == '__main__':
    output_directory = 'public'
    os.makedirs(output_directory, exist_ok=True)

    scraped_data = scrape_linktree_data('linktree.html')
    download_profile_picture(scraped_data['profile_picture_url'], output_dir=output_directory)
    generate_html(scraped_data, output_dir=output_directory)
    generate_css(output_dir=output_directory)
    print(f"Successfully generated files in '{output_directory}' directory.")
