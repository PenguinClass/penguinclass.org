---
layout: default
title: Results
permalink: /results/
---

# Results

Search and browse regatta results and race outcomes from the Penguin Class archives.

## Search Results

<input id="search-input" type="search" placeholder="Search by year, event, club, or location..." class="search-input">

<div id="search-results">
  <div id="loading">Loading results...</div>
</div>

<script src="https://unpkg.com/lunr/lunr.js"></script>
<script>
(async () => {
  const searchInput = document.getElementById('search-input');
  const searchResults = document.getElementById('search-results');
  
  try {
    console.log('Loading results data...');
    
    // Load results data
    const resultsResponse = await fetch('/assets/data/results.json', {cache: 'no-cache'});
    
    if (!resultsResponse.ok) {
      throw new Error(`HTTP error! status: ${resultsResponse.status}`);
    }
    
    const results = await resultsResponse.json();
    console.log('Loaded results:', results.length);
    
    // Create search index
    const index = lunr(function () {
      this.ref('year');
      this.field('year');
      this.field('series');
      this.field('club');
      this.field('location');
      this.field('filename');
      
      results.forEach(item => {
        this.add({
          year: String(item.year),
          series: item.series || '',
          club: item.club || '',
          location: item.location || '',
          filename: item.filename || ''
        });
      });
    });
    
    function renderResults(results) {
      if (results.length === 0) {
        searchResults.innerHTML = '<p class="no-results">No results found.</p>';
        return;
      }
      
      const html = results.map(result => {
        const item = results.find(r => String(r.year) === result.ref);
        if (!item) return '';
        
        const resultsLink = item.results_url ? 
          `<a href="${item.results_url}" class="results-link" target="_blank">View Results</a>` : 
          '<span class="no-results-link">No results available</span>';
        
        return `
          <div class="result-item">
            <div class="result-header">
              <h3>${item.year} ${item.series}</h3>
              ${resultsLink}
            </div>
            <div class="result-details">
              ${item.club ? `<p><strong>Club:</strong> ${item.club}</p>` : ''}
              ${item.location ? `<p><strong>Location:</strong> ${item.location}</p>` : ''}
              <p><strong>File:</strong> ${item.filename}</p>
            </div>
          </div>
        `;
      }).join('');
      
      searchResults.innerHTML = html;
    }
    
    function performSearch(query) {
      if (!query.trim()) {
        // Show all results, sorted by year (most recent first)
        const allResults = results
          .map(r => ({ ref: String(r.year) }))
          .sort((a, b) => parseInt(b.ref) - parseInt(a.ref));
        renderResults(allResults);
        return;
      }
      
      try {
        const searchResults = index.search(query);
        renderResults(searchResults);
      } catch (error) {
        console.error('Search error:', error);
        searchResults.innerHTML = '<p class="error">Search error. Please try again.</p>';
      }
    }
    
    // Initial load - show all results
    performSearch('');
    
    // Search on input
    searchInput.addEventListener('input', (e) => {
      performSearch(e.target.value);
    });
    
  } catch (error) {
    console.error('Error loading results:', error);
    searchResults.innerHTML = '<p class="error">Error loading results: ' + error.message + '. Please refresh the page.</p>';
  }
})();
</script>

<style>
.search-input {
  width: 100%;
  padding: 0.75rem;
  margin-bottom: 1rem;
  border: 1px solid var(--header-border);
  border-radius: 4px;
  font-size: 1rem;
  background: var(--bg);
  color: var(--text-color);
  font-family: inherit;
}

.search-input:focus {
  outline: none;
  border-color: var(--link);
  box-shadow: 0 0 0 2px rgba(44, 90, 160, 0.2);
}

.result-item {
  border: 1px solid var(--header-border);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  background: var(--bg);
  transition: box-shadow 0.2s ease;
}

.result-item:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

@media (prefers-color-scheme: dark) {
  .result-item:hover {
    box-shadow: 0 2px 8px rgba(255,255,255,0.1);
  }
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--header-border);
}

.result-header h3 {
  margin: 0;
  color: var(--text-color);
  font-size: 1.25rem;
}

.results-link {
  background: var(--link);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  text-decoration: none;
  font-size: 0.9rem;
  transition: opacity 0.2s ease;
}

.results-link:hover {
  opacity: 0.8;
  text-decoration: none;
}

.no-results-link {
  color: var(--ink);
  font-style: italic;
  font-size: 0.9rem;
  opacity: 0.7;
}

.result-details p {
  margin: 0.5rem 0;
  font-size: 0.95rem;
  line-height: 1.4;
  color: var(--text-color);
}

.result-details strong {
  color: var(--text-color);
  font-weight: 600;
}

#loading, .no-results, .error {
  text-align: center;
  padding: 2rem;
  color: var(--ink);
}

.error {
  color: #e74c3c;
}

@media (prefers-color-scheme: dark) {
  .error {
    color: #ff6b6b;
  }
}
</style>

## About These Results

This search includes all regatta results and race outcomes from the Penguin Class archives, including:

- **International Championships** (2006-present)
- **North American Championships** (2012-present)
- **Annual Regattas** (TAYC, Corsica, Cambridge, etc.)
- **Frostbite Series** (winter racing)
- **Heritage Regattas** (special events)
- **Spring Series** (early season racing)
- **Rum Bucket Regattas** (social racing events)
- **Revival Regattas** (Beachwood events)

Results are searchable by year, event type, yacht club, or location. Click "View Results" to access the complete race results and standings.

For championship winners and Hall of Fame information, visit our [Champions](/champions/) page. For additional historical records, visit our [Archive](/archive/legacy-website/).