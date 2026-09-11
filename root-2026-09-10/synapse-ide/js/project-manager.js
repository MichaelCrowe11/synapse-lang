/**
 * Advanced Project Management for Synapse IDE
 * Handles multi-language projects with cross-language transpilation
 */

class SynapseProjectManager {
    constructor() {
        this.currentProject = null;
        this.projects = new Map();
        this.recentProjects = [];
        this.transpiler = new CrossLanguageTranspiler();
        this.workspaceSettings = {};
        
        this.init();
    }
    
    init() {
        this.loadRecentProjects();
        this.setupProjectUI();
        console.log('Project Manager initialized');
    }
    
    loadRecentProjects() {
        const stored = localStorage.getItem('synapse-recent-projects');
        if (stored) {
            this.recentProjects = JSON.parse(stored);
        }
    }
    
    saveRecentProjects() {
        localStorage.setItem('synapse-recent-projects', JSON.stringify(this.recentProjects));
    }
    
    setupProjectUI() {
        this.updateProjectExplorer();
        this.setupProjectEvents();
    }
    
    setupProjectEvents() {
        document.addEventListener('click', (e) => {
            const action = e.target.getAttribute('data-action');
            
            switch (action) {
                case 'new-project':
                    this.showNewProjectDialog();
                    break;
                case 'open-project':
                    this.showOpenProjectDialog();
                    break;
                case 'save-project':
                    this.saveProject();
                    break;
                case 'close-project':
                    this.closeProject();
                    break;
                case 'project-settings':
                    this.showProjectSettings();
                    break;
                case 'transpile-project':
                    this.showTranspileDialog();
                    break;
            }
        });
    }
    
    async createProject(config) {
        const project = {
            id: Date.now().toString(),
            name: config.name,
            type: config.type, // 'synapse', 'multi-language', 'research'
            languages: config.languages || ['synapse'],
            created: new Date(),
            modified: new Date(),
            structure: {
                src: {},
                tests: {},
                docs: {},
                examples: {}
            },
            settings: {
                targetLanguages: config.targetLanguages || [],
                transpileOnSave: config.transpileOnSave || false,
                autoTest: config.autoTest || false,
                aiAssistance: config.aiAssistance !== false
            },
            dependencies: config.dependencies || {},
            metadata: {
                description: config.description || '',
                author: config.author || '',
                version: '1.0.0',
                tags: config.tags || []
            }
        };
        
        // Create default project structure
        await this.createProjectStructure(project);
        
        this.projects.set(project.id, project);
        this.currentProject = project;
        
        // Add to recent projects
        this.addToRecent(project);
        
        // Update UI
        this.updateProjectExplorer();
        this.updateProjectStatus();
        
        console.log(`Project created: ${project.name}`);
        return project;
    }
    
    async createProjectStructure(project) {
        const templates = {
            synapse: {
                'src/main.syn': this.getTemplate('synapse-main'),
                'tests/test_main.syn': this.getTemplate('synapse-test'),
                'examples/uncertainty_demo.syn': this.getTemplate('synapse-example'),
                'README.md': this.getTemplate('readme', project),
                'synapse.config.json': JSON.stringify({
                    name: project.name,
                    version: project.metadata.version,
                    dependencies: project.dependencies,
                    settings: project.settings
                }, null, 2)
            },
            'qubit-flow': {
                'src/quantum_circuit.qf': this.getTemplate('qubit-flow-main'),
                'tests/test_circuit.qf': this.getTemplate('qubit-flow-test'),
                'examples/bell_state.qf': this.getTemplate('qubit-flow-example')
            },
            'quantum-net': {
                'src/network.qn': this.getTemplate('quantum-net-main'),
                'tests/test_network.qn': this.getTemplate('quantum-net-test'),
                'examples/teleportation.qn': this.getTemplate('quantum-net-example')
            },
            flux: {
                'src/pipeline.flux': this.getTemplate('flux-main'),
                'tests/test_pipeline.flux': this.getTemplate('flux-test')
            },
            crowe: {
                'src/main.crowe': this.getTemplate('crowe-main'),
                'tests/test_main.crowe': this.getTemplate('crowe-test')
            }
        };
        
        // Create files for primary language
        const primaryTemplate = templates[project.languages[0]] || templates.synapse;
        Object.assign(project.structure.src, primaryTemplate);
        
        // Add cross-language files if multi-language project
        if (project.type === 'multi-language') {
            project.languages.forEach(lang => {
                if (templates[lang] && lang !== project.languages[0]) {
                    Object.assign(project.structure.src, templates[lang]);
                }
            });
        }
    }
    
