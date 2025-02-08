document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('scrape-form');
    const submitButton = form.querySelector('button[type="submit"]');
    const statusMessage = document.getElementById('status');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        submitButton.disabled = true;
        const buttonText = submitButton.querySelector('.button-text');
        const spinner = submitButton.querySelector('.spinner');
        
        buttonText.textContent = "Scraping...";
        spinner.style.display = "inline-block";
        statusMessage.style.display = "block";
        statusMessage.innerHTML = "Scraping in progress, please wait...";
        statusMessage.className = "";

        try {
            const formData = new FormData(form);
            const response = await fetch('/scrape', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(errorText || 'Scraping failed');
            }

            // Handle successful response
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');

            const businessType = formData.get('business_type').replace(/\s+/g, '_').toLowerCase();
            const location = formData.get('location').replace(/\s+/g, '_').toLowerCase();
            const filename = `${businessType}_${location}.xlsx`;

            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            statusMessage.innerHTML = "Scraping completed successfully!";
            statusMessage.classList.add('success');
        } catch (error) {
            console.error('Error:', error);
            statusMessage.innerHTML = error.message || "An error occurred during scraping.";
            statusMessage.classList.add('error');
        } finally {
            submitButton.disabled = false;
            buttonText.textContent = "Scrape";
            spinner.style.display = "none";
        }
    });
});