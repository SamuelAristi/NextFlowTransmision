/**
 * JavaScript para la aplicación web de gestión de datos con WebSocket
 */

// Variables globales
let currentPage = 1;
let currentFilters = {};
let socket;
let toastElement;
let toast;

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar Socket.IO
    initializeWebSocket();

    // Inicializar Toast para notificaciones
    toastElement = document.getElementById('liveToast');
    toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 4000
    });

    // Cargar datos iniciales
    loadDashboardData();
    loadOrders();
});

// Variables globales para gestión de órdenes
let currentEditingOrderId = null;

// ===== WEBSOCKET =====

function initializeWebSocket() {
    // Conectar al servidor WebSocket
    socket = io();

    // Evento: Conexión establecida
    socket.on('connect', function() {
        console.log('✅ Conectado al servidor WebSocket');
        updateConnectionStatus(true);
        showToast('Conectado a NextFlow', 'Actualizaciones en tiempo real activas', 'success');
    });

    // Evento: Desconexión
    socket.on('disconnect', function() {
        console.log('❌ Desconectado del servidor WebSocket');
        updateConnectionStatus(false);
    });

    // Evento: Respuesta de conexión
    socket.on('connection_response', function(data) {
        console.log('Respuesta del servidor:', data);
    });

    // Evento: Actualización del dashboard
    socket.on('dashboard_update', function(data) {
        console.log('📊 Dashboard actualizado', data);
        updateDashboardWithData(data);
    });

    // Evento: Cambio en una orden
    socket.on('order_changed', function(data) {
        console.log('📝 Orden modificada:', data);
        handleOrderChange(data);
    });

    // Evento: Notificación
    socket.on('notification', function(data) {
        console.log('🔔 Notificación:', data);
        showToast('NextFlow', data.message, data.type);

        // Si estamos en la página de órdenes, recargarlas
        const currentSection = document.querySelector('.section:not([style*="display: none"])');
        if (currentSection && currentSection.id === 'orders-section') {
            loadOrders();
        }
    });

    // Evento: Error
    socket.on('error', function(data) {
        console.error('❌ Error:', data);
        showToast('Error', data.message, 'error');
    });

    // Solicitar actualización del dashboard cada 30 segundos
    setInterval(function() {
        if (socket.connected) {
            socket.emit('request_dashboard_update');
        }
    }, 30000);
}

function updateConnectionStatus(connected) {
    const statusBadge = document.getElementById('connection-status');
    const statusText = document.getElementById('status-text');
    const indicator = statusBadge.querySelector('.realtime-indicator');

    if (connected) {
        statusBadge.classList.remove('bg-danger');
        statusBadge.classList.add('bg-success');
        statusText.textContent = 'En Vivo';
        indicator.style.backgroundColor = '#10b981';
    } else {
        statusBadge.classList.remove('bg-success');
        statusBadge.classList.add('bg-danger');
        statusText.textContent = 'Desconectado';
        indicator.style.backgroundColor = '#ef4444';
    }
}

function showToast(title, message, type = 'info') {
    const toastTitle = document.getElementById('toast-title');
    const toastMessage = document.getElementById('toast-message');
    const toastIcon = document.getElementById('toast-icon');
    const toastElement = document.getElementById('liveToast');

    // Limpiar clases anteriores
    toastElement.classList.remove('toast-success', 'toast-error', 'toast-warning', 'toast-info');

    // Agregar clase según el tipo
    toastElement.classList.add(`toast-${type}`);

    // Actualizar contenido
    toastTitle.textContent = title;
    toastMessage.textContent = message;

    // Actualizar icono según el tipo
    const icons = {
        'success': 'fa-check-circle',
        'error': 'fa-exclamation-circle',
        'warning': 'fa-exclamation-triangle',
        'info': 'fa-info-circle'
    };

    toastIcon.className = `fas ${icons[type] || icons.info} me-2`;

    // Mostrar toast
    const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 4000 });
    toast.show();
}

function handleOrderChange(data) {
    const { order_id, action } = data;

    // Actualizar la lista de órdenes si estamos en esa sección
    const ordersSection = document.getElementById('orders-section');
    if (ordersSection && ordersSection.style.display !== 'none') {
        loadOrders();
    }

    // Actualizar el dashboard
    loadDashboardData();
}

