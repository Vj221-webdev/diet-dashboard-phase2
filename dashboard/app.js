// Configuration
let API_BASE_URL = 'https://dietfunctionvijay.azurewebsites.net/api'; // Default for local testing
let currentPage = 1;
let chartInstances = {};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Check if API URL is saved in localStorage
    const savedApiUrl = localStorage.getItem('apiBaseUrl');
    if (savedApiUrl) {
        API_BASE_URL = savedApiUrl;
        loadDashboardData();
    } else {
        showConfigModal();
    }
    
    // Setup event listeners
    setupEventListeners();
});

// Show configuration modal
function showConfigModal() {
    const modal = document.getElementById('configModal');
    modal.classList.add('show');
    
    document.getElementById('saveApiUrl').addEventListener('click', () => {
        const apiUrl = document.getElementById('apiUrlInput').value.trim();
        if (apiUrl) {
            API_BASE_URL = apiUrl;
            localStorage.setItem('apiBaseUrl', apiUrl);
            modal.classList.remove('show');
            loadDashboardData();
        } else {
            alert('Please enter a valid API URL');
        }
    });
}

// Setup event listeners
function setupEventListeners() {
    // Filter changes
    document.getElementById('dietTypeFilter').addEventListener('change', handleFilterChange);
    document.getElementById('searchInput').addEventListener('input', handleSearchInput);
    
    // API buttons
    document.getElementById('btnNutritionalInsights').addEventListener('click', () => {
        fetchAndDisplayApiData('nutritional-insights');
    });
    
    document.getElementById('btnRecipes').addEventListener('click', () => {
        fetchRecipes();
    });
    
    document.getElementById('btnClusters').addEventListener('click', () => {
        fetchAndDisplayApiData('clusters');
    });
    
    // Pagination
    document.getElementById('prevBtn').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            fetchRecipes();
        }
    });
    
    document.getElementById('nextBtn').addEventListener('click', () => {
        currentPage++;
        fetchRecipes();
    });
}

// Load all dashboard data
async function loadDashboardData() {
    showLoading(true);
    
    try {
        await Promise.all([
            loadBarChart(),
            loadScatterChart(),
            loadHeatmapChart(),
            loadPieChart()
        ]);
        
        hideError();
    } catch (error) {
        showError(`Failed to load dashboard data: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// Load Bar Chart (Average Macronutrients)
async function loadBarChart() {
    try {
        const response = await fetch(`${API_BASE_URL}/nutritional-insights`);
        const data = await response.json();
        
        const ctx = document.getElementById('barChart').getContext('2d');
        
        // Destroy existing chart if exists
        if (chartInstances.barChart) {
            chartInstances.barChart.destroy();
        }
        
        chartInstances.barChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.diet_types,
                datasets: [
                    {
                        label: 'Protein (g)',
                        data: data.protein,
                        backgroundColor: 'rgba(59, 130, 246, 0.7)',
                        borderColor: 'rgba(59, 130, 246, 1)',
                        borderWidth: 2
                    },
                    {
                        label: 'Carbs (g)',
                        data: data.carbs,
                        backgroundColor: 'rgba(16, 185, 129, 0.7)',
                        borderColor: 'rgba(16, 185, 129, 1)',
                        borderWidth: 2
                    },
                    {
                        label: 'Fat (g)',
                        data: data.fat,
                        backgroundColor: 'rgba(251, 146, 60, 0.7)',
                        borderColor: 'rgba(251, 146, 60, 1)',
                        borderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Grams'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Diet Type'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading bar chart:', error);
        throw error;
    }
}

// Load Scatter Chart (Protein vs Carbs)
async function loadScatterChart() {
    try {
        const response = await fetch(`${API_BASE_URL}/scatter-data?limit=100`);
        const data = await response.json();
        
        const ctx = document.getElementById('scatterChart').getContext('2d');
        
        // Destroy existing chart if exists
        if (chartInstances.scatterChart) {
            chartInstances.scatterChart.destroy();
        }
        
        // Group data by diet type for different colors
        const dietTypes = [...new Set(data.data.map(d => d.diet_type))];
        const colors = {
            'paleo': 'rgba(239, 68, 68, 0.6)',
            'keto': 'rgba(59, 130, 246, 0.6)',
            'vegan': 'rgba(16, 185, 129, 0.6)',
            'mediterranean': 'rgba(251, 146, 60, 0.6)',
            'dash': 'rgba(139, 92, 246, 0.6)'
        };
        
        const datasets = dietTypes.map(dietType => {
            const filteredData = data.data.filter(d => d.diet_type === dietType);
            return {
                label: dietType.charAt(0).toUpperCase() + dietType.slice(1),
                data: filteredData.map(d => ({ x: d.carbs, y: d.protein })),
                backgroundColor: colors[dietType] || 'rgba(107, 114, 128, 0.6)',
                pointRadius: 5,
                pointHoverRadius: 7
            };
        });
        
        chartInstances.scatterChart = new Chart(ctx, {
            type: 'scatter',
            data: { datasets },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: Protein ${context.parsed.y}g, Carbs ${context.parsed.x}g`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Carbohydrates (g)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Protein (g)'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading scatter chart:', error);
        throw error;
    }
}

// Load Heatmap Chart (Nutrient Correlations)
async function loadHeatmapChart() {
    try {
        const response = await fetch(`${API_BASE_URL}/heatmap-data`);
        const data = await response.json();
        
        const ctx = document.getElementById('heatmapChart').getContext('2d');
        
        // Destroy existing chart if exists
        if (chartInstances.heatmapChart) {
            chartInstances.heatmapChart.destroy();
        }
        
        // Convert correlation matrix to heatmap data
        const heatmapData = [];
        data.data.forEach((row, i) => {
            row.forEach((value, j) => {
                heatmapData.push({
                    x: data.labels[j],
                    y: data.labels[i],
                    v: value
                });
            });
        });
        
        // Create a pseudo-heatmap using a bubble chart
        chartInstances.heatmapChart = new Chart(ctx, {
            type: 'bubble',
            data: {
                datasets: [{
                    label: 'Correlation',
                    data: heatmapData.map(d => ({
                        x: data.labels.indexOf(d.x),
                        y: data.labels.indexOf(d.y),
                        r: Math.abs(d.v) * 20 + 10,
                        correlation: d.v
                    })),
                    backgroundColor: heatmapData.map(d => {
                        const value = d.v;
                        if (value > 0.5) return 'rgba(239, 68, 68, 0.7)';
                        if (value > 0) return 'rgba(251, 146, 60, 0.7)';
                        if (value > -0.5) return 'rgba(59, 130, 246, 0.7)';
                        return 'rgba(16, 185, 129, 0.7)';
                    })
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const xLabel = data.labels[context.parsed.x];
                                const yLabel = data.labels[context.parsed.y];
                                const corr = context.raw.correlation.toFixed(2);
                                return `${xLabel} vs ${yLabel}: ${corr}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        min: -0.5,
                        max: 2.5,
                        ticks: {
                            callback: function(value) {
                                return data.labels[Math.round(value)] || '';
                            }
                        }
                    },
                    y: {
                        min: -0.5,
                        max: 2.5,
                        ticks: {
                            callback: function(value) {
                                return data.labels[Math.round(value)] || '';
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading heatmap chart:', error);
        throw error;
    }
}

// Load Pie Chart (Recipe Distribution)
async function loadPieChart() {
    try {
        const response = await fetch(`${API_BASE_URL}/pie-chart-data`);
        const data = await response.json();
        
        const ctx = document.getElementById('pieChart').getContext('2d');
        
        // Destroy existing chart if exists
        if (chartInstances.pieChart) {
            chartInstances.pieChart.destroy();
        }
        
        chartInstances.pieChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: [
                        'rgba(59, 130, 246, 0.7)',
                        'rgba(16, 185, 129, 0.7)',
                        'rgba(251, 146, 60, 0.7)',
                        'rgba(139, 92, 246, 0.7)',
                        'rgba(239, 68, 68, 0.7)'
                    ],
                    borderColor: [
                        'rgba(59, 130, 246, 1)',
                        'rgba(16, 185, 129, 1)',
                        'rgba(251, 146, 60, 1)',
                        'rgba(139, 92, 246, 1)',
                        'rgba(239, 68, 68, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'right',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = data.total;
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading pie chart:', error);
        throw error;
    }
}

// Handle filter changes
async function handleFilterChange() {
    const dietType = document.getElementById('dietTypeFilter').value;
    
    showLoading(true);
    
    try {
        // Reload bar chart with filter
        const response = await fetch(`${API_BASE_URL}/nutritional-insights?diet_type=${dietType}`);
        const data = await response.json();
        
        if (chartInstances.barChart) {
            chartInstances.barChart.data.labels = data.diet_types;
            chartInstances.barChart.data.datasets[0].data = data.protein;
            chartInstances.barChart.data.datasets[1].data = data.carbs;
            chartInstances.barChart.data.datasets[2].data = data.fat;
            chartInstances.barChart.update();
        }
        
        // Reload scatter chart with filter
        const scatterResponse = await fetch(`${API_BASE_URL}/scatter-data?diet_type=${dietType}&limit=100`);
        await loadScatterChart();
        
    } catch (error) {
        showError(`Failed to apply filter: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// Handle search input
function handleSearchInput(event) {
    const searchTerm = event.target.value.toLowerCase();
    const selectElement = document.getElementById('dietTypeFilter');
    
    // Find matching diet type
    const options = Array.from(selectElement.options);
    const matchedOption = options.find(option => 
        option.value.toLowerCase().includes(searchTerm) && option.value !== 'all'
    );
    
    if (matchedOption) {
        selectElement.value = matchedOption.value;
        handleFilterChange();
    } else if (searchTerm === '') {
        selectElement.value = 'all';
        handleFilterChange();
    }
}

// Fetch and display API data
async function fetchAndDisplayApiData(endpoint) {
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/${endpoint}`);
        const data = await response.json();
        
        // Display response
        const apiResponse = document.getElementById('apiResponse');
        const apiResponseContent = document.getElementById('apiResponseContent');
        
        apiResponseContent.textContent = JSON.stringify(data, null, 2);
        apiResponse.classList.remove('hidden');
        
        // Scroll to response
        apiResponse.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
    } catch (error) {
        showError(`Failed to fetch data: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// Fetch recipes
async function fetchRecipes() {
    const dietType = document.getElementById('dietTypeFilter').value;
    
    showLoading(true);
    
    try {
        const response = await fetch(
            `${API_BASE_URL}/recipes?diet_type=${dietType}&page=${currentPage}&limit=20`
        );
        const data = await response.json();
        
        // Display recipes in table
        displayRecipesTable(data.recipes);
        updatePagination(data.page, data.total_pages);
        
        // Show recipes section
        document.getElementById('recipesSection').style.display = 'block';
        
        // Show API response
        const apiResponse = document.getElementById('apiResponse');
        const apiResponseContent = document.getElementById('apiResponseContent');
        apiResponseContent.textContent = JSON.stringify(data, null, 2);
        apiResponse.classList.remove('hidden');
        
    } catch (error) {
        showError(`Failed to fetch recipes: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// Display recipes in table
function displayRecipesTable(recipes) {
    const tbody = document.getElementById('recipesTableBody');
    tbody.innerHTML = '';
    
    recipes.forEach(recipe => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${recipe.recipe_name}</td>
            <td><span class="badge">${recipe.diet_type}</span></td>
            <td>${recipe.cuisine_type}</td>
            <td>${recipe.protein}</td>
            <td>${recipe.carbs}</td>
            <td>${recipe.fat}</td>
        `;
        tbody.appendChild(row);
    });
}

// Update pagination
function updatePagination(currentPageNum, totalPages) {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const paginationInfo = document.querySelector('.pagination-info');
    
    prevBtn.disabled = currentPageNum === 1;
    nextBtn.disabled = currentPageNum === totalPages;
    
    // Update page numbers
    paginationInfo.innerHTML = '';
    
    // Show first page, current page, and last page
    const pagesToShow = [1];
    if (currentPageNum > 2) pagesToShow.push(currentPageNum - 1);
    if (currentPageNum > 1 && currentPageNum < totalPages) pagesToShow.push(currentPageNum);
    if (currentPageNum < totalPages - 1) pagesToShow.push(currentPageNum + 1);
    if (totalPages > 1) pagesToShow.push(totalPages);
    
    // Remove duplicates and sort
    const uniquePages = [...new Set(pagesToShow)].sort((a, b) => a - b);
    
    uniquePages.forEach((page, index) => {
        // Add ellipsis if there's a gap
        if (index > 0 && page - uniquePages[index - 1] > 1) {
            const ellipsis = document.createElement('span');
            ellipsis.textContent = '...';
            ellipsis.style.padding = '0.5rem';
            paginationInfo.appendChild(ellipsis);
        }
        
        const pageBtn = document.createElement('button');
        pageBtn.className = 'pagination-btn';
        if (page === currentPageNum) {
            pageBtn.classList.add('active');
        }
        pageBtn.textContent = page;
        pageBtn.addEventListener('click', () => {
            currentPage = page;
            fetchRecipes();
        });
        paginationInfo.appendChild(pageBtn);
    });
}

// Utility functions
function showLoading(show) {
    const loading = document.getElementById('loading');
    if (show) {
        loading.classList.remove('hidden');
    } else {
        loading.classList.add('hidden');
    }
}

function showError(message) {
    const error = document.getElementById('error');
    error.textContent = message;
    error.classList.remove('hidden');
}

function hideError() {
    const error = document.getElementById('error');
    error.classList.add('hidden');
}
