from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "API OOH funcionando!",
        "status": "success",
        "version": "1.0"
    })

@app.route('/test')
def test():
    # Teste simples com pandas
    data = {
        'setor': ['001', '002', '003'],
        'populacao': [1000, 1500, 2000]
    }
    df = pd.DataFrame(data)
    
    return jsonify({
        "data": df.to_dict('records'),
        "total_setores": len(df)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