function updateDashboardWithData(data) {
    // Actualizar estadísticas
    if (data.total_orders !== undefined) {
        document.getElementById('total-orders').textContent = data.total_orders.toLocaleString();
    }

    if (data.status_distribution && data.status_distribution['Order Finished']) {
        document.getElementById('completed-orders').textContent = data.status_distribution['Order Finished'];
    }

    if (data.category_distribution) {
        document.getElementById('categories').textContent = Object.keys(data.category_distribution).length;
    }
}

// Navegación
function showSection(sectionName) {
    // Ocultar todas las secciones
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });
    
    // Remover clase active de todos los nav-links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Mostrar sección seleccionada
    document.getElementById(sectionName + '-section').style.display = 'block';
    
    // Agregar clase active al nav-link correspondiente
    event.target.classList.add('active');
    
    // Actualizar título
    const titles = {
        'dashboard': 'Dashboard',
        'data-quality': 'Calidad de Datos',
        'data-cleaning': 'Limpieza de Datos',
        'orders': 'Gestión de Órdenes',
        'order-management': 'Gestión de Órdenes',
        'powerbi': 'Power BI',
        'export': 'Exportar Datos'
    };
    document.getElementById('page-title').textContent = titles[sectionName];
    
    // Cargar datos específicos de la sección
    if (sectionName === 'data-quality') {
        loadDataQualityReport();
    } else if (sectionName === 'order-management') {
        setupOrderManagement();
    }
}

// Dashboard
async function loadDashboardData() {
    try {
        const response = await fetch('/api/dashboard/stats');
        const data = await response.json();
        
        // Actualizar estadísticas
        document.getElementById('total-orders').textContent = data.total_orders.toLocaleString();
        document.getElementById('completed-orders').textContent = data.status_distribution['Order Finished'] || 0;
        document.getElementById('duplicates').textContent = '2'; // Se actualizará con la verificación
        document.getElementById('categories').textContent = Object.keys(data.category_distribution).length;
        
        // Crear gráficos
        createStatusChart(data.status_distribution);
        createCategoryChart(data.category_revenue);
        createYearlyChart(data.yearly_stats);
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showAlert('Error al cargar datos del dashboard', 'danger');
    }
}

function createStatusChart(statusData) {
    const ctx = document.getElementById('statusChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(statusData),
            datasets: [{
                data: Object.values(statusData),
                backgroundColor: [
                    '#a78bfa', // Lavanda claro
                    '#8b5cf6', // Violeta medio
                    '#6366f1'  // Indigo azulado
                ],
                borderColor: '#010001',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#fbfbfb',
                        font: {
                            family: 'Inter',
                            size: 13,
                            weight: '500'
                        },
                        padding: 15,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: '#1a1a1a',
                    titleColor: '#fbfbfb',
                    bodyColor: '#fbfbfb',
                    borderColor: '#5638c3',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    boxPadding: 6
                }
            }
        }
    });
}

function createCategoryChart(categoryData) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(categoryData),
            datasets: [{
                label: 'Ingresos ($)',
                data: Object.values(categoryData),
                backgroundColor: [
                    '#c084fc', // Rosa lavanda
                    '#7c3aed', // Violeta intenso
                    '#818cf8'  // Azul lavanda
                ],
                borderColor: [
                    '#a855f7',
                    '#6d28d9',
                    '#6366f1'
                ],
                borderWidth: 2,
                borderRadius: 8,
                barThickness: 50
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#fbfbfb',
                        font: {
                            family: 'Inter',
                            size: 13,
                            weight: '500'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: '#1a1a1a',
                    titleColor: '#fbfbfb',
                    bodyColor: '#fbfbfb',
                    borderColor: '#5638c3',
                    borderWidth: 1,
                    padding: 12
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(251, 251, 251, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#fbfbfb',
                        font: {
                            family: 'Inter',
                            size: 12
                        },
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#fbfbfb',
                        font: {
                            family: 'Inter',
                            size: 12,
                            weight: '500'
                        }
                    }
                }
            }
        }
    });
}

