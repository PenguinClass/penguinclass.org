---
layout: page
title: Gallery
permalink: /gallery/
---

Welcome to the Penguin Class Gallery! This collection contains **<span id="total-photos">Loading...</span> unique photos and videos** from events, regattas, and activities spanning decades of Penguin Class history.  There are also links and information at the bottom of this page if you are looking for or able to provide additional photos.

## Search

<div class="gallery-search">
  <input type="text" id="search-input-upper" placeholder="Search photos by filename, event, or year..." />
</div>
<div id="search-results" class="search-results"></div>

## Browse by Category

<div class="gallery-categories">
  <div class="category-card" data-category="photos">
    <h3>📸 All Photos</h3>
    <p id="photos-count">Loading...</p>
    <button class="view-photos-btn" onclick="viewCategory('photos')">View Photos</button>
  </div>
  
  <div class="category-card" data-category="championships">
    <h3>🏆 Championships</h3>
    <p id="championships-count">Loading...</p>
    <button class="view-photos-btn" onclick="viewCategory('championships')">View Photos</button>
  </div>
  
  <div class="category-card" data-category="regattas">
    <h3>⛵ Regattas</h3>
    <p id="regattas-count">Loading...</p>
    <button class="view-photos-btn" onclick="viewCategory('regattas')">View Photos</button>
  </div>
  
  <div class="category-card" data-category="frostbite">
    <h3>❄️ Frostbite</h3>
    <p id="frostbite-count">Loading...</p>
    <button class="view-photos-btn" onclick="viewCategory('frostbite')">View Photos</button>
  </div>
  
  <div class="category-card" data-category="tayc">
    <h3>🏛️ TAYC</h3>
    <p id="tayc-count">Loading...</p>
    <button class="view-photos-btn" onclick="viewCategory('tayc')">View Photos</button>
  </div>
  
  <div class="category-card" data-category="cryc">
    <h3>🌊 CRYC</h3>
    <p id="cryc-count">Loading...</p>
    <button class="view-photos-btn" onclick="viewCategory('cryc')">View Photos</button>
  </div>
  
  <div class="category-card" data-category="giys">
    <h3>⚓ GIYS</h3>
    <p id="giys-count">Loading...</p>
    <button class="view-photos-btn" onclick="viewCategory('giys')">View Photos</button>
  </div>
  
  <div class="category-card" data-category="beachwood">
    <h3>🏖️ Beachwood</h3>
    <p id="beachwood-count">Loading...</p>
    <button class="view-photos-btn" onclick="viewCategory('beachwood')">View Photos</button>
  </div>
  
  <div class="category-card" data-category="awards">
    <h3>🏅 Awards</h3>
    <p id="awards-count">Loading...</p>
    <button class="view-photos-btn" onclick="viewCategory('awards')">View Photos</button>
  </div>
  
  <div class="category-card" data-category="heritage">
    <h3>📜 Heritage</h3>
    <p id="heritage-count">Loading...</p>
    <button class="view-photos-btn" onclick="viewCategory('heritage')">View Photos</button>
  </div>
  
  <div class="category-card" data-category="boats">
    <h3>⛵ Boats</h3>
    <p id="boats-count">Loading...</p>
    <button class="view-photos-btn" onclick="viewCategory('boats')">View Photos</button>
  </div>
</div>

## Browse by Year

<div class="gallery-years">
  <div class="year-section">
    <h3>Recent Years</h3>
    <div class="year-grid">
      <button class="year-link" onclick="viewYear('2024')">2024 (30 photos)</button>
      <button class="year-link" onclick="viewYear('2023')">2023 (44 photos)</button>
      <button class="year-link" onclick="viewYear('2022')">2022 (22 photos)</button>
      <button class="year-link" onclick="viewYear('2021')">2021 (46 photos)</button>
    </div>
  </div>
  
  <div class="year-section">
    <h3>Historical Years</h3>
    <div class="year-grid">
      <button class="year-link" onclick="viewYear('2016')">2016 (10 photos)</button>
      <button class="year-link" onclick="viewYear('2014')">2014 (4 photos)</button>
      <button class="year-link" onclick="viewYear('2012')">2012 (3 photos)</button>
      <button class="year-link" onclick="viewYear('2011')">2011 (2 photos)</button>
      <button class="year-link" onclick="viewYear('2010')">2010 (66 photos)</button>
      <button class="year-link" onclick="viewYear('2008')">2008 (20 photos)</button>
      <button class="year-link" onclick="viewYear('2006')">2006 (69 photos)</button>
      <button class="year-link" onclick="viewYear('1955')">1955 (1 photo)</button>
    </div>
  </div>
</div>

<!-- disabled 2025-09-16 lacking solution to display of results
div class="gallery-search">
  <input type="text" id="search-input-lower" placeholder="Search photos by filename, event, or year..." />
</div -->

<div id="gallery-photo-viewer" class="photo-viewer" style="display: none;">
  <div class="viewer-header">
    <h3 id="viewer-title">Photo Gallery</h3>
    <button id="close-viewer" onclick="closeViewer()">×</button>
  </div>
  <div class="viewer-controls">
    <button id="prev-photo" onclick="previousPhoto()">← Previous</button>
    <span id="photo-counter">1 of 1</span>
    <button id="next-photo" onclick="nextPhoto()">Next →</button>
  </div>
  <div class="photo-container">
    <img id="current-photo" src="" alt="" />
  </div>
  <div class="photo-info">
    <p id="photo-filename"></p>
    <p id="photo-details"></p>
    <p id="photo-credit"></p>
  </div>
  <div class="photo-thumbnails" id="photo-thumbnails"></div>
</div>

## Legacy Archive Access

All historical photos are preserved in the [Legacy Website Archive](/archive/legacy-website/) with full organization by event, year, and category. The archive contains the complete collection of photos with their original organization.

## Photo Information

- **Total Photos**: <span id="total-photos">Loading...</span> unique images
- **Date Range**: 1941 - 2025
- **Sources**: Publicly available photos (see credits and watermarks) and legacy website archive
- **Formats**: JPG, PNG, GIF, and other standard web formats
- **Note**: Some photos may be copyrighted. Please respect photographer credits and watermarks.

## Submit Photos

To contribute photos to the gallery:
- Email photos to the [Class Secretary](/class/officers/)
- Include event name, date, and photographer credit
- High-resolution images preferred
- Photos will be reviewed before posting

## Photo Guidelines

- Photos should be Penguin Class related
- Include proper credits when possible
- Respect privacy of participants
- Event organizers may submit official event photos

*For questions about the gallery or to submit photos, please contact the [Class Secretary](/class/officers/).*

<style>
.gallery-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
  margin: 2rem 0;
}

.category-card {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1.5rem;
  background: var(--card-background);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.category-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.category-card h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
}

.category-card p {
  margin: 0 0 1rem 0;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.view-photos-btn {
  background: var(--button-background);
  color: var(--button-text);
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s ease;
}

.view-photos-btn:hover {
  background: var(--button-hover-background);
}

.gallery-years {
  margin: 2rem 0;
}

.year-section {
  margin-bottom: 2rem;
}

.year-section h3 {
  margin-bottom: 1rem;
  color: var(--heading-color);
}

.year-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.5rem;
}

.year-link {
  padding: 0.75rem 1rem;
  background: var(--button-background);
  color: var(--button-text);
  border: none;
  border-radius: 4px;
  text-align: center;
  transition: background-color 0.2s ease;
  font-size: 0.9rem;
  cursor: pointer;
}

.year-link:hover {
  background: var(--button-hover-background);
}

.gallery-search {
  margin: 2rem 0;
  padding: 1.5rem;
  background: var(--card-background);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

#search-input-upper,
#search-input-lower {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 1rem;
  background: var(--input-background);
  color: var(--text-color);
}

.search-results {
  margin-top: 1rem;
  min-height: 60px;
  max-height: 200px;
  overflow-y: auto;
  padding: 0.5rem;
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.photo-viewer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.95);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  flex-shrink: 0;
}