    getTemplate(type, project = null) {
        const templates = {
            'synapse-main': `// Synapse Language Main File
// Generated by Synapse IDE

experiment MainExperiment {
    // Define uncertain variables
    uncertain temperature = 300.0 ± 5.0
    uncertain pressure = 1.0 ± 0.1
    
    // Parallel computation branches
    parallel {
        branch physics: calculate_thermodynamics(temperature, pressure)
        branch chemistry: analyze_reactions(temperature, pressure)
        branch optimization: monte_carlo_simulation(1000)
    }
    
    // Synthesize results
    synthesize: combine_results(physics, chemistry, optimization)
}`,
            
            'synapse-test': `// Synapse Test Suite
import main from "./main.syn"

test "uncertainty propagation" {
    uncertain x = 10.0 ± 1.0
    uncertain y = 20.0 ± 2.0
    uncertain result = x + y
    
    assert result.value ≈ 30.0
    assert result.error ≈ 2.236
}

test "parallel execution" {
    parallel {
        branch a: compute_slow_operation()
        branch b: compute_fast_operation()
    }
    
    assert execution_time < serial_time
}`,
            
            'synapse-example': `// Uncertainty Propagation Example

uncertain measurement_1 = 42.3 ± 0.5
uncertain measurement_2 = 17.8 ± 0.3

// Automatic error propagation
uncertain sum = measurement_1 + measurement_2
uncertain product = measurement_1 * measurement_2
uncertain ratio = measurement_1 / measurement_2

// Monte Carlo validation
monte_carlo validation {
    samples: 10000
    variables: [measurement_1, measurement_2]
    verify: [sum, product, ratio]
}`,
            
            'qubit-flow-main': `// Quantum Circuit Main File

// Initialize qubits
qubit q0 = |0⟩
qubit q1 = |0⟩

// Create Bell state circuit
circuit BellState {
    H gate on q0           // Hadamard on first qubit
    CNOT gate on q0, q1    // Controlled-NOT
    measure q0, q1         // Measure both qubits
}

// Execute circuit
execute BellState`,
            
            'quantum-net-main': `// Quantum Network Main File

// Define network nodes
node Alice at (0, 0)
node Bob at (100, 0)
node Charlie at (50, 86.6)

// Create quantum links
quantum_link Alice ↔ Bob
quantum_link Bob ↔ Charlie
quantum_link Charlie ↔ Alice

// Quantum teleportation protocol
protocol Teleportation {
    sender: Alice
    receiver: Bob
    
    entangle Alice.qubit ⊗ Bob.qubit
    measure Alice.qubit → classical_bits
    transmit classical_bits → Bob
    apply_correction Bob.qubit based_on classical_bits
}`,
            
            'flux-main': `// Flux Data Pipeline

flow DataProcessing {
    input → filter(valid_data) 
          → transform(normalize) 
          → map(feature_extraction)
          → reduce(aggregation)
          → output
}

async pipeline MLTraining {
    data_stream → batch(1000)
                → train_model
                → validate
                → optimize_hyperparameters
                → deploy
}`,
            
            'crowe-main': `// Crowe Language Main File

module Main {
    function main() -> Result<(), Error> {
        let data = load_data()?;
        let processed = process_data(data)?;
        let result = analyze(processed)?;
        
        print(result);
        Ok(())
    }
    
    function process_data(data: Array<i32>) -> Array<f64> {
        data.map(|x| x as f64 / 100.0)
            .filter(|&x| x > 0.0)
            .collect()
    }
}`,
            
            readme: `# ${project?.name || 'Synapse Project'}

${project?.metadata?.description || 'A Synapse Language project for scientific computing'}

## Languages Used
${project?.languages?.map(lang => `- ${lang}`).join('\n') || '- Synapse'}

## Project Structure
- \`src/\` - Source code files
- \`tests/\` - Test files
- \`examples/\` - Example code
- \`docs/\` - Documentation

## Getting Started
1. Open in Synapse IDE
2. Run tests: \`synapse test\`
3. Execute main: \`synapse run src/main.syn\`

## Features
- Uncertainty quantification
- Parallel execution
- Cross-language transpilation
- AI-assisted development

Generated by Synapse IDE v1.0
`
        };
        
        return templates[type] || '';
    }
    
