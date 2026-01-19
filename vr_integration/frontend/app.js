/**
 * Main Application JavaScript
 * Handles question generation, answer checking, and VR scene management
 */

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Global state
let currentQuestion = null;
let currentVRConfig = null;
let answerSelected = false;

/**
 * Generate a new question
 */
async function generateQuestion() {
    console.log('Generating new question...');
    
    // Get visual dependency filter
    const gorselFilter = document.getElementById('gorsel-filter').value;
    console.log('Visual filter:', gorselFilter || 'All');
    
    // Show loading
    document.getElementById('loading').classList.add('active');
    document.getElementById('question-container').style.display = 'none';
    document.getElementById('new-question-btn').disabled = true;
    
    // Reset state
    answerSelected = false;
    currentQuestion = null;
    currentVRConfig = null;
    
    // Hide result message
    document.getElementById('result-message').style.display = 'none';
    
    try {
        // Build URL with filter parameter
        let url = `${API_BASE_URL}/generate-question`;
        if (gorselFilter) {
            url += `?gorsel_filter=${encodeURIComponent(gorselFilter)}`;
        }
        
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Question generated:', data);

        // Store question
        currentQuestion = data.question;
        currentVRConfig = data.vr_config;

        // Display question
        displayQuestion(data.question);
        
        // Display prediction if available
        if (data.prediction) {
            displayPrediction(data.prediction);
        }
        
        // Update VR panel
        if (data.vr_config) {
            updateVRPanel(data.vr_config);
        }

        } catch (error) {
        console.error('Question generation error:', error);
        let errorMsg = `Hata: ${error.message}`;
        if (error.message.includes('503') || error.message.includes('not available')) {
            errorMsg += '\n\nSeçilen filtreye uygun soru bulunamadı. Lütfen farklı bir filtre seçin.';
        }
        alert(errorMsg);
    } finally {
        document.getElementById('loading').classList.remove('active');
        document.getElementById('question-container').style.display = 'block';
        document.getElementById('new-question-btn').disabled = false;
    }
}

/**
 * Display question and options
 */
function displayQuestion(question) {
    // Display question text
    document.getElementById('question-text').textContent = question.soru_metin;
    
    // Clear and create options
    const optionsContainer = document.getElementById('options-container');
    optionsContainer.innerHTML = '';
    
    const options = question.secenekler || {};
    const optionKeys = Object.keys(options).sort(); // A, B, C, D, E
    
    optionKeys.forEach(opt => {
        const btn = document.createElement('button');
        btn.className = 'option-btn';
        btn.innerHTML = `
            <span class="option-label">${opt})</span>
            <span class="option-text">${options[opt]}</span>
        `;
        btn.onclick = () => checkAnswer(opt, question.dogru_cevap);
        optionsContainer.appendChild(btn);
    });
}

/**
 * Check if selected answer is correct
 */
function checkAnswer(selectedAnswer, correctAnswer) {
    if (answerSelected) {
        return; // Already answered
    }
    
    answerSelected = true;
    
    // Disable all option buttons
    const optionButtons = document.querySelectorAll('.option-btn');
    optionButtons.forEach(btn => {
        btn.disabled = true;
    });
    
    // Highlight correct answer
    const correctBtn = Array.from(optionButtons).find(btn => {
        const label = btn.querySelector('.option-label').textContent.trim();
        return label.startsWith(correctAnswer);
    });
    
    if (correctBtn) {
        correctBtn.classList.add('correct');
    }
    
    // Check if selected answer is correct
    const isCorrect = selectedAnswer.toUpperCase() === correctAnswer?.toUpperCase();
    
    // Highlight selected answer
    const selectedBtn = Array.from(optionButtons).find(btn => {
        const label = btn.querySelector('.option-label').textContent.trim();
        return label.startsWith(selectedAnswer);
    });
    
    if (selectedBtn && !isCorrect) {
        selectedBtn.classList.add('incorrect');
    }
    
    // Show result message
    const resultMessage = document.getElementById('result-message');
    resultMessage.style.display = 'block';
    
    if (isCorrect) {
        resultMessage.textContent = '✅ Doğru Cevap! Tebrikler!';
        resultMessage.className = 'result-message correct';
    } else {
        resultMessage.textContent = `❌ Yanlış Cevap! Doğru cevap: ${correctAnswer}`;
        resultMessage.className = 'result-message incorrect';
    }
}

/**
 * Display prediction information
 */
function displayPrediction(prediction) {
    const infoBox = document.getElementById('prediction-info');
    const predictionText = document.getElementById('prediction-text');
    
    if (prediction) {
        const conf = prediction.confidence || {};
        predictionText.innerHTML = `
            <strong>Alt Konu:</strong> ${prediction.alt_konu} 
            (${(conf.alt_konu * 100).toFixed(1)}%)<br>
            <strong>Soru Tipi:</strong> ${prediction.soru_tipi} 
            (${(conf.soru_tipi * 100).toFixed(1)}%)
        `;
        infoBox.style.display = 'block';
    } else {
        infoBox.style.display = 'none';
    }
}

/**
 * Update VR panel based on configuration
 */
function updateVRPanel(vrConfig) {
    const vrStatus = document.getElementById('vr-status');
    const startVRBtn = document.getElementById('start-vr-btn');

    if (vrConfig && vrConfig.activated) {
        vrStatus.textContent = '✅ VR Aktif';
        vrStatus.className = 'vr-status active';
        startVRBtn.style.display = 'block';
        
        // Auto-start VR for guided and full modes
        if (vrConfig.mode === 'guided' || vrConfig.mode === 'full') {
            console.log('Auto-starting VR (mode:', vrConfig.mode, ')');
            setTimeout(() => {
                startVR();
            }, 500);
        }
    } else {
        vrStatus.textContent = '❌ VR Kapalı';
        vrStatus.className = 'vr-status inactive';
        startVRBtn.style.display = 'none';
    }
}

/**
 * Start VR scene
 */
async function startVR() {
    if (!currentVRConfig || !currentVRConfig.activated) {
        alert('VR aktif değil!');
        return;
    }

    console.log('Starting VR scene:', currentVRConfig);

    try {
        // Import and initialize VR scene
        const module = await import('./vr_scenes/scene_manager.js');
        const sceneManager = module.getSceneManager();
        
        // Check if canvas exists
        const canvas = document.getElementById('vr-canvas');
        if (!canvas) {
            throw new Error('VR canvas not found!');
        }

        console.log('Loading scene:', currentVRConfig.scene_type);
        sceneManager.loadScene(
            currentVRConfig.scene_type,
            currentVRConfig.config,
            currentVRConfig.mode
        );
        console.log('VR scene loaded successfully!');
    } catch (error) {
        console.error('VR scene load error:', error);
        alert(`VR sahnesi yüklenirken hata oluştu: ${error.message}\n\nKonsolu kontrol edin (F12).`);
    }
}

// Export to window for onclick handlers
window.startVR = startVR;
window.generateQuestion = generateQuestion;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('LGS VR Math Learning - Frontend loaded');
    
    // Add event listeners
    const newQuestionBtn = document.getElementById('new-question-btn');
    if (newQuestionBtn) {
        newQuestionBtn.addEventListener('click', generateQuestion);
        console.log('New question button event listener added');
    }
    
    const startVRBtn = document.getElementById('start-vr-btn');
    if (startVRBtn) {
        startVRBtn.addEventListener('click', startVR);
        console.log('Start VR button event listener added');
    }
    
    // Check API health
    fetch(`${API_BASE_URL}/health`)
        .then(res => res.json())
        .then(data => {
            console.log('API Health:', data);
            if (data.model === 'not_loaded') {
                console.warn('Model not loaded. Some features may not work.');
            }
            if (data.question_generator === 'not_loaded') {
                console.warn('Question generator not loaded.');
            }
            
            // Auto-generate first question
            console.log('Auto-generating first question...');
            generateQuestion();
        })
        .catch(err => {
            console.error('API connection failed:', err);
            alert(`API'ye bağlanılamadı: ${API_BASE_URL}\n\nLütfen API sunucusunun çalıştığından emin olun.`);
        });
});
