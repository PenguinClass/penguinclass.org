---
layout: page
title: Gallery
permalink: /gallery/
---

Welcome to the Penguin Class Gallery! This collection contains **<span id="total-photos-welcome">Loading...</span> unique photos and videos** from events, regattas, and activities spanning decades of Penguin Class history.  There are also links and information at the bottom of this page if you are looking for or able to provide additional photos.

## Search

<div class="gallery-search">
  <input type="text" id="search-input-upper" placeholder="Search photos by filename, event, or year..." />
</div>
<div id="search-results" class="search-results"></div>

## 📁 Browse by Category

<div class="gallery-browse-section">
  <button class="browse-btn" onclick="viewCategory('photos')" id="photos-btn">All Photos (1145)</button>
  <button class="browse-btn" onclick="viewCategory('championships')" id="championships-btn">Championships (307)</button>
  <button class="browse-btn" onclick="viewCategory('regattas')" id="regattas-btn">Regattas (173)</button>
  <button class="browse-btn" onclick="viewCategory('tred_avon_yacht_club')" id="tred_avon_yacht_club-btn">Tred Avon Yacht Club (104)</button>
  <button class="browse-btn" onclick="viewCategory('beachwood_yacht_club')" id="beachwood_yacht_club-btn">Beachwood Yacht Club (88)</button>
  <button class="browse-btn" onclick="viewCategory('frostbite')" id="frostbite-btn">Frostbite (64)</button>
  <button class="browse-btn" onclick="viewCategory('gibson_island_yacht_squadron')" id="gibson_island_yacht_squadron-btn">Gibson Island Yacht Squadron (28)</button>
  <button class="browse-btn" onclick="viewCategory('awards')" id="awards-btn">Awards (21)</button>
  <button class="browse-btn" onclick="viewCategory('corsica_river_yacht_club')" id="corsica_river_yacht_club-btn">Corsica River Yacht Club (20)</button>
  <button class="browse-btn" onclick="viewCategory('heritage')" id="heritage-btn">Heritage (3)</button>
  <button class="browse-btn" onclick="viewCategory('boats')" id="boats-btn">Boats (2)</button>
</div>

## 📅 Browse by Year

<div class="gallery-browse-section">
  <div class="decade-section" data-decade="2020">
    <h3 class="decade-title">📅 2020-2029</h3>
    <div class="year-grid">
      <button class="browse-btn year-btn" onclick="viewYear('2021')">2021 (38)</button>
      <button class="browse-btn year-btn" onclick="viewYear('2022')">2022 (11)</button>
      <button class="browse-btn year-btn" onclick="viewYear('2023')">2023 (34)</button>
      <button class="browse-btn year-btn" onclick="viewYear('2024')">2024 (28)</button>
      <button class="browse-btn year-btn" onclick="viewYear('2025')">2025 (72)</button>
    </div>
  </div>
  <div class="decade-section" data-decade="2010">
    <h3 class="decade-title">📅 2010-2019</h3>
    <div class="year-grid">
      <button class="browse-btn year-btn" onclick="viewYear('2010')">2010 (33)</button>
      <button class="browse-btn year-btn" onclick="viewYear('2011')">2011 (2)</button>
      <button class="browse-btn year-btn" onclick="viewYear('2012')">2012 (2)</button>
      <button class="browse-btn year-btn" onclick="viewYear('2014')">2014 (3)</button>
      <button class="browse-btn year-btn" onclick="viewYear('2016')">2016 (10)</button>
    </div>
  </div>
  <div class="decade-section" data-decade="2000">
    <h3 class="decade-title">📅 2000-2009</h3>
    <div class="year-grid">
      <button class="browse-btn year-btn" onclick="viewYear('2006')">2006 (21)</button>
      <button class="browse-btn year-btn" onclick="viewYear('2008')">2008 (3)</button>
    </div>
  </div>
  <div class="decade-section" data-decade="1950">
    <h3 class="decade-title">📅 1950s</h3>
    <div class="year-grid">
      <button class="browse-btn year-btn" onclick="viewYear('1955')">1955 (1)</button>
    </div>
  </div>
