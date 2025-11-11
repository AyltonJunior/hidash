/**
 * Função para adicionar filtros em tabelas de dados
 * Permite filtrar rapidamente por conteúdos de cada coluna
 */
function setupTableFilters() {
    const tables = document.querySelectorAll('table.filterable');
    
    tables.forEach(table => {
        const thead = table.querySelector('thead');
        const tbody = table.querySelector('tbody');
        const headers = Array.from(thead.querySelectorAll('th'));
        
        // Criar a linha de filtros
        const filterRow = document.createElement('tr');
        filterRow.className = 'filter-row';
        
        // Adicionar um campo de input para cada coluna
        headers.forEach((header, index) => {
            const cell = document.createElement('td');
            
            // Se for a última coluna (ações), não adicionar filtro
            if (header.textContent.trim().toLowerCase() === 'actions' || 
                header.textContent.trim().toLowerCase() === 'ações') {
                filterRow.appendChild(cell);
                return;
            }
            
            // Criar campo de filtro
            const input = document.createElement('input');
            input.type = 'text';
            input.className = 'form-control form-control-sm filter-input';
            input.placeholder = `Filtrar ${header.textContent}`;
            input.dataset.index = index;
            
            // Adicionar evento de filtro
            input.addEventListener('input', () => filterTable(table));
            
            cell.appendChild(input);
            filterRow.appendChild(cell);
        });
        
        // Inserir a linha de filtros após o cabeçalho
        thead.appendChild(filterRow);
        
        // Adicionar botão para limpar filtros
        const clearFilters = document.createElement('button');
        clearFilters.className = 'btn btn-sm btn-secondary mt-2 mb-3';
        clearFilters.textContent = 'Limpar Filtros';
        clearFilters.addEventListener('click', () => {
            table.querySelectorAll('.filter-input').forEach(input => {
                input.value = '';
            });
            filterTable(table);
        });
        
        // Inserir o botão antes da tabela
        table.parentNode.insertBefore(clearFilters, table);
    });
}

/**
 * Filtra os dados da tabela baseado nos valores dos inputs
 */
function filterTable(table) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const filters = Array.from(table.querySelectorAll('.filter-input'))
        .filter(input => input.value.trim() !== '')
        .map(input => ({
            index: parseInt(input.dataset.index),
            value: input.value.toLowerCase()
        }));
    
    // Se não há filtros, mostrar todas as linhas
    if (filters.length === 0) {
        rows.forEach(row => row.style.display = '');
        return;
    }
    
    // Aplicar filtros
    rows.forEach(row => {
        const cells = Array.from(row.querySelectorAll('td'));
        const visible = filters.every(filter => {
            const cellText = cells[filter.index].textContent.toLowerCase();
            return cellText.includes(filter.value);
        });
        
        row.style.display = visible ? '' : 'none';
    });
}

// Executar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', setupTableFilters);