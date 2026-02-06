from flask import Flask, request, jsonify, make_response
import joblib
import numpy as np
import pandas as pd

app = Flask(__name__)

# Disable caching for development
@app.after_request
def add_header(response):
    """Add cache-control headers to prevent caching"""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Load the trained model
model = joblib.load("milk_quality_model.pkl")

# Cute grade mapping
grade_map = {0: 'low', 1: 'medium', 2: 'high'}
grade_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}

@app.route('/')
def cute_home():
    """Cute homepage"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🐄 Milk Quality Checker 🐄</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🐄 Milk Quality Checker 🐄</h1>
                <p class="subtitle">Making dairy testing adorable! ✨</p>
            </div>
            
            <div class="form-container">
                <h2>🌸 Enter Milk Details 🌸</h2>
                <p class="hint">💡 Hint: pH (3-10), Temp (20-90)</p>
                <form id="milkForm">
                    <div class="form-group">
                        <label for="ph">🧪 pH Level:</label>
                        <input type="number" step="0.1" id="ph" name="ph" placeholder="e.g., 6.6" min="3" max="10" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="temperature">🌡️ Temperature (°C):</label>
                        <input type="number" id="temperature" name="temperature" placeholder="e.g., 35" min="20" max="90" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="taste">👅 Taste:</label>
                        <select id="taste" name="taste" required>
                            <option value="">Select...</option>
                            <option value="1">Good (1)</option>
                            <option value="0">Bad (0)</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="odor">👃 Odor:</label>
                        <select id="odor" name="odor" required>
                            <option value="">Select...</option>
                            <option value="1">Good (1)</option>
                            <option value="0">Bad (0)</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="fat">🥛 Fat:</label>
                        <select id="fat" name="fat" required>
                            <option value="">Select...</option>
                            <option value="1">High (1)</option>
                            <option value="0">Low (0)</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="turbidity">💧 Turbidity:</label>
                        <select id="turbidity" name="turbidity" required>
                            <option value="">Select...</option>
                            <option value="1">High (1)</option>
                            <option value="0">Low (0)</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="colour">🎨 Colour (240-255):</label>
                        <input type="number" id="colour" name="colour" placeholder="e.g., 255" min="240" max="255" required>
                    </div>
                    
                    <button type="submit" class="predict-btn">🔮 Predict Quality</button>
                </form>
                
                <div id="result" class="result-container" style="display:none;">
                    <h3>✨ Prediction Result ✨</h3>
                    <div id="resultContent"></div>
                </div>
            </div>
            
            <div class="footer">
                <p>🐮 Made with love for milk lovers! 🐮</p>
            </div>
        </div>
        
        <script>
            document.getElementById('milkForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const data = {};
                formData.forEach((value, key) => data[key] = parseFloat(value));
                
                try {
                    const response = await fetch('/predict', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    const resultDiv = document.getElementById('result');
                    const resultContent = document.getElementById('resultContent');
                    
                    resultDiv.style.display = 'block';
                    
                    if(result.success) {
                        const emoji = grade_emoji[result.grade];
                        resultContent.innerHTML = `
                            <div class="grade-display ${result.grade}">
                                <span class="grade-emoji">${emoji}</span>
                                <span class="grade-text">${result.grade.toUpperCase()}</span>
                                <span class="grade-emoji">${emoji}</span>
                            </div>
                            <p class="confidence">Confidence: ${(result.confidence * 100).toFixed(2)}% 💕</p>
                        `;
                    } else {
                        resultContent.innerHTML = `<p class="error">❌ ${result.error}</p>`;
                    }
                } catch (error) {
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('resultContent').innerHTML = `<p class="error">❌ Something went wrong!</p>`;
                }
            });
            
            // Define grade_emoji for JavaScript
            const grade_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'};
        </script>
    </body>
    </html>
    '''

@app.route('/predict', methods=['POST'])
def predict():
    """Predict milk quality"""
    try:
        data = request.get_json()
        print("Received data:", data)
        
        # Extract and validate features
        ph = float(data['ph'])
        temperature = float(data['temperature'])
        taste = float(data['taste'])
        odor = float(data['odor'])
        fat = float(data['fat'])
        turbidity = float(data['turbidity'])
        colour = float(data['colour'])
        
        # Validate inputs
        if not (0 <= ph <= 14):
            return jsonify({'success': False, 'error': f'pH must be between 0-14, got {ph}'})
        if not (0 <= temperature <= 100):
            return jsonify({'success': False, 'error': f'Temperature must be 0-100°C, got {temperature}'})
        
        features = [ph, temperature, taste, odor, fat, turbidity, colour]
        print("Features:", features)
        
        # Make prediction
        prediction = model.predict([features])[0]
        probabilities = model.predict_proba([features])[0]
        confidence = max(probabilities)
        
        grade = grade_map[int(prediction)]
        
        return jsonify({
            'success': True,
            'grade': grade,
            'confidence': float(confidence)
        })
    
    except Exception as e:
        print("Error:", str(e))
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/cute')
def cute_endpoint():
    """Bonus cute endpoint with fun facts"""
    return jsonify({
        'message': '🐄 Moo! Welcome to the Milk Quality API! 🐄',
        'endpoints': {
            '/': '🌸 Cute homepage with form',
            '/predict': '🔮 POST here for predictions',
            '/cute': '✨ This fun endpoint!'
        },
        'fun_fact': 'Did you know? Cows have best friends and they get stressed when separated! 🐄💕'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

