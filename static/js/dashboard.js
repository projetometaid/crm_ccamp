// Dashboard JavaScript para análise de atualizações CRM CCAMP

let uploadedFiles = {
    'emissao': null,
    'renovacao-geral': null,
    'renovacao-safeid': null
};

let fileData = {
    'emissao': null,
    'renovacao-geral': null,
    'renovacao-safeid': null
};

// Inicializar eventos quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    initializeUploadAreas();
});

function initializeUploadAreas() {
    const uploadAreas = ['emissao', 'renovacao-geral', 'renovacao-safeid'];
    
    uploadAreas.forEach(area => {
        const uploadDiv = document.getElementById(`upload-${area}`);
        const fileInput = document.getElementById(`file-${area}`);
        
        // Click para abrir seletor de arquivo
        uploadDiv.addEventListener('click', () => fileInput.click());
        
        // Drag and drop
        uploadDiv.addEventListener('dragover', handleDragOver);
        uploadDiv.addEventListener('dragleave', handleDragLeave);
        uploadDiv.addEventListener('drop', (e) => handleDrop(e, area));
        
        // Mudança de arquivo
        fileInput.addEventListener('change', (e) => handleFileSelect(e, area));
    });
}

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e, area) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        processFile(files[0], area);
    }
}

function handleFileSelect(e, area) {
    const files = e.target.files;
    if (files.length > 0) {
        processFile(files[0], area);
    }
}

function processFile(file, area) {
    // Validar tipo de arquivo
    if (!file.name.match(/\.(xlsx|xls)$/i)) {
        alert('Por favor, selecione apenas arquivos Excel (.xlsx ou .xls)');
        return;
    }
    
    // Armazenar arquivo
    uploadedFiles[area] = file;
    
    // Mostrar informações do arquivo
    showFileInfo(file, area);
    
    // Ler dados do arquivo
    readExcelFile(file, area);
    
    // Verificar se pode habilitar botões
    checkEnableButtons();
}

function showFileInfo(file, area) {
    const uploadDiv = document.getElementById(`upload-${area}`);
    const infoDiv = document.getElementById(`info-${area}`);
    const nameSpan = document.getElementById(`name-${area}`);
    const sizeSpan = document.getElementById(`size-${area}`);
    
    uploadDiv.style.display = 'none';
    infoDiv.style.display = 'block';
    
    nameSpan.textContent = file.name;
    sizeSpan.textContent = `${(file.size / 1024 / 1024).toFixed(2)} MB`;
}

function removeFile(area) {
    uploadedFiles[area] = null;
    fileData[area] = null;
    
    const uploadDiv = document.getElementById(`upload-${area}`);
    const infoDiv = document.getElementById(`info-${area}`);
    const fileInput = document.getElementById(`file-${area}`);
    
    uploadDiv.style.display = 'block';
    infoDiv.style.display = 'none';
    fileInput.value = '';
    
    checkEnableButtons();
}

function readExcelFile(file, area) {
    const reader = new FileReader();
    
    reader.onload = function(e) {
        try {
            const data = new Uint8Array(e.target.result);
            const workbook = XLSX.read(data, { type: 'array' });
            
            // Assumir que os dados estão na primeira planilha
            const firstSheetName = workbook.SheetNames[0];
            const worksheet = workbook.Sheets[firstSheetName];
            
            // Converter para JSON
            const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
            
            // Processar dados
            fileData[area] = processExcelData(jsonData);
            
            console.log(`Dados carregados para ${area}:`, fileData[area]);
            
        } catch (error) {
            console.error(`Erro ao ler arquivo ${area}:`, error);
            alert(`Erro ao processar arquivo ${area}. Verifique se é um arquivo Excel válido.`);
        }
    };
    
    reader.readAsArrayBuffer(file);
}

function processExcelData(rawData) {
    if (rawData.length < 2) return [];
    
    const headers = rawData[0];
    const rows = rawData.slice(1);
    
    return rows.map(row => {
        const obj = {};
        headers.forEach((header, index) => {
            obj[header] = row[index] || null;
        });
        return obj;
    }).filter(row => row.protocolo); // Filtrar apenas linhas com protocolo
}

function checkEnableButtons() {
    const hasAnyFile = Object.values(uploadedFiles).some(file => file !== null);
    const hasAllFiles = Object.values(uploadedFiles).every(file => file !== null);
    
    document.getElementById('btn-analyze').disabled = !hasAnyFile;
    document.getElementById('btn-process').disabled = !hasAllFiles;
}

async function analyzeFiles() {
    showLoading(true);
    
    try {
        // Simular análise (aqui você faria a chamada para o backend)
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const analysis = performAnalysis();
        displayAnalysisResults(analysis);
        
        showResults(true);
        
    } catch (error) {
        console.error('Erro na análise:', error);
        alert('Erro ao analisar arquivos. Tente novamente.');
    } finally {
        showLoading(false);
    }
}

