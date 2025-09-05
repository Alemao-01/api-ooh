from flask import Flask, request, jsonify
import geopandas as gpd
from shapely.geometry import Point
import os

app = Flask(__name__)

# Carregar dados de SC uma vez só (quando a API inicializar)
print("🔄 Carregando dados de SC...")
try:
    setores_sc = gpd.read_file("SC_setores_comprimido.shp")
    print(f"✅ {len(setores_sc)} setores carregados!")
    print(f"📊 Colunas disponíveis: {list(setores_sc.columns)}")
except Exception as e:
    print(f"❌ Erro ao carregar: {e}")
    setores_sc = None

@app.route('/')
def home():
    """Página inicial para testar se API está funcionando"""
    return {
        "status": "API Geocoding SC funcionando!",
        "versao": "2.0 - Arquivo Comprimido",
        "setores_carregados": len(setores_sc) if setores_sc is not None else 0,
        "tamanho_arquivo": "4.4 MB (era 115 MB)",
        "uso": "/buscar?lat=-27.1&lng=-52.6",
        "exemplo_floripa": "/buscar?lat=-27.5954&lng=-48.5480"
    }

@app.route('/buscar')
def buscar_setor():
    """Buscar setor censitário por coordenada"""
    
    try:
        # Pegar parâmetros
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        
        if not lat or not lng:
            return jsonify({
                "erro": "Parâmetros obrigatórios: lat e lng",
                "exemplo": "/buscar?lat=-27.5954&lng=-48.5480",
                "exemplo_chapeco": "/buscar?lat=-27.1&lng=-52.6"
            }), 400
        
        # Converter para números
        lat = float(lat)
        lng = float(lng)
        
        # Validar coordenadas básicas
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            return jsonify({"erro": "Coordenadas inválidas"}), 400
        
        # Validar se está aproximadamente em SC
        if not (-29.5 <= lat <= -25.5) or not (-54 <= lng <= -48):
            return jsonify({
                "erro": "Coordenadas fora de Santa Catarina",
                "dica": "SC fica entre lat -29.5 a -25.5 e lng -54 a -48",
                "exemplo_floripa": "lat=-27.5954, lng=-48.5480"
            }), 400
        
        # Verificar se dados estão carregados
        if setores_sc is None:
            return jsonify({"erro": "Dados não carregados"}), 500
        
        # Criar ponto
        ponto = Point(lng, lat)
        
        # Buscar setor que contém o ponto
        for idx, row in setores_sc.iterrows():
            try:
                if row['geometry'].contains(ponto):
                    return jsonify({
                        "codigo_setor": row['CD_SETOR'],
                        "status": "encontrado",
                        "coordenadas": {
                            "lat": lat,
                            "lng": lng
                        },
                        "info": "Setor censitário encontrado em SC"
                    })
            except Exception as e:
                continue
        
        # Se não encontrou
        return jsonify({
            "codigo_setor": None,
            "status": "nao_encontrado",
            "coordenadas": {
                "lat": lat,
                "lng": lng
            },
            "mensagem": "Coordenada em SC mas setor não encontrado",
            "dica": "Pode estar em área não mapeada ou coordenada muito precisa"
        })
        
    except ValueError:
        return jsonify({
            "erro": "lat e lng devem ser números",
            "exemplo": "/buscar?lat=-27.5954&lng=-48.5480"
        }), 400
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

@app.route('/health')
def health():
    """Verificar saúde da API"""
    return jsonify({
        "status": "ok",
        "dados_carregados": setores_sc is not None,
        "total_setores": len(setores_sc) if setores_sc is not None else 0,
        "arquivo": "SC_setores_comprimido.shp",
        "tamanho": "4.4 MB"
    })

@app.route('/teste')
def teste():
    """Endpoint para testar com coordenadas conhecidas"""
    exemplos = [
        {
            "cidade": "Florianópolis - Centro",
            "lat": -27.5954,
            "lng": -48.5480,
            "url": "/buscar?lat=-27.5954&lng=-48.5480"
        },
        {
            "cidade": "Chapecó - Centro", 
            "lat": -27.1,
            "lng": -52.6,
            "url": "/buscar?lat=-27.1&lng=-52.6"
        },
        {
            "cidade": "Blumenau - Centro",
            "lat": -26.9194,
            "lng": -49.0661,
            "url": "/buscar?lat=-26.9194&lng=-49.0661"
        }
    ]
    
    return jsonify({
        "message": "Coordenadas de teste para SC",
        "exemplos": exemplos
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)