function createYearlyChart(yearlyData) {
    const ctx = document.getElementById('yearlyChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: yearlyData.map(item => item.year),
            datasets: [{
                label: 'Órdenes',
                data: yearlyData.map(item => item.orders),
                borderColor: '#a78bfa',
                backgroundColor: 'rgba(167, 139, 250, 0.15)',
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#a78bfa',
                pointBorderColor: '#fbfbfb',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7
            }, {
                label: 'Ingresos ($)',
                data: yearlyData.map(item => item.revenue),
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.15)',
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                yAxisID: 'y1',
                pointBackgroundColor: '#6366f1',
                pointBorderColor: '#fbfbfb',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#fbfbfb',
                        font: {
                            family: 'Inter',
                            size: 13,
                            weight: '500'
                        },
                        usePointStyle: true,
                        pointStyle: 'circle',
                        padding: 15
                    }
                },
                tooltip: {
                    backgroundColor: '#1a1a1a',
                    titleColor: '#fbfbfb',
                    bodyColor: '#fbfbfb',
                    borderColor: '#5638c3',
                    borderWidth: 1,
                    padding: 12
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    grid: {
                        color: 'rgba(251, 251, 251, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#fbfbfb',
                        font: {
                            family: 'Inter',
                            size: 12
                        }
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: {
                        drawOnChartArea: false,
                    },
                    ticks: {
                        color: '#fbfbfb',
                        font: {
                            family: 'Inter',
                            size: 12
                        },
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(251, 251, 251, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#fbfbfb',
                        font: {
                            family: 'Inter',
                            size: 12,
                            weight: '500'
                        }
                    }
                }
            }
        }
    });
}