async function performAnalysis() {
    try {
        // Preparar FormData com os arquivos
        const formData = new FormData();

        Object.keys(uploadedFiles).forEach(area => {
            if (uploadedFiles[area]) {
                formData.append(`file-${area}`, uploadedFiles[area]);
            }
        });

        // Fazer chamada para análise detalhada
        const response = await fetch('/api/detailed-analysis', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.status === 'success') {
            return processDetailedAnalysis(result.detailed_analysis);
        } else {
            throw new Error(result.message);
        }

    } catch (error) {
        console.error('Erro na análise:', error);
        throw error;
    }
}

function processDetailedAnalysis(detailedAnalysis) {
    let totalProtocols = 0;
    let newProtocols = 0;
    let updatedProtocols = 0;
    let updatedFields = 0;
    let comparisons = [];
    let fieldStatistics = {};

    // Processar análise de cada tabela
    Object.keys(detailedAnalysis).forEach(table => {
        const analysis = detailedAnalysis[table];

        if (analysis.error) {
            console.error(`Erro na análise da tabela ${table}:`, analysis.error);
            return;
        }

        // Somar estatísticas gerais
        totalProtocols += analysis.summary.total_protocols_analyzed;
        newProtocols += analysis.new_protocols.length;
        updatedProtocols += analysis.summary.protocols_with_changes;
        updatedFields += analysis.summary.total_field_changes;

        // Processar protocolos novos
        analysis.new_protocols.forEach(newProtocol => {
            comparisons.push({
                protocol: newProtocol.protocol,
                table: table,
                field: 'NOVO REGISTRO',
                currentValue: '',
                newValue: 'Registro completo',
                status: 'new',
                changeType: 'NEW'
            });
        });

        // Processar mudanças de campo
        analysis.field_changes.forEach(change => {
            comparisons.push({
                protocol: change.protocol,
                table: table,
                field: change.field,
                currentValue: change.current_value,
                newValue: change.new_value,
                status: 'updated',
                changeType: change.change_type
            });
        });

        // Consolidar estatísticas por campo
        Object.keys(analysis.field_statistics).forEach(fieldName => {
            const fieldKey = `${table}.${fieldName}`;
            fieldStatistics[fieldKey] = analysis.field_statistics[fieldName];
        });
    });

    return {
        totalProtocols,
        newProtocols,
        updatedProtocols,
        updatedFields,
        comparisons,
        fieldStatistics,
        detailedAnalysis
    };
}

function displayAnalysisResults(analysis) {
    // Atualizar estatísticas principais
    document.getElementById('stat-total-protocols').textContent = analysis.totalProtocols;
    document.getElementById('stat-new-protocols').textContent = analysis.newProtocols;
    document.getElementById('stat-updated-protocols').textContent = analysis.updatedProtocols;
    document.getElementById('stat-updated-fields').textContent = analysis.updatedFields;

    // Criar seção de estatísticas por campo
    displayFieldStatistics(analysis.fieldStatistics);

    // Atualizar tabela de comparação detalhada
    const tbody = document.getElementById('comparison-tbody');
    tbody.innerHTML = '';

    // Agrupar por protocolo para melhor visualização
    const protocolGroups = {};
    analysis.comparisons.forEach(comp => {
        if (!protocolGroups[comp.protocol]) {
            protocolGroups[comp.protocol] = [];
        }
        protocolGroups[comp.protocol].push(comp);
    });

    // Exibir agrupado por protocolo
    Object.keys(protocolGroups).forEach(protocol => {
        const changes = protocolGroups[protocol];

        // Cabeçalho do protocolo
        const headerRow = document.createElement('tr');
        headerRow.className = 'protocol-header';
        headerRow.innerHTML = `
            <td colspan="6">
                <strong>📋 Protocolo: ${protocol}</strong>
                <span class="badge bg-info ms-2">${changes.length} mudança(s)</span>
                <span class="badge bg-secondary ms-1">${changes[0].table}</span>
            </td>
        `;
        tbody.appendChild(headerRow);

        // Mudanças do protocolo
        changes.forEach(comp => {
            const row = document.createElement('tr');
            row.className = comp.status === 'new' ? 'field-new' : 'field-updated';

            const changeTypeIcon = comp.changeType === 'FILL_EMPTY' ? '📝' : '🔄';
            const changeTypeBadge = comp.changeType === 'FILL_EMPTY' ?
                '<span class="badge bg-info">Preenchimento</span>' :
                '<span class="badge bg-warning">Atualização</span>';

            row.innerHTML = `
                <td style="padding-left: 2rem;">${changeTypeIcon} ${comp.field}</td>
                <td>${changeTypeBadge}</td>
                <td><small class="text-muted">${formatValue(comp.currentValue)}</small></td>
                <td><strong>${formatValue(comp.newValue)}</strong></td>
                <td>
                    <span class="badge ${comp.status === 'new' ? 'bg-success' : 'bg-warning'}">
                        ${comp.status === 'new' ? 'Novo' : 'Mudança'}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-info" onclick="showFieldDetails('${comp.field}', '${comp.table}')">
                        <i class="fas fa-info-circle"></i>
                    </button>
                </td>
            `;

            tbody.appendChild(row);
        });
    });
}

function displayFieldStatistics(fieldStatistics) {
    // Criar ou atualizar seção de estatísticas por campo
    let statsSection = document.getElementById('field-statistics-section');

    if (!statsSection) {
        // Criar seção se não existir
        const resultsSection = document.getElementById('results-section');
        const newSection = document.createElement('div');
        newSection.id = 'field-statistics-section';
        newSection.className = 'row mb-4';
        newSection.innerHTML = `
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="fas fa-chart-bar"></i> Estatísticas por Campo
                        </h5>
                    </div>
                    <div class="card-body" id="field-statistics-content">
                        <!-- Conteúdo será inserido aqui -->
                    </div>
                </div>
            </div>
        `;

        // Inserir antes da tabela de comparação
        const comparisonCard = resultsSection.querySelector('.card:last-child');
        resultsSection.insertBefore(newSection, comparisonCard);
        statsSection = newSection;
    }

    const content = document.getElementById('field-statistics-content');
    content.innerHTML = '';

    if (Object.keys(fieldStatistics).length === 0) {
        content.innerHTML = '<p class="text-muted">Nenhuma mudança de campo detectada.</p>';
        return;
    }

    // Criar cards para cada campo alterado
    const fieldsHtml = Object.keys(fieldStatistics).map(fieldKey => {
        const stats = fieldStatistics[fieldKey];
        const [table, field] = fieldKey.split('.');

        return `
            <div class="col-md-4 mb-3">
                <div class="card border-left-warning">
                    <div class="card-body">
                        <h6 class="card-title">
                            <span class="badge bg-secondary">${table}</span>
                            ${field}
                        </h6>
                        <p class="card-text">
                            <strong>${stats.total_changes}</strong> mudanças<br>
                            <small class="text-muted">${stats.protocols_affected.length} protocolos afetados</small>
                        </p>
                        <button class="btn btn-sm btn-outline-primary" onclick="showFieldExamples('${fieldKey}', ${JSON.stringify(stats).replace(/"/g, '&quot;')})">
                            Ver Exemplos
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    content.innerHTML = `<div class="row">${fieldsHtml}</div>`;
}

function showFieldExamples(fieldKey, stats) {
    const [table, field] = fieldKey.split('.');

    let examplesHtml = stats.change_examples.map(example => `
        <tr>
            <td><code>${example.protocol}</code></td>
            <td><span class="text-muted">${formatValue(example.from)}</span></td>
            <td><strong>${formatValue(example.to)}</strong></td>
        </tr>
    `).join('');

    const modalHtml = `
        <div class="modal fade" id="fieldExamplesModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            Exemplos de Mudanças - ${field}
                            <span class="badge bg-secondary ms-2">${table}</span>
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p><strong>Total de mudanças:</strong> ${stats.total_changes}</p>
                        <p><strong>Protocolos afetados:</strong> ${stats.protocols_affected.length}</p>

                        <h6>Exemplos de mudanças:</h6>
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Protocolo</th>
                                    <th>Valor Atual</th>
                                    <th>Novo Valor</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${examplesHtml}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remover modal anterior se existir
    const existingModal = document.getElementById('fieldExamplesModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Adicionar novo modal
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('fieldExamplesModal'));
    modal.show();
}

async function processUpdates() {
    if (!confirm('Confirma o processamento das atualizações no banco de dados?')) {
        return;
    }
    
    showLoading(true);
    
    try {
        // Aqui você faria a chamada para o backend processar as atualizações
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        alert('Atualizações processadas com sucesso!');
        
        // Limpar arquivos após processamento
        Object.keys(uploadedFiles).forEach(area => {
            removeFile(area);
        });
        
        showResults(false);
        
    } catch (error) {
        console.error('Erro no processamento:', error);
        alert('Erro ao processar atualizações. Tente novamente.');
    } finally {
        showLoading(false);
    }
}

function showLoading(show) {
    const loadingSection = document.getElementById('loading-section');
    loadingSection.style.display = show ? 'block' : 'none';
}

function showResults(show) {
    const resultsSection = document.getElementById('results-section');
    resultsSection.style.display = show ? 'block' : 'none';
}

// Função para formatar valores
function formatValue(value) {
    if (value === null || value === undefined || value === '') {
        return '<em class="text-muted">vazio</em>';
    }
    
    if (typeof value === 'string' && value.length > 50) {
        return value.substring(0, 50) + '...';
    }
    
    return value;
}