    async openProject(projectPath) {
        try {
            // Load project configuration
            const projectConfig = await this.loadProjectConfig(projectPath);
            const project = await this.loadProjectStructure(projectConfig);
            
            this.currentProject = project;
            this.projects.set(project.id, project);
            
            this.addToRecent(project);
            this.updateProjectExplorer();
            this.updateProjectStatus();
            
            console.log(`Project opened: ${project.name}`);
            return project;
            
        } catch (error) {
            console.error('Failed to open project:', error);
            throw error;
        }
    }
    
    async saveProject() {
        if (!this.currentProject) return;
        
        try {
            // Save project configuration
            await this.saveProjectConfig(this.currentProject);
            
            // Save all open files
            await this.saveAllFiles();
            
            this.currentProject.modified = new Date();
            
            console.log(`Project saved: ${this.currentProject.name}`);
            
        } catch (error) {
            console.error('Failed to save project:', error);
            throw error;
        }
    }
    
    closeProject() {
        if (!this.currentProject) return;
        
        // Save before closing
        this.saveProject().then(() => {
            this.currentProject = null;
            this.updateProjectExplorer();
            this.updateProjectStatus();
            
            console.log('Project closed');
        });
    }
    
    addToRecent(project) {
        // Remove if already in recent
        this.recentProjects = this.recentProjects.filter(p => p.id !== project.id);
        
        // Add to beginning
        this.recentProjects.unshift({
            id: project.id,
            name: project.name,
            path: project.path,
            lastOpened: new Date()
        });
        
        // Keep only last 10
        this.recentProjects = this.recentProjects.slice(0, 10);
        this.saveRecentProjects();
    }
    
    updateProjectExplorer() {
        const explorer = document.getElementById('file-tree');
        if (!explorer) return;
        
        if (!this.currentProject) {
            explorer.innerHTML = `
                <div class="no-project">
                    <p>No project open</p>
                    <button data-action="new-project" class="btn-primary">New Project</button>
                    <button data-action="open-project" class="btn-secondary">Open Project</button>
                </div>
            `;
            return;
        }
        
        const project = this.currentProject;
        explorer.innerHTML = `
            <div class="project-header">
                <div class="project-name">${project.name}</div>
                <div class="project-actions">
                    <button data-action="project-settings" class="btn-icon" title="Settings">⚙️</button>
                    <button data-action="transpile-project" class="btn-icon" title="Transpile">🔄</button>
                </div>
            </div>
            <div class="project-tree">
                ${this.renderProjectTree(project.structure)}
            </div>
        `;
    }
    
    renderProjectTree(structure, path = '') {
        let html = '';
        
        Object.keys(structure).forEach(key => {
            const value = structure[key];
            const fullPath = path ? `${path}/${key}` : key;
            
            if (typeof value === 'object' && value !== null) {
                // Directory
                html += `
                    <div class="tree-item tree-folder" data-path="${fullPath}">
                        <span class="icon">📁</span>
                        <span class="name">${key}</span>
                    </div>
                    <div class="tree-children">
                        ${this.renderProjectTree(value, fullPath)}
                    </div>
                `;
            } else {
                // File
                const extension = key.split('.').pop();
                const icon = this.getFileIcon(extension);
                
                html += `
                    <div class="tree-item tree-file" data-path="${fullPath}" onclick="window.projectManager.openFile('${fullPath}')">
                        <span class="icon">${icon}</span>
                        <span class="name">${key}</span>
                    </div>
                `;
            }
        });
        
        return html;
    }
    
    getFileIcon(extension) {
        const icons = {
            syn: '🧠',
            synapse: '🧠',
            qf: '⚛️',
            qubit: '⚛️',
            qn: '🌐',
            qnet: '🌐',
            flux: '🌊',
            fl: '🌊',
            crowe: '🦅',
            cr: '🦅',
            py: '🐍',
            js: '📜',
            md: '📝',
            json: '📋',
            txt: '📄'
        };
        
        return icons[extension] || '📄';
    }
    
