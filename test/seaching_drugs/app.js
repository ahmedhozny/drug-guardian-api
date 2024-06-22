const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');

searchInput.addEventListener('input', async (event) => {
    const searchKey = event.target.value;
    if (searchKey.length < 3) {
        searchResults.innerHTML = '';  // Clear search results if search key is less than 3 characters
        return;
    }

    // Fetch search results from FastAPI route
    const response = await fetch(`http://drugguardian.servehttp.com/drugs?search_key=${searchKey}`);
    const data = await response.json();
    console.log(data); // Debug: Log the received data

    // Display search results
    searchResults.innerHTML = '';
    if (data.results && data.results.length > 0) {
        data.results.forEach(drug => {
            const drugInfo = document.createElement('li');
            drugInfo.innerHTML = `
                <strong>Brand Name:</strong> ${drug.brand_name}<br>
                <strong>Drug Ref:</strong> ${drug.drug_ref}<br>
                <strong>Drug Name:</strong> ${drug.drug_name}<br>
            `;
            searchResults.appendChild(drugInfo);
        });
    } else {
        console.log("No results found");
        searchResults.innerHTML = '<li>No results found</li>';
    }
});
