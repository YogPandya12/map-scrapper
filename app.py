from flask import Flask, request, send_file, render_template, after_this_request, make_response
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

        excel_file = scrape_business_info(business_type, location)
        if not excel_file:
            return "Error occurred during scraping. Please try again."

        filename = os.path.basename(excel_file)

        # Open the file in binary mode and read its contents into memory.
        with open(excel_file, "rb") as f:
            data = f.read()

        # Delete the file now that we've read it.
        try:
            os.remove(excel_file)
        except Exception as e:
            app.logger.error(f"Error removing file: {e}")

        # Create a response with the file data.
        response = make_response(data)
        response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
        
    except Exception as e:
        app.logger.error(f"Error during scraping: {e}")
        return "An unexpected error occurred. Please try again later.", 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