    async openFile(path) {
        if (!this.currentProject) return;
        
        const content = this.getFileContent(this.currentProject.structure, path);
        const extension = path.split('.').pop();
        const language = this.getLanguageFromExtension(extension);
        
        // Open in Monaco editor
        if (window.monacoEditor) {
            window.monacoEditor.setValue(content);
            monaco.editor.setModelLanguage(window.monacoEditor.getModel(), language);
        }
        
        // Update tab
        this.updateEditorTab(path, language);
        
        console.log(`Opened file: ${path}`);
    }
    
    getFileContent(structure, path) {
        const parts = path.split('/');
        let current = structure;
        
        for (const part of parts) {
            current = current[part];
            if (current === undefined) return '';
        }
        
        return current || '';
    }
    
    getLanguageFromExtension(extension) {
        const mapping = {
            syn: 'synapse',
            synapse: 'synapse',
            qf: 'qubit-flow',
            qubit: 'qubit-flow',
            qn: 'quantum-net',
            qnet: 'quantum-net',
            flux: 'flux',
            fl: 'flux',
            crowe: 'crowe',
            cr: 'crowe',
            py: 'python',
            js: 'javascript',
            json: 'json',
            md: 'markdown'
        };
        
        return mapping[extension] || 'plaintext';
    }
    
    updateEditorTab(filePath, language) {
        const tabBar = document.getElementById('tab-bar');
        if (!tabBar) return;
        
        // Remove existing tabs
        tabBar.querySelectorAll('.editor-tab').forEach(tab => tab.classList.remove('active'));
        
        // Check if tab already exists
        let tab = tabBar.querySelector(`[data-file="${filePath}"]`);
        if (!tab) {
            tab = document.createElement('div');
            tab.className = 'tab editor-tab';
            tab.setAttribute('data-file', filePath);
            
            const fileName = filePath.split('/').pop();
            tab.innerHTML = `
                <span class="tab-title">${fileName}</span>
                <button class="tab-close" onclick="this.parentElement.remove()">×</button>
            `;
            
            tabBar.appendChild(tab);
        }
        
        tab.classList.add('active');
    }
    
    updateProjectStatus() {
        const statusElement = document.getElementById('file-status');
        if (!statusElement) return;
        
        if (this.currentProject) {
            statusElement.textContent = `Project: ${this.currentProject.name}`;
        } else {
            statusElement.textContent = 'No project';
        }
    }
    
    showNewProjectDialog() {
        const dialog = document.createElement('div');
        dialog.className = 'modal-overlay';
        dialog.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Create New Project</h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
                </div>
                <div class="modal-body">
                    <form id="new-project-form">
                        <div class="form-group">
                            <label>Project Name</label>
                            <input type="text" name="name" required>
                        </div>
                        <div class="form-group">
                            <label>Project Type</label>
                            <select name="type">
                                <option value="synapse">Synapse Project</option>
                                <option value="multi-language">Multi-Language Project</option>
                                <option value="research">Research Project</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Primary Language</label>
                            <select name="primaryLanguage">
                                <option value="synapse">Synapse</option>
                                <option value="qubit-flow">Qubit-Flow</option>
                                <option value="quantum-net">Quantum-Net</option>
                                <option value="flux">Flux</option>
                                <option value="crowe">Crowe</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Additional Languages</label>
                            <div class="checkbox-group">
                                <label><input type="checkbox" name="languages" value="python"> Python</label>
                                <label><input type="checkbox" name="languages" value="javascript"> JavaScript</label>
                                <label><input type="checkbox" name="languages" value="cpp"> C++</label>
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea name="description" rows="3"></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                    <button class="btn-primary" onclick="window.projectManager.handleNewProject()">Create Project</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(dialog);
    }
    