</div>

## 👤 Browse by Creator

<div class="gallery-browse-section">
  <button class="browse-btn" onclick="viewCreator('unknown_photographer')" id="unknown_photographer-btn">Unknown photographer (965)</button>
  <button class="browse-btn" onclick="viewCreator('will_keyworth')" id="will_keyworth-btn">Will Keyworth (53)</button>
  <button class="browse-btn" onclick="viewCreator('frank_parisi')" id="frank_parisi-btn">Frank Parisi (49)</button>
  <button class="browse-btn" onclick="viewCreator('paul_rohrkemper')" id="paul_rohrkemper-btn">Paul Rohrkemper (40)</button>
  <button class="browse-btn" onclick="viewCreator('al_schreitmueller')" id="al_schreitmueller-btn">Al Schreitmueller (37)</button>
  <button class="browse-btn" onclick="viewCreator('joe_della_barba')" id="joe_della_barba-btn">Joe Della Barba (10)</button>
  <button class="browse-btn" onclick="viewCreator('penoso')" id="penoso-btn">Penoso (1)</button>
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

- **Total Photos**: <span id="total-photos-info">Loading...</span> unique images
- **Date Range**: 1955 - 2025
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
    document.getElementById('total-photos-welcome').textContent = 'Loading...';
    document.getElementById('total-photos-info').textContent = 'Loading...';    
    
    const response = await fetch('/assets/data/gallery.json');
    galleryData = await response.json();
    
    // Update category counts
    updateCategoryCounts();
    updateYearCounts();
    updateTotalCount();
  } catch (error) {
    console.error('Error loading gallery data:', error);
    document.getElementById('total-photos-welcome').textContent = 'Error loading';
    document.getElementById('total-photos-info').textContent = 'Error loading';    
  }
}

// Update category counts dynamically
function updateCategoryCounts() {
  if (!galleryData) return;
  
  const categoryCounts = {
    'photos': galleryData.categories['Photos']?.length || 0,
    'awards': galleryData.categories['Awards']?.length || 0,
    'beachwood_yacht_club': galleryData.categories['Beachwood Yacht Club']?.length || 0,
    'boats': galleryData.categories['Boats']?.length || 0,
    'championships': galleryData.categories['Championships']?.length || 0,
    'corsica_river_yacht_club': galleryData.categories['Corsica River Yacht Club']?.length || 0,
    'frostbite': galleryData.categories['Frostbite']?.length || 0,
    'gibson_island_yacht_squadron': galleryData.categories['Gibson Island Yacht Squadron']?.length || 0,
    'heritage': galleryData.categories['Heritage']?.length || 0,
    'regattas': galleryData.categories['Regattas']?.length || 0,
    'tred_avon_yacht_club': galleryData.categories['Tred Avon Yacht Club']?.length || 0,
  };
  
  // Update button text with counts
  for (const [category, count] of Object.entries(categoryCounts)) {
    const button = document.getElementById(`${category}-btn`);
    if (button) {
      if (category === 'photos') {
        button.textContent = `All Photos (${count})`;
      } else {
        const categoryName = button.textContent.split(' (')[0];
        button.textContent = `${categoryName} (${count})`;
      }
    }
  }
}

function updateCreatorCounts() {
  if (!galleryData) return;
  
  // Group media by creator/credit
  const creators = {};
  galleryData.media_index.forEach(item => {
    const credit = item.credit || 'Unknown photographer';
    if (!creators[credit]) creators[credit] = [];
    creators[credit].push(item);
  });
  
  // Update creator button text with counts
  for (const [creator, items] of Object.entries(creators)) {
    const creatorId = creator.toLowerCase().replace(/[^a-z0-9]/g, '_');
    const button = document.getElementById(`${creatorId}-btn`);
    if (button) {
      button.textContent = `${creator} (${items.length})`;
    }
  }
}