// Calidad de Datos
async function loadDataQualityReport() {
    const loading = document.querySelector('#data-quality-section .loading');
    const report = document.getElementById('quality-report');
    
    loading.style.display = 'block';
    report.innerHTML = '';
    
    try {
        const response = await fetch('/api/data-quality/report');
        const data = await response.json();
        
        loading.style.display = 'none';
        
        const html = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Estadísticas Generales</h6>
                    <ul class="list-group">
                        <li class="list-group-item d-flex justify-content-between">
                            <span>Total de Registros:</span>
                            <span class="badge bg-primary">${data.total_records.toLocaleString()}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between">
                            <span>Total de Columnas:</span>
                            <span class="badge bg-primary">${data.total_columns}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between">
                            <span>Registros Duplicados:</span>
                            <span class="badge bg-warning">${data.duplicate_records}</span>
                        </li>
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6>Completitud de Datos</h6>
                    <ul class="list-group">
                        ${Object.entries(data.data_completeness).map(([column, percentage]) => `
                            <li class="list-group-item d-flex justify-content-between">
                                <span>${column}:</span>
                                <span class="badge ${percentage === 100 ? 'bg-success' : 'bg-warning'}">${percentage}%</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        `;
        
        report.innerHTML = html;
        
    } catch (error) {
        loading.style.display = 'none';
        report.innerHTML = '<div class="alert alert-danger">Error al cargar el reporte de calidad</div>';
        console.error('Error loading data quality report:', error);
    }
}

// Limpieza de Datos
async function checkDuplicates() {
    showLoading('cleaning-results');
    
    try {
        const response = await fetch('/api/data-cleaning/duplicates');
        const data = await response.json();
        
        const html = `
            <div class="card mt-3">
                <div class="card-header">
                    <h6><i class="fas fa-copy me-2"></i>Resultados de Verificación de Duplicados</h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="text-center">
                                <h4 class="text-warning">${data.duplicates_found}</h4>
                                <p class="mb-0">Duplicados Encontrados</p>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="text-center">
                                <h4 class="text-info">${data.total_records}</h4>
                                <p class="mb-0">Total Registros</p>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="text-center">
                                <h4 class="text-warning">${data.warnings}</h4>
                                <p class="mb-0">Warnings</p>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="text-center">
                                <h4 class="text-success">${data.total_records - data.duplicates_found}</h4>
                                <p class="mb-0">Registros Únicos</p>
                            </div>
                        </div>
                    </div>
                    ${data.duplicates_found > 0 ? `
                        <div class="mt-3">
                            <h6>Ejemplos de Duplicados:</h6>
                            <div class="table-responsive">
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>ID</th>
                                            <th>Cliente</th>
                                            <th>Fecha</th>
                                            <th>Categoría</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${data.summary.duplicate_examples ? data.summary.duplicate_examples.map(dup => `
                                            <tr>
                                                <td>${dup.order_id}</td>
                                                <td>${dup.customer_name}</td>
                                                <td>${dup.order_date}</td>
                                                <td>${dup.category}</td>
                                            </tr>
                                        `).join('') : '<tr><td colspan="4">No hay ejemplos disponibles</td></tr>'}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    ` : '<div class="alert alert-success mt-3">¡No se encontraron duplicados!</div>'}
                </div>
            </div>
        `;
        
        document.getElementById('cleaning-results').innerHTML = html;
        
    } catch (error) {
        document.getElementById('cleaning-results').innerHTML = '<div class="alert alert-danger">Error al verificar duplicados</div>';
        console.error('Error checking duplicates:', error);
    }
}

async function checkIncomplete() {
    showLoading('cleaning-results');
    
    try {
        const response = await fetch('/api/data-cleaning/incomplete');
        const data = await response.json();
        
        const html = `
            <div class="card mt-3">
                <div class="card-header">
                    <h6><i class="fas fa-exclamation-circle me-2"></i>Resultados de Verificación de Registros Incompletos</h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="text-center">
                                <h4 class="text-danger">${data.incomplete_records}</h4>
                                <p class="mb-0">Registros Problemáticos</p>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="text-center">
                                <h4 class="text-danger">${data.errors}</h4>
                                <p class="mb-0">Errores</p>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="text-center">
                                <h4 class="text-warning">${data.warnings}</h4>
                                <p class="mb-0">Warnings</p>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="text-center">
                                <h4 class="text-success">${data.total_records - data.incomplete_records}</h4>
                                <p class="mb-0">Registros Válidos</p>
                            </div>
                        </div>
                    </div>
                    ${data.incomplete_records > 0 ? `
                        <div class="mt-3">
                            <h6>Problemas Encontrados:</h6>
                            <div class="alert alert-warning">
                                <strong>IDs de registros problemáticos:</strong> 
                                ${data.summary.problematic_order_ids ? data.summary.problematic_order_ids.join(', ') : 'No disponibles'}
                            </div>
                        </div>
                    ` : '<div class="alert alert-success mt-3">¡No se encontraron registros incompletos!</div>'}
                </div>
            </div>
        `;
        
        document.getElementById('cleaning-results').innerHTML = html;
        
    } catch (error) {
        document.getElementById('cleaning-results').innerHTML = '<div class="alert alert-danger">Error al verificar registros incompletos</div>';
        console.error('Error checking incomplete records:', error);
    }
}

async function validateData() {
    showLoading('cleaning-results');
    
    try {
        const response = await fetch('/api/data-cleaning/validate');
        const data = await response.json();
        
        const html = `
            <div class="card mt-3">
                <div class="card-header">
                    <h6><i class="fas fa-check-circle me-2"></i>Resultados de Validación de Tipos de Datos</h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4">
                            <div class="text-center">
                                <h4 class="text-danger">${data.errors}</h4>
                                <p class="mb-0">Errores</p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="text-center">
                                <h4 class="text-warning">${data.warnings}</h4>
                                <p class="mb-0">Warnings</p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="text-center">
                                <h4 class="text-success">${data.total_records - data.warnings - data.errors}</h4>
                                <p class="mb-0">Registros Válidos</p>
                            </div>
                        </div>
                    </div>
                    ${data.warnings > 0 ? `
                        <div class="mt-3">
                            <h6>Problemas de Validación:</h6>
                            <ul class="list-group">
                                ${data.summary.validation_issues ? data.summary.validation_issues.map(issue => `
                                    <li class="list-group-item">${issue}</li>
                                `).join('') : '<li class="list-group-item">No hay detalles disponibles</li>'}
                            </ul>
                        </div>
                    ` : '<div class="alert alert-success mt-3">¡Todos los datos pasaron la validación!</div>'}
                </div>
            </div>
        `;
        
        document.getElementById('cleaning-results').innerHTML = html;
        
    } catch (error) {
        document.getElementById('cleaning-results').innerHTML = '<div class="alert alert-danger">Error al validar datos</div>';
        console.error('Error validating data:', error);
    }
}

// Gestión de Órdenes
async function loadOrders(page = 1) {
    const status = document.getElementById('status-filter').value;
    const category = document.getElementById('category-filter').value;
    
    currentFilters = { status, category };
    currentPage = page;
    
    const params = new URLSearchParams({
        page: page,
        per_page: 50,
        ...(status && { status }),
        ...(category && { category })
    });
    
    try {
        const response = await fetch(`/api/orders?${params}`);
        const data = await response.json();
        
        // Actualizar tabla
        const tbody = document.getElementById('orders-table');
        if (data.orders.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">No se encontraron órdenes</td></tr>';
        } else {
            tbody.innerHTML = data.orders.map(order => `
                <tr>
                    <td>${order.order_id}</td>
                    <td>${order.customer_name}</td>
                    <td>${new Date(order.order_date).toLocaleDateString()}</td>
                    <td><span class="badge bg-${getStatusColor(order.status)}">${order.status}</span></td>
                    <td>${order.category}</td>
                    <td>$${parseFloat(order.subtotal_amount).toLocaleString()}</td>
                    <td>${order.quantity}</td>
                </tr>
            `).join('');
        }
        
        // Actualizar paginación
        updatePagination(data.total_pages, page);
        
    } catch (error) {
        console.error('Error loading orders:', error);
        document.getElementById('orders-table').innerHTML = '<tr><td colspan="7" class="text-center text-danger">Error al cargar órdenes</td></tr>';
    }
}

function filterOrders() {
    loadOrders(1);
}

function updatePagination(totalPages, currentPage) {
    const pagination = document.getElementById('pagination');
    let html = '';
    
    // Botón anterior
    html += `<li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
        <a class="page-link" href="#" onclick="loadOrders(${currentPage - 1})">Anterior</a>
    </li>`;
    
    // Páginas
    for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {
        html += `<li class="page-item ${i === currentPage ? 'active' : ''}">
            <a class="page-link" href="#" onclick="loadOrders(${i})">${i}</a>
        </li>`;
    }
    
    // Botón siguiente
    html += `<li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
        <a class="page-link" href="#" onclick="loadOrders(${currentPage + 1})">Siguiente</a>
    </li>`;
    
    pagination.innerHTML = html;
}

function getStatusColor(status) {
    const colors = {
        'Order Finished': 'success',
        'Order Returned': 'warning',
        'Order Cancelled': 'danger',
        'pending': 'info'
    };
    return colors[status] || 'secondary';
}

// Power BI
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    element.select();
    element.setSelectionRange(0, 99999);
    document.execCommand('copy');
    
    showAlert('URL copiada al portapapeles', 'success');
}

// Exportar
async function exportCSV() {
    try {
        const response = await fetch('/api/export/csv');
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `orders_export_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showAlert('Archivo CSV descargado exitosamente', 'success');
        } else {
            throw new Error('Error al exportar CSV');
        }
    } catch (error) {
        console.error('Error exporting CSV:', error);
        showAlert('Error al exportar CSV', 'danger');
    }
}

// Utilidades
function refreshData() {
    const currentSection = document.querySelector('.section[style*="block"]');
    if (currentSection) {
        const sectionId = currentSection.id;
        if (sectionId === 'dashboard-section') {
            loadDashboardData();
        } else if (sectionId === 'data-quality-section') {
            loadDataQualityReport();
        } else if (sectionId === 'orders-section') {
            loadOrders(currentPage);
        }
    }
    showAlert('Datos actualizados', 'success');
}

function showLoading(containerId) {
    document.getElementById(containerId).innerHTML = `
        <div class="text-center">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="mt-2">Procesando...</p>
        </div>
    `;
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// ===== GESTIÓN DE ÓRDENES =====

function setupOrderManagement() {
    // Configurar formulario de creación
    document.getElementById('create-order-form').addEventListener('submit', createOrder);
    
    // Configurar formulario de edición
    document.getElementById('edit-order-form').addEventListener('submit', updateOrder);
    
    // Establecer fecha actual por defecto
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('create-order-date').value = today;
}

async function createOrder(event) {
    event.preventDefault();
    
    const formData = {
        customer_name: document.getElementById('create-customer-name').value,
        order_date: document.getElementById('create-order-date').value,
        status: document.getElementById('create-status').value,
        quantity: parseInt(document.getElementById('create-quantity').value),
        subtotal_amount: parseFloat(document.getElementById('create-subtotal').value),
        tax_rate: parseFloat(document.getElementById('create-tax-rate').value),
        shipping_cost: parseFloat(document.getElementById('create-shipping').value),
        category: document.getElementById('create-category').value,
        subcategory: document.getElementById('create-subcategory').value
    };
    
    try {
        const response = await fetch('/api/orders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert(`Orden creada exitosamente con ID: ${result.order_id}`, 'success');
            document.getElementById('create-order-form').reset();
            // Actualizar dashboard si está visible
            if (document.getElementById('dashboard-section').style.display !== 'none') {
                loadDashboardData();
            }
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        console.error('Error creating order:', error);
        showAlert('Error al crear la orden', 'danger');
    }
}

async function searchOrder() {
    const orderId = document.getElementById('search-order-id').value;
    
    if (!orderId) {
        showAlert('Por favor ingresa un ID de orden', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`/api/orders/${orderId}`);
        const result = await response.json();
        
        if (response.ok) {
            // Llenar formulario de edición
            document.getElementById('edit-customer-name').value = result.customer_name;
            document.getElementById('edit-order-date').value = result.order_date;
            document.getElementById('edit-status').value = result.status;
            document.getElementById('edit-quantity').value = result.quantity;
            document.getElementById('edit-subtotal').value = result.subtotal_amount;
            document.getElementById('edit-tax-rate').value = result.tax_rate;
            document.getElementById('edit-shipping').value = result.shipping_cost;
            document.getElementById('edit-category').value = result.category;
            document.getElementById('edit-subcategory').value = result.subcategory;
            
            // Mostrar formulario de edición
            document.getElementById('order-edit-form').style.display = 'block';
            currentEditingOrderId = orderId;
            
            showAlert('Orden encontrada', 'success');
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
            document.getElementById('order-edit-form').style.display = 'none';
            currentEditingOrderId = null;
        }
    } catch (error) {
        console.error('Error searching order:', error);
        showAlert('Error al buscar la orden', 'danger');
    }
}

async function updateOrder(event) {
    event.preventDefault();
    
    if (!currentEditingOrderId) {
        showAlert('No hay orden seleccionada para editar', 'warning');
        return;
    }
    
    const formData = {
        customer_name: document.getElementById('edit-customer-name').value,
        order_date: document.getElementById('edit-order-date').value,
        status: document.getElementById('edit-status').value,
        quantity: parseInt(document.getElementById('edit-quantity').value),
        subtotal_amount: parseFloat(document.getElementById('edit-subtotal').value),
        tax_rate: parseFloat(document.getElementById('edit-tax-rate').value),
        shipping_cost: parseFloat(document.getElementById('edit-shipping').value),
        category: document.getElementById('edit-category').value,
        subcategory: document.getElementById('edit-subcategory').value
    };
    
    try {
        const response = await fetch(`/api/orders/${currentEditingOrderId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert('Orden actualizada exitosamente', 'success');
            // Actualizar dashboard si está visible
            if (document.getElementById('dashboard-section').style.display !== 'none') {
                loadDashboardData();
            }
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        console.error('Error updating order:', error);
        showAlert('Error al actualizar la orden', 'danger');
    }
}

async function deleteOrder() {
    if (!currentEditingOrderId) {
        showAlert('No hay orden seleccionada para eliminar', 'warning');
        return;
    }
    
    if (!confirm(`¿Estás seguro de que quieres eliminar la orden ${currentEditingOrderId}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/orders/${currentEditingOrderId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert('Orden eliminada exitosamente', 'success');
            document.getElementById('order-edit-form').style.display = 'none';
            document.getElementById('search-order-id').value = '';
            currentEditingOrderId = null;
            // Actualizar dashboard si está visible
            if (document.getElementById('dashboard-section').style.display !== 'none') {
                loadDashboardData();
            }
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        console.error('Error deleting order:', error);
        showAlert('Error al eliminar la orden', 'danger');
    }
}

async function bulkUpdateStatus() {
    const orderIdsText = document.getElementById('bulk-order-ids').value;
    const newStatus = document.getElementById('bulk-new-status').value;
    
    if (!orderIdsText.trim()) {
        showAlert('Por favor ingresa los IDs de las órdenes', 'warning');
        return;
    }
    
    // Parsear IDs
    const orderIds = orderIdsText.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id));
    
    if (orderIds.length === 0) {
        showAlert('No se encontraron IDs válidos', 'warning');
        return;
    }
    
    if (!confirm(`¿Estás seguro de que quieres actualizar ${orderIds.length} órdenes al estado "${newStatus}"?`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/orders/bulk-status', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                order_ids: orderIds,
                status: newStatus
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert(`${result.updated_count} órdenes actualizadas exitosamente`, 'success');
            document.getElementById('bulk-order-ids').value = '';
            // Actualizar dashboard si está visible
            if (document.getElementById('dashboard-section').style.display !== 'none') {
                loadDashboardData();
            }
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        console.error('Error in bulk update:', error);
        showAlert('Error al actualizar las órdenes', 'danger');
    }
}

// ============================================================================
// CHATBOT FUNCTIONALITY
// ============================================================================

function toggleChatbot() {
    const chatbot = document.getElementById('chatbotContainer');
    chatbot.classList.toggle('open');

    // Focus input when opening
    if (chatbot.classList.contains('open')) {
        document.getElementById('chatbotInput').focus();
    }
}

function addChatbotMessage(message, isUser = false) {
    const messagesContainer = document.getElementById('chatbotMessages');

    const messageDiv = document.createElement('div');
    messageDiv.className = `chatbot-message ${isUser ? 'user' : 'bot'}`;

    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'chatbot-avatar';
    avatarDiv.innerHTML = isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'chatbot-bubble';
    bubbleDiv.textContent = message;

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(bubbleDiv);
    messagesContainer.appendChild(messageDiv);

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function sendChatbotMessage() {
    const input = document.getElementById('chatbotInput');
    const message = input.value.trim();

    if (!message) return;

    // Add user message to chat
    addChatbotMessage(message, true);

    // Clear input
    input.value = '';

    // Disable send button
    const sendBtn = document.getElementById('chatbotSendBtn');
    sendBtn.disabled = true;

    // Show "typing" indicator
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chatbot-message bot';
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = `
        <div class="chatbot-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="chatbot-bubble">
            <i class="fas fa-circle-notch fa-spin"></i> Escribiendo...
        </div>
    `;
    document.getElementById('chatbotMessages').appendChild(typingDiv);

    try {
        // Send message via HTTP POST
        const response = await fetch('/api/chatbot/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        // Remove typing indicator
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }

        // Add bot response
        if (data.success && data.message) {
            addChatbotMessage(data.message, false);
        } else if (data.message) {
            addChatbotMessage(data.message, false);
        } else {
            addChatbotMessage('No pude obtener una respuesta. Verifica que tu workflow de n8n esté activo.', false);
        }

    } catch (error) {
        console.error('Error sending chatbot message:', error);

        // Remove typing indicator
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }

        addChatbotMessage('Error al conectar con el bot. Por favor intenta de nuevo.', false);
    } finally {
        // Re-enable send button
        sendBtn.disabled = false;
    }
}

function handleChatbotKeyPress(event) {
    if (event.key === 'Enter') {
        sendChatbotMessage();
    }
}

// Listen for chatbot responses via WebSocket
if (socket) {
    socket.on('chatbot_response', function(data) {
        console.log('Chatbot response received:', data);
        addChatbotMessage(data.message, false);

        // Re-enable send button
        document.getElementById('chatbotSendBtn').disabled = false;
    });
}