    async handleNewProject() {
        const form = document.getElementById('new-project-form');
        const formData = new FormData(form);
        
        const config = {
            name: formData.get('name'),
            type: formData.get('type'),
            languages: [formData.get('primaryLanguage')],
            description: formData.get('description'),
            author: 'Synapse IDE User'
        };
        
        // Add additional languages
        const additionalLangs = formData.getAll('languages');
        config.languages.push(...additionalLangs);
        
        try {
            await this.createProject(config);
            
            // Close dialog
            document.querySelector('.modal-overlay').remove();
            
        } catch (error) {
            console.error('Failed to create project:', error);
            alert('Failed to create project: ' + error.message);
        }
    }
    
    showTranspileDialog() {
        if (!this.currentProject) return;
        
        const dialog = document.createElement('div');
        dialog.className = 'modal-overlay';
        dialog.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Cross-Language Transpilation</h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
                </div>
                <div class="modal-body">
                    <div class="transpile-options">
                        <div class="form-group">
                            <label>Source Language</label>
                            <select id="source-language">
                                ${this.currentProject.languages.map(lang => 
                                    `<option value="${lang}">${lang}</option>`
                                ).join('')}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Target Languages</label>
                            <div class="checkbox-group">
                                <label><input type="checkbox" value="python"> Python</label>
                                <label><input type="checkbox" value="javascript"> JavaScript</label>
                                <label><input type="checkbox" value="cpp"> C++</label>
                                <label><input type="checkbox" value="rust"> Rust</label>
                                <label><input type="checkbox" value="julia"> Julia</label>
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Optimization Level</label>
                            <select id="optimization-level">
                                <option value="basic">Basic Translation</option>
                                <option value="optimized">Performance Optimized</option>
                                <option value="readable">Human Readable</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                    <button class="btn-primary" onclick="window.projectManager.transpileProject()">Transpile</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(dialog);
    }
    
    async transpileProject() {
        const sourceLanguage = document.getElementById('source-language').value;
        const targetLanguages = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
            .map(cb => cb.value);
        const optimizationLevel = document.getElementById('optimization-level').value;
        
        if (targetLanguages.length === 0) {
            alert('Please select at least one target language');
            return;
        }
        
        try {
            const results = await this.transpiler.transpileProject(
                this.currentProject,
                sourceLanguage,
                targetLanguages,
                optimizationLevel
            );
            
            this.showTranspileResults(results);
            document.querySelector('.modal-overlay').remove();
            
        } catch (error) {
            console.error('Transpilation failed:', error);
            alert('Transpilation failed: ' + error.message);
        }
    }
    
    showTranspileResults(results) {
        // Implementation for showing transpilation results
        console.log('Transpilation results:', results);
    }
}

// Cross-Language Transpiler
class CrossLanguageTranspiler {
    constructor() {
        this.patterns = new Map();
        this.setupTranspilationPatterns();
    }
    
    setupTranspilationPatterns() {
        // Synapse to Python patterns
        this.patterns.set('synapse->python', {
            uncertainty: {
                pattern: /uncertain\s+(\w+)\s*=\s*([0-9.]+)\s*±\s*([0-9.]+)/g,
                replacement: 'from uncertainties import ufloat\n$1 = ufloat($2, $3)'
            },
            parallel: {
                pattern: /parallel\s*\{([^}]+)\}/g,
                replacement: 'import concurrent.futures\nwith concurrent.futures.ThreadPoolExecutor() as executor:\n    $1'
            }
        });
        
        // Add more language patterns...
    }
    
    async transpileProject(project, sourceLanguage, targetLanguages, optimizationLevel) {
        const results = new Map();
        
        for (const targetLanguage of targetLanguages) {
            const transpiled = await this.transpileToLanguage(
                project,
                sourceLanguage,
                targetLanguage,
                optimizationLevel
            );
            results.set(targetLanguage, transpiled);
        }
        
        return results;
    }
    
    async transpileToLanguage(project, sourceLanguage, targetLanguage, optimizationLevel) {
        // Implementation for specific language transpilation
        const patternKey = `${sourceLanguage}->${targetLanguage}`;
        const patterns = this.patterns.get(patternKey);
        
        if (!patterns) {
            throw new Error(`No transpilation patterns for ${sourceLanguage} to ${targetLanguage}`);
        }
        
        // Apply transpilation patterns
        // This is a simplified version - real implementation would be much more complex
        
        return {
            files: new Map(),
            warnings: [],
            errors: []
        };
    }
}

// Initialize project manager
window.projectManager = new SynapseProjectManager();