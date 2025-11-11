// HiDash Custom JavaScript

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
  // Rotating quotes in the header
  const quotes = [
    "Sem dados confiáveis, toda estratégia é um palpite caro.",
    "Dados confiáveis são o alicerce de toda decisão inteligente.",
    "Sem dados, não há controle; sem controle, não há futuro.",
    "Gestão eficiente começa com dados reais, não com suposições.",
    "A diferença entre sucesso e prejuízo está na qualidade dos dados."
  ];
  
  function initRotatingQuotes() {
    const quoteElement = document.getElementById('rotating-quote');
    if (!quoteElement) return;
    
    console.log("Rotating quotes initialized");
    let currentQuoteIndex = 0;
    
    // Set initial opacity to ensure transitions work
    quoteElement.style.opacity = 1;
    
    // Function to change the quote with fade effect
    function changeQuote() {
      console.log("Changing quote...");
      quoteElement.style.opacity = 0;
      
      setTimeout(function() {
        currentQuoteIndex = (currentQuoteIndex + 1) % quotes.length;
        quoteElement.textContent = quotes[currentQuoteIndex];
        quoteElement.style.opacity = 1;
        console.log("New quote: " + quotes[currentQuoteIndex]);
      }, 500);
    }
    
    // Change quote every 5 seconds
    setInterval(changeQuote, 5000);
  }
  
  // Initialize rotating quotes
  initRotatingQuotes();
  
  // Password strength validator
  const passwordField = document.getElementById('password');
  if (passwordField) {
    const confirmField = document.getElementById('confirm_password');
    const lengthRule = document.getElementById('length-rule');
    const uppercaseRule = document.getElementById('uppercase-rule');
    const lowercaseRule = document.getElementById('lowercase-rule');
    const numberRule = document.getElementById('number-rule');
    const specialRule = document.getElementById('special-rule');
    
    passwordField.addEventListener('keyup', function() {
      validatePassword(this.value);
    });
    
    if (confirmField) {
      confirmField.addEventListener('keyup', function() {
        if (passwordField.value === this.value) {
          this.classList.remove('is-invalid');
          this.classList.add('is-valid');
        } else {
          this.classList.remove('is-valid');
          this.classList.add('is-invalid');
        }
      });
    }
    
    function validatePassword(password) {
      // Length rule
      if (password.length >= 8) {
        lengthRule.querySelector('i').className = 'fas fa-check-circle text-success';
      } else {
        lengthRule.querySelector('i').className = 'fas fa-times-circle text-danger';
      }
      
      // Uppercase rule
      if (/[A-Z]/.test(password)) {
        uppercaseRule.querySelector('i').className = 'fas fa-check-circle text-success';
      } else {
        uppercaseRule.querySelector('i').className = 'fas fa-times-circle text-danger';
      }
      
      // Lowercase rule
      if (/[a-z]/.test(password)) {
        lowercaseRule.querySelector('i').className = 'fas fa-check-circle text-success';
      } else {
        lowercaseRule.querySelector('i').className = 'fas fa-times-circle text-danger';
      }
      
      // Number rule
      if (/[0-9]/.test(password)) {
        numberRule.querySelector('i').className = 'fas fa-check-circle text-success';
      } else {
        numberRule.querySelector('i').className = 'fas fa-times-circle text-danger';
      }
      
      // Special character rule
      if (/[!@#$%^&*]/.test(password)) {
        specialRule.querySelector('i').className = 'fas fa-check-circle text-success';
      } else {
        specialRule.querySelector('i').className = 'fas fa-times-circle text-danger';
      }
    }
  }
  
  // Auto-dismiss alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
  alerts.forEach(function(alert) {
    setTimeout(function() {
      const alert = bootstrap.Alert.getOrCreateInstance(alert);
      alert.close();
    }, 5000);
  });
  
  // Handle company selection to update departments dropdown
  const companySelect = document.getElementById('company_id');
  const departmentSelect = document.getElementById('department_ids');
  const roleSelect = document.getElementById('role');
  
  if (companySelect && departmentSelect) {
    // Function to load departments based on company selection
    function loadDepartments(companyId) {
      if (companyId) {
        // Clear current options
        departmentSelect.innerHTML = '';
        
        // Fetch departments for selected company
        fetch(`/api/departments?company_id=${companyId}`)
          .then(response => response.json())
          .then(data => {
            if (data && data.length > 0) {
              data.forEach(dept => {
                const option = document.createElement('option');
                option.value = dept.id;
                option.textContent = dept.name;
                departmentSelect.appendChild(option);
              });
            } else {
              // Add a placeholder option if no departments are found
              const option = document.createElement('option');
              option.value = "";
              option.textContent = "No departments available";
              option.disabled = true;
              departmentSelect.appendChild(option);
            }
          })
          .catch(error => console.error('Error fetching departments:', error));
      }
    }
    
    // Function to handle role change and departments visibility
    function updateDepartmentsField() {
      if (roleSelect && roleSelect.value === 'admin') {
        departmentSelect.disabled = true;
        document.querySelector('small.form-text').innerHTML = 'Administrators have access to all departments automatically.';
      } else {
        departmentSelect.disabled = false;
        document.querySelector('small.form-text').innerHTML = 'Hold Ctrl (Windows) or Command (Mac) to select multiple departments.';
      }
      
      // Toggle password fields visibility based on role
      const passwordSections = document.querySelectorAll('.password-section');
      if (passwordSections.length > 0) {
        const selectedRole = roleSelect.value;
        const showPasswordFields = selectedRole === 'master' || selectedRole === 'admin';
        
        passwordSections.forEach(section => {
          section.style.display = showPasswordFields ? 'flex' : 'none';
        });
      }
    }
    
    // Load departments when the page loads if a company is already selected
    if (companySelect.value) {
      loadDepartments(companySelect.value);
    }
    
    // Load departments when company selection changes
    companySelect.addEventListener('change', function() {
      loadDepartments(this.value);
    });
    
    // Handle role change
    if (roleSelect) {
      updateDepartmentsField(); // Set initial state
      roleSelect.addEventListener('change', updateDepartmentsField);
    }
  }
  
  // Toggle sidebar
  const sidebarToggle = document.querySelector('#sidebarToggle');
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function(e) {
      e.preventDefault();
      document.querySelector('body').classList.toggle('sidebar-toggled');
      document.querySelector('.sidebar').classList.toggle('toggled');
      
      if (document.querySelector('.sidebar').classList.contains('toggled')) {
        document.querySelectorAll('.sidebar .collapse').forEach(collapse => {
          collapse.classList.remove('show');
        });
      }
    });
  }
  
  // Close any open menu dropdowns when window is resized below 768px
  window.addEventListener('resize', function() {
    if (window.innerWidth < 768) {
      document.querySelectorAll('.sidebar .collapse').forEach(collapse => {
        collapse.classList.remove('show');
      });
    }
    
    if (window.innerWidth < 480 && !document.querySelector('.sidebar').classList.contains('toggled')) {
      document.querySelector('body').classList.add('sidebar-toggled');
      document.querySelector('.sidebar').classList.add('toggled');
      document.querySelectorAll('.sidebar .collapse').forEach(collapse => {
        collapse.classList.remove('show');
      });
    }
  });
  
  // Prevent the content wrapper from scrolling when hovering over the sidebar menu
  document.querySelectorAll('.sidebar-menu').forEach(menu => {
    menu.addEventListener('mousewheel', function(e) {
      if (this.scrollTop === 0 && e.deltaY < 0) {
        e.preventDefault();
      } else if (this.scrollHeight === this.scrollTop + this.offsetHeight && e.deltaY > 0) {
        e.preventDefault();
      }
    });
  });
  
  // Dashboard cards click handler
  const dashboardCards = document.querySelectorAll('.card-dashboard');
  dashboardCards.forEach(card => {
    card.addEventListener('click', function() {
      const dashboardId = this.getAttribute('data-dashboard-id');
      if (dashboardId) {
        window.location.href = `/dashboard/view/${dashboardId}`;
      }
    });
  });
  
  // Confirmation dialogs for delete actions
  const deleteButtons = document.querySelectorAll('[data-confirm]');
  deleteButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      const confirmMessage = this.getAttribute('data-confirm');
      if (!confirm(confirmMessage || 'Are you sure you want to delete this item?')) {
        e.preventDefault();
      }
    });
  });
  
  // Toggle password visibility
  const togglePasswordButtons = document.querySelectorAll('.toggle-password');
  togglePasswordButtons.forEach(button => {
    button.addEventListener('click', function() {
      const input = document.querySelector(this.getAttribute('data-target'));
      if (input.type === 'password') {
        input.type = 'text';
        this.innerHTML = '<i class="fas fa-eye-slash"></i>';
      } else {
        input.type = 'password';
        this.innerHTML = '<i class="fas fa-eye"></i>';
      }
    });
  });
});

// API endpoints for AJAX
function fetchDepartments(companyId, callback) {
  fetch(`/api/departments?company_id=${companyId}`)
    .then(response => response.json())
    .then(data => callback(null, data))
    .catch(error => callback(error, null));
}

// Fullscreen dashboard back button
function goBack() {
  window.location.href = '/dashboard';
}
