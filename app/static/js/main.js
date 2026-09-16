// Main JavaScript file for the multiplication table app

// Sound effects using Web Audio API
const audioContext = new (window.AudioContext || window.webkitAudioContext)();

function playSound(type) {
    if (!getSoundEnabled()) return;
    
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    if (type === 'correct') {
        oscillator.frequency.value = 523.25; // C5
        oscillator.type = 'sine';
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.3);
    } else if (type === 'wrong') {
        oscillator.frequency.value = 220; // A3
        oscillator.type = 'square';
        gainNode.gain.setValueAtTime(0.2, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.2);
    } else if (type === 'click') {
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.1);
    }
}

function getSoundEnabled() {
    const soundToggle = document.getElementById('sound-toggle');
    return soundToggle ? soundToggle.checked : true;
}

// Feedback display delays (ms), configurable on the settings page
function getFeedbackDelays() {
    return {
        correct: parseInt(localStorage.getItem('feedbackDelayCorrect')) || 500,
        wrong: parseInt(localStorage.getItem('feedbackDelayWrong')) || 2000
    };
}

// Web Speech API for reading questions
function speakQuestion(left, right, answer) {
    if (!('speechSynthesis' in window)) return;
    
    const text = `${left} умножить на ${right} равно ${answer}`;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ru-RU';
    utterance.rate = 0.8;
    
    window.speechSynthesis.speak(utterance);
}

// Initialize sound toggle
document.addEventListener('DOMContentLoaded', function() {
    const soundToggle = document.getElementById('sound-toggle');
    if (soundToggle) {
        soundToggle.addEventListener('change', function() {
            localStorage.setItem('soundEnabled', this.checked);
        });
        
        const savedSoundEnabled = localStorage.getItem('soundEnabled');
        if (savedSoundEnabled !== null) {
            soundToggle.checked = savedSoundEnabled === 'true';
        }
    }
    
    const delayCorrect = document.getElementById('delay-correct');
    if (delayCorrect) {
        delayCorrect.value = localStorage.getItem('feedbackDelayCorrect') || '500';
        delayCorrect.addEventListener('change', function() {
            localStorage.setItem('feedbackDelayCorrect', this.value);
        });
    }
    
    const delayWrong = document.getElementById('delay-wrong');
    if (delayWrong) {
        delayWrong.value = localStorage.getItem('feedbackDelayWrong') || '2000';
        delayWrong.addEventListener('change', function() {
            localStorage.setItem('feedbackDelayWrong', this.value);
        });
    }
});

// Keyboard navigation improvements
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const modal = document.getElementById('reset-modal');
        if (modal && !modal.classList.contains('hidden')) {
            modal.classList.add('hidden');
        }
    }
});