function updateCreatorCounts() {
  if (!galleryData) return;
  
  // Group media by creator/credit
  const creators = {};
  galleryData.media_index.forEach(item => {
    const credit = item.credit || 'Unknown photographer';
    if (!creators[credit]) creators[credit] = [];
    creators[credit].push(item);
  });
  
  // Update creator button text with counts
  for (const [creator, items] of Object.entries(creators)) {
    const creatorId = creator.toLowerCase().replace(/[^a-z0-9]/g, '_');
    const button = document.getElementById(`${creatorId}-btn`);
    if (button) {
      button.textContent = `${creator} (${items.length})`;
    }
  }
}

function updateCreatorCounts() {
  if (!galleryData) return;
  
  // Group media by creator/credit
  const creators = {};
  galleryData.media_index.forEach(item => {
    const credit = item.credit || 'Unknown photographer';
    if (!creators[credit]) creators[credit] = [];
    creators[credit].push(item);
  });
  
  // Update creator button text with counts
  for (const [creator, items] of Object.entries(creators)) {
    const creatorId = creator.toLowerCase().replace(/[^a-z0-9]/g, '_');
    const button = document.getElementById(`${creatorId}-btn`);
    if (button) {
      button.textContent = `${creator} (${items.length})`;
    }
  }
}

function updateCreatorCounts() {
  if (!galleryData) return;
  
  // Group media by creator/credit
  const creators = {};
  galleryData.media_index.forEach(item => {
    const credit = item.credit || 'Unknown photographer';
    if (!creators[credit]) creators[credit] = [];
    creators[credit].push(item);
  });
  
  // Update creator counts
  for (const [creator, items] of Object.entries(creators)) {
    const creatorId = creator.toLowerCase().replace(/[^a-z0-9]/g, '_');
    const element = document.getElementById(`${creatorId}-count`);
    if (element) {
      element.textContent = `${items.length} photos`;
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
  
  const totalElementWelcome = document.getElementById('total-photos-welcome');
  if (totalElementWelcome) {
    totalElementWelcome.textContent = galleryData.stats.total_media;
  }
  const totalElementInfo = document.getElementById('total-photos-info');
  if (totalElementInfo) {
    totalElementInfo.textContent = galleryData.stats.total_media;
  }
}

// View photos by category
function viewCategory(category) {
  if (!galleryData) {
    alert('Gallery data not loaded yet. Please try again.');
    return;
  }
  
  // Map lowercase category names to actual category names in the data
    // Map lowercase category names to actual category names in the data
    // Map lowercase category names to actual category names in the data
    // Map lowercase category names to actual category names in the data
    // Map lowercase category names to actual category names in the data
    // Map lowercase category names to actual category names in the data
    // Map lowercase category names to actual category names in the data
    // Map lowercase category names to actual category names in the data
    // Map lowercase category names to actual category names in the data
  const categoryMap = {
    'photos': 'Photos',
    'gibson_island_yacht_squadron': 'Gibson Island Yacht Squadron',
    'corsica_river_yacht_club': 'Corsica River Yacht Club',
    'boats': 'Boats',
    'beachwood_yacht_club': 'Beachwood Yacht Club',
    'championships': 'Championships',
    'regattas': 'Regattas',
    'frostbite': 'Frostbite',
    'tred_avon_yacht_club': 'Tred Avon Yacht Club',
    'awards': 'Awards',
    'heritage': 'Heritage',
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

// View photos by creator
function viewCreator(creator) {
  if (!galleryData) {
    alert('Gallery data not loaded yet. Please try again.');
    return;
  }
  
  // Find photos by this creator
  const creatorPhotos = [];
  for (const item of galleryData.media_index) {
    const credit = item.credit || 'Unknown photographer';
    const creatorId = credit.toLowerCase().replace(' ', '_').replace(',', '').replace('.', '').replace('(', '').replace(')', '');
    if (creatorId === creator) {
      creatorPhotos.push(item);
    }
  }
  
  if (creatorPhotos.length === 0) {
    alert('No photos found for this creator.');
    return;
  }
  
  currentPhotos = creatorPhotos;
  currentPhotoIndex = 0;
  showPhotoViewer(`Photos by ${creatorPhotos[0].credit}`);
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
    }
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