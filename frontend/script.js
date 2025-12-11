// Configuration
const API_BASE_URL = 'http://localhost:8000/api';
let currentPage = 1;
let currentPerPage = 20;
let currentFilters = {};
let totalRecipes = 0;
let totalPages = 1;

// DOM Elements
const tableBody = document.getElementById('recipesTableBody');
const searchInput = document.getElementById('searchInput');
const minRating = document.getElementById('minRating');
const ratingValue = document.getElementById('ratingValue');
const maxCalories = document.getElementById('maxCalories');
const maxTime = document.getElementById('maxTime');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const pageInfo = document.getElementById('pageInfo');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateRatingDisplay();
    loadStats();
    loadRecipes();
    
    // Event listeners
    minRating.addEventListener('input', updateRatingDisplay);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchRecipes();
    });
});

// Update rating display
function updateRatingDisplay() {
    ratingValue.textContent = `${minRating.value}+`;
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('totalRecipes').textContent = data.total_recipes.toLocaleString();
            document.getElementById('avgRating').textContent = data.avg_rating;
            document.getElementById('avgTime').textContent = `${data.avg_time} min`;
            document.getElementById('footerCount').textContent = data.total_recipes.toLocaleString();
            totalRecipes = data.total_recipes;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load recipes
async function loadRecipes(page = 1, filters = {}) {
    try {
        tableBody.innerHTML = `
            <tr class="loading-row">
                <td colspan="7">
                    <i class="fas fa-spinner fa-spin"></i> Loading recipes...
                </td>
            </tr>
        `;
        
        const params = new URLSearchParams({
            page: page,
            per_page: currentPerPage,
            ...filters
        });
        
        const url = Object.keys(filters).length === 0 
            ? `${API_BASE_URL}/recipes?${params}`
            : `${API_BASE_URL}/recipes/search?${params}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            displayRecipes(data.data);
            updatePagination(data.pagination);
        } else {
            throw new Error(data.error || 'Failed to load recipes');
        }
    } catch (error) {
        console.error('Error loading recipes:', error);
        tableBody.innerHTML = `
            <tr class="empty-row">
                <td colspan="7">
                    <i class="fas fa-exclamation-triangle"></i>
                    Error loading recipes: ${error.message}
                </td>
            </tr>
        `;
    }
}

// Display recipes in table
function displayRecipes(recipes) {
    if (!recipes || recipes.length === 0) {
        tableBody.innerHTML = `
            <tr class="empty-row">
                <td colspan="7">
                    <i class="fas fa-search"></i>
                    No recipes found. Try different filters.
                </td>
            </tr>
        `;
        return;
    }
    
    let tableHTML = '';
    
    recipes.forEach((recipe, index) => {
        const calories = recipe.nutrients?.calories || 'N/A';
        const stars = createStars(recipe.rating || 0);
        const totalTime = recipe.total_time || 'N/A';
        
        tableHTML += `
            <tr data-recipe-id="${index}">
                <td>
                    <strong>${recipe.title || 'Untitled Recipe'}</strong>
                    ${recipe.description ? `<br><small style="color: #64748b;">${truncateText(recipe.description, 60)}</small>` : ''}
                </td>
                <td>${recipe.cuisine || 'N/A'}</td>
                <td>
                    <span class="rating-stars">${stars}</span>
                    <span class="rating-value">${recipe.rating || 'N/A'}</span>
                </td>
                <td>${totalTime} min</td>
                <td>${recipe.serves || 'N/A'}</td>
                <td>${calories}</td>
                <td>
                    <button class="expand-btn" onclick="toggleRowDetails(this, ${index})">
                        <i class="fas fa-chevron-down"></i> Details
                    </button>
                </td>
            </tr>
            <tr id="details-${index}" class="expandable-details">
                <td colspan="7">
                    <div class="detail-grid">
                        ${createDetailsHTML(recipe)}
                    </div>
                </td>
            </tr>
        `;
    });
    
    tableBody.innerHTML = tableHTML;
}

// Create stars HTML
function createStars(rating) {
    let stars = '';
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    
    for (let i = 0; i < 5; i++) {
        if (i < fullStars) {
            stars += '<i class="fas fa-star"></i>';
        } else if (i === fullStars && hasHalfStar) {
            stars += '<i class="fas fa-star-half-alt"></i>';
        } else {
            stars += '<i class="far fa-star"></i>';
        }
    }
    
    return stars;
}

// Create details HTML
function createDetailsHTML(recipe) {
    const nutrients = recipe.nutrients || {};
    const prepTime = recipe.prep_time || 0;
    const cookTime = recipe.cook_time || 0;
    
    // Filter out empty nutrients
    const nutrientItems = Object.entries(nutrients)
        .filter(([key, value]) => value && value !== '0 g' && value !== '0 mg' && value !== '0 kcal')
        .map(([key, value]) => `
            <div class="nutrient-item">
                <span class="nutrient-key">${formatNutrientKey(key)}</span>
                <span class="nutrient-value">${value}</span>
            </div>
        `).join('');
    
    return `
        <div class="detail-section">
            <h3><i class="fas fa-info-circle"></i> Description</h3>
            <p>${recipe.description || 'No description available.'}</p>
        </div>
        
        <div class="detail-section">
            <h3><i class="fas fa-fire"></i> Nutrition Facts</h3>
            ${nutrientItems ? `
                <div class="nutrients-grid">
                    ${nutrientItems}
                </div>
            ` : '<p>No nutrition information available.</p>'}
        </div>
        
        <div class="detail-section">
            <h3><i class="fas fa-clock"></i> Time Breakdown</h3>
            <div class="time-breakdown">
                <div class="time-item">
                    <i class="fas fa-hourglass-start"></i>
                    <span>Prep</span>
                    <strong>${prepTime} min</strong>
                </div>
                <div class="time-item">
                    <i class="fas fa-hourglass-half"></i>
                    <span>Cook</span>
                    <strong>${cookTime} min</strong>
                </div>
                <div class="time-item">
                    <i class="fas fa-hourglass-end"></i>
                    <span>Total</span>
                    <strong>${recipe.total_time || prepTime + cookTime || 0} min</strong>
                </div>
            </div>
        </div>
    `;
}

// Toggle row details
function toggleRowDetails(button, index) {
    const detailsRow = document.getElementById(`details-${index}`);
    const isExpanded = detailsRow.classList.contains('show');
    const icon = button.querySelector('i');
    
    if (isExpanded) {
        detailsRow.classList.remove('show');
        icon.className = 'fas fa-chevron-down';
        button.innerHTML = '<i class="fas fa-chevron-down"></i> Details';
        button.parentElement.parentElement.classList.remove('expanded');
    } else {
        // Close any other open rows
        document.querySelectorAll('.expandable-details.show').forEach(row => {
            row.classList.remove('show');
            const btn = row.previousElementSibling.querySelector('.expand-btn');
            if (btn) {
                btn.innerHTML = '<i class="fas fa-chevron-down"></i> Details';
                btn.parentElement.parentElement.classList.remove('expanded');
            }
        });
        
        detailsRow.classList.add('show');
        icon.className = 'fas fa-chevron-up';
        button.innerHTML = '<i class="fas fa-chevron-up"></i> Hide';
        button.parentElement.parentElement.classList.add('expanded');
        
        // Scroll to the expanded row
        detailsRow.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

// Helper functions
function truncateText(text, maxLength) {
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

function formatNutrientKey(key) {
    const keyMap = {
        'calories': 'Calories',
        'carbohydrateContent': 'Carbs',
        'cholesterolContent': 'Cholesterol',
        'fiberContent': 'Fiber',
        'proteinContent': 'Protein',
        'saturatedFatContent': 'Saturated Fat',
        'sodiumContent': 'Sodium',
        'sugarContent': 'Sugar',
        'fatContent': 'Fat',
        'unsaturatedFatContent': 'Unsaturated Fat'
    };
    
    return keyMap[key] || key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
}

// Search recipes
function searchRecipes() {
    currentPage = 1;
    currentFilters = {};
    
    const query = searchInput.value.trim();
    if (query) currentFilters.query = query;
    
    const rating = parseFloat(minRating.value);
    if (rating > 0) currentFilters.min_rating = rating;
    
    const calories = maxCalories.value.trim();
    if (calories) currentFilters.max_calories = parseInt(calories);
    
    const time = maxTime.value.trim();
    if (time) currentFilters.max_total_time = parseInt(time);
    
    loadRecipes(currentPage, currentFilters);
}

// Clear filters
function clearFilters() {
    searchInput.value = '';
    minRating.value = 0;
    maxCalories.value = '';
    maxTime.value = '';
    updateRatingDisplay();
    currentFilters = {};
    currentPage = 1;
    loadRecipes();
}

// Change page
function changePage(direction) {
    const newPage = currentPage + direction;
    if (newPage >= 1 && newPage <= totalPages) {
        currentPage = newPage;
        loadRecipes(currentPage, currentFilters);
    }
}

// Update pagination
function updatePagination(pagination) {
    currentPage = pagination.page || 1;
    totalPages = pagination.total_pages || 1;
    
    pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    prevBtn.disabled = !pagination.has_prev;
    nextBtn.disabled = !pagination.has_next;
}