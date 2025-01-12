from flask import Flask, request, send_file, render_template, after_this_request
from scraper import scrape_business_info
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        business_type = request.form['business_type']
        location = request.form['location']

        if not business_type or not location:
            return "Error: Please enter both Business Type and Location.", 400

        csv_file = scrape_business_info(business_type, location)
        print('CSV FILE',csv_file)
        if csv_file:
            @after_this_request
            def remove_file(response):
                try:
                    os.remove(csv_file)
                except Exception as e:
                    app.logger.error(f"Error removing or closing downloaded file handle: {e}")
                return response
            return send_file(csv_file, as_attachment=True)
        else:
            return "Error occurred during scraping. Please try again."
    except Exception as e:
        app.logger.error(f"Error during scraping: {e}")
        return "An unexpected error occurred. Please try again later.", 500

if __name__ == '__main__':
    app.run(debug=True)