.viewer-header h3 {
  margin: 0;
  color: white;
}

#close-viewer {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  font-size: 2rem;
  cursor: pointer;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

#close-viewer:hover {
  background: rgba(255, 255, 255, 0.3);
}

.viewer-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.8);
  color: white;
}

.viewer-controls button {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.viewer-controls button:hover {
  background: rgba(255, 255, 255, 0.3);
}

.photo-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  min-height: 0; /* Allow flex item to shrink */
  overflow: hidden;
}

.photo-container img {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  border-radius: 4px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  display: block;
}

.photo-info {
  padding: 1rem;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  text-align: center;
  flex-shrink: 0;
}

.photo-info p {
  margin: 0.25rem 0;
  color: white;
}

.photo-thumbnails {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.9);
  overflow-x: auto;
  flex-shrink: 0;
}

.photo-thumbnails img {
  width: 80px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.photo-thumbnails img:hover,
.photo-thumbnails img.active {
  opacity: 1;
}

@media (prefers-color-scheme: dark) {
  .category-card {
    background: var(--dark-card-background);
    border-color: var(--dark-border-color);
  }
  
  .gallery-search {
    background: var(--dark-card-background);
    border-color: var(--dark-border-color);
  }
  
  #search-input-upper,
  #search-input-lower {
    background: var(--dark-input-background);
    border-color: var(--dark-border-color);
    color: var(--dark-text-color);
  }
  
  .search-results {
    background: var(--dark-card-background);
    border-color: var(--dark-border-color);
  }
}

@media (max-width: 768px) {
  .gallery-categories {
    grid-template-columns: 1fr;
  }
  
  .year-buttons {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .photo-viewer {
    padding: 1rem;
  }
  
  .viewer-controls {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .photo-thumbnails {
    max-height: 60px;
  }
  
  .photo-thumbnails img {
    width: 40px;
    height: 40px;
  }
  
  .search-results {
    max-height: 150px;
    font-size: 0.9rem;
  }
}

@media (min-width: 1200px) {
  .gallery-categories {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .search-results {
    max-height: 250px;
  }
}
</style>

<script>
let galleryData = null;
let currentPhotos = [];
let currentPhotoIndex = 0;

// Load gallery data
async function loadGalleryData() {
  try {
    // Show loading state
    document.getElementById('total-photos').textContent = 'Loading...';
    
    const response = await fetch('/assets/data/gallery.json');
    galleryData = await response.json();
    
    // Update category counts
    updateCategoryCounts();
    updateYearCounts();
    updateTotalCount();
  } catch (error) {
    console.error('Error loading gallery data:', error);
    document.getElementById('total-photos').textContent = 'Error loading';
  }
}

// Update category counts dynamically
function updateCategoryCounts() {
  if (!galleryData) return;
  
  const categoryCounts = {
    'photos': galleryData.categories['Photos']?.length || 0,
    'championships': galleryData.categories['Championships']?.length || 0,
    'regattas': galleryData.categories['Regattas']?.length || 0,
    'frostbite': galleryData.categories['Frostbite']?.length || 0,
    'tayc': galleryData.categories['TAYC']?.length || 0,
    'cryc': galleryData.categories['CRYC']?.length || 0,
    'giys': galleryData.categories['GIYS']?.length || 0,
    'beachwood': galleryData.categories['Beachwood']?.length || 0,
    'awards': galleryData.categories['Awards']?.length || 0,
    'heritage': galleryData.categories['Heritage']?.length || 0,
    'boats': galleryData.categories['Boats']?.length || 0
  };
  
  // Update each category count
  for (const [category, count] of Object.entries(categoryCounts)) {
    const element = document.getElementById(`${category}-count`);
    if (element) {
      if (category === 'photos') {
        element.textContent = `${count} photos from all events and activities`;
      } else {
        element.textContent = `${count} photos from ${category} events`;
      }
    }
  }
}

// Update year counts dynamically
function updateYearCounts() {
  if (!galleryData) return;
  
  const yearButtons = document.querySelectorAll('.year-link');
  yearButtons.forEach(button => {
    const year = button.textContent.match(/\d{4}/)?.[0];
    if (year && galleryData.years[year]) {
      const count = galleryData.years[year].length;
      button.textContent = `${year} (${count} photos)`;
    }
  });
}

// Update total count
function updateTotalCount() {
  if (!galleryData) return;
  
  const totalElement = document.getElementById('total-photos');
  if (totalElement) {
    totalElement.textContent = galleryData.stats.total_media;
  }
}

// View photos by category
function viewCategory(category) {
  if (!galleryData) {
    alert('Gallery data not loaded yet. Please try again.');
    return;
  }
  
  // Map lowercase category names to actual category names in the data
  const categoryMap = {
    'championships': 'Championships',
    'regattas': 'Regattas', 
    'frostbite': 'Frostbite',
    'tayc': 'TAYC',
    'cryc': 'CRYC',
    'giys': 'GIYS',
    'beachwood': 'Beachwood',
    'awards': 'Awards',
    'heritage': 'Heritage',
    'boats': 'Boats',
    'general': 'General',
    'photos': 'Photos',
    'videos': 'Videos',
    'external_videos': 'External Videos'
  };
  
  const actualCategory = categoryMap[category] || category;
  const categoryData = galleryData.categories[actualCategory];
  
  if (!categoryData || categoryData.length === 0) {
    alert(`No photos found for category: ${actualCategory}`);
    return;
  }
  
  currentPhotos = categoryData;
  currentPhotoIndex = 0;
  showPhotoViewer(actualCategory);
}

// View photos by year
function viewYear(year) {
  if (!galleryData) {
    alert('Gallery data not loaded yet. Please try again.');
    return;
  }
  
  const yearData = galleryData.years[year];
  if (!yearData || yearData.length === 0) {
    alert('No photos found for this year.');
    return;
  }
  
  currentPhotos = yearData;
  currentPhotoIndex = 0;
  showPhotoViewer(`Photos from ${year}`);
}

// Show photo viewer
function showPhotoViewer(title) {
  const viewer = document.getElementById('gallery-photo-viewer');
  
  if (!viewer) {
    console.error('Photo viewer element not found in DOM!');
    alert('Photo viewer element not found. Please check the HTML structure.');
    return;
  }
  
  document.getElementById('viewer-title').textContent = title;
  
  // Make sure viewer is visible
  viewer.style.display = 'flex';
  viewer.style.visibility = 'visible';
  viewer.style.opacity = '1';
  viewer.style.background = 'rgba(0, 0, 0, 0.95)';
  viewer.style.position = 'fixed';
  viewer.style.top = '0';
  viewer.style.left = '0';
  viewer.style.width = '100vw';
  viewer.style.height = '100vh';
  viewer.style.zIndex = '9999';
  
  updatePhotoDisplay();
  updateThumbnails();
}

// Close photo viewer
function closeViewer() {
  document.getElementById('gallery-photo-viewer').style.display = 'none';
}

// Update photo display
function updatePhotoDisplay() {
  if (currentPhotos.length === 0) {
    return;
  }
  
  const photo = currentPhotos[currentPhotoIndex];
  const img = document.getElementById('current-photo');
  const filename = document.getElementById('photo-filename');
  const details = document.getElementById('photo-details');
  const credit = document.getElementById('photo-credit');
  const counter = document.getElementById('photo-counter');
  const container = document.querySelector('.photo-container');
  
  if (!img) {
    console.error('Image element not found!');
    return;
  }
  
  // Ensure container is properly styled
  if (container) {
    container.style.background = 'transparent';
    container.style.border = 'none';
  }
  
  // Ensure absolute URLs for photos using encoded path
  const photoUrl = photo.encoded_path.startsWith('/') ? photo.encoded_path : '/' + photo.encoded_path;
  
  img.src = photoUrl;
  img.alt = photo.filename;
  
  // Ensure image is visible
  img.style.display = 'block';
  img.style.visibility = 'visible';
  img.style.opacity = '1';
  img.style.maxWidth = '100%';
  img.style.maxHeight = '100%';
  img.style.objectFit = 'contain';
  img.style.width = 'auto';
  img.style.height = 'auto';
  
  filename.textContent = photo.filename;
  details.textContent = `Size: ${Math.round(photo.size / 1024)} KB | Year: ${photo.year || 'Unknown'} | Source: ${photo.source}`;
  credit.textContent = `Credit: ${photo.credit || 'Unknown photographer'}`;
  counter.textContent = `${currentPhotoIndex + 1} of ${currentPhotos.length}`;
  
  // Update thumbnail selection
  const thumbnails = document.querySelectorAll('.photo-thumbnails img');
  thumbnails.forEach((thumb, index) => {
    thumb.classList.toggle('active', index === currentPhotoIndex);
  });
}

// Update thumbnails
function updateThumbnails() {
  const container = document.getElementById('photo-thumbnails');
  container.innerHTML = '';
  
  currentPhotos.forEach((photo, index) => {
    const img = document.createElement('img');
    // Ensure absolute URLs for thumbnails using encoded path
    const photoUrl = photo.encoded_path.startsWith('/') ? photo.encoded_path : '/' + photo.encoded_path;
    img.src = photoUrl;
    img.alt = photo.filename;
    img.onclick = () => {
      currentPhotoIndex = index;
      updatePhotoDisplay();
    };
    container.appendChild(img);
  });
}

// Navigation functions
function previousPhoto() {
  if (currentPhotoIndex > 0) {
    currentPhotoIndex--;
    updatePhotoDisplay();
  }
}

function nextPhoto() {
  if (currentPhotoIndex < currentPhotos.length - 1) {
    currentPhotoIndex++;
    updatePhotoDisplay();
  }
}

// Keyboard navigation
document.addEventListener('keydown', function(e) {
  const viewer = document.getElementById('gallery-photo-viewer');
  if (viewer.style.display === 'none') return;
  
  switch(e.key) {
    case 'Escape':
      closeViewer();
      break;
    case 'ArrowLeft':
      previousPhoto();
      break;
    case 'ArrowRight':
      nextPhoto();
      break;
  }
});

// Search functionality
function performSearch(query) {
  const searchResults = document.getElementById('search-results');
  
  if (!query.trim()) {
    searchResults.innerHTML = '<p>Enter a search term to find photos or video by category, year, or event.</p>';
    return;
  }
  
  if (!galleryData) {
    searchResults.innerHTML = '<p>Gallery data not loaded yet.</p>';
    return;
  }
  
  const results = [];
  const queryLower = query.toLowerCase();
  
  // Search categories
  for (const [category, photos] of Object.entries(galleryData.categories)) {
    if (category.toLowerCase().includes(queryLower)) {
      // Map back to lowercase for the viewCategory function
      const categoryKey = category.toLowerCase();
      results.push(`<div class="search-result-item"><strong>${category}</strong> - ${photos.length} photos <button onclick="viewCategory('${categoryKey}')">View Photos</button></div>`);
    }
  }
  
  // Search years
  for (const [year, photos] of Object.entries(galleryData.years)) {
    if (year.includes(query)) {
      results.push(`<div class="search-result-item"><strong>${year}</strong> - ${photos.length} photos <button onclick="viewYear('${year}')">View Photos</button></div>`);
    }
  }
  
  if (results.length === 0) {
    searchResults.innerHTML = '<p>No results found. Try searching for categories like "Championships", "TAYC", or years like "2024".</p>';
  } else {
    searchResults.innerHTML = results.join('');
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
  loadGalleryData();
  
  // Set up both search inputs
  const searchInputUpper = document.getElementById('search-input-upper');
  const searchInputLower = document.getElementById('search-input-lower');
  
  function handleSearch(e) {
    performSearch(e.target.value);
  }
  
  if (searchInputUpper) {
    searchInputUpper.addEventListener('input', handleSearch);
  }
  
  if (searchInputLower) {
    searchInputLower.addEventListener('input', handleSearch);
  }
  
  // Initialize search results
  performSearch('');
});
</script>