from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import logging

app = Flask(__name__)

# Configura CORS liberando todas origens (pode limitar depois)
CORS(app)

# Configura logging para DEBUG (exibe no console do Render)
logging.basicConfig(level=logging.DEBUG)

# Carrega a chave da OpenRouter da variável ambiente
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

@app.route('/')
def home():
    return "🧠 API ZapAgent Gerador Profissional está online."

@app.route('/gerar-resposta-profissional', methods=['POST'])
def gerar_resposta():
    try:
        data = request.get_json(force=True)
        app.logger.debug(f"Recebido JSON: {data}")

        mensagem = data.get("mensagem", "").strip()
        tom = data.get("tom", "profissional").strip().lower()
        tipo = data.get("tipo", "resposta").strip().lower()

        if not mensagem:
            return jsonify({"resposta": "⚠️ Nenhuma mensagem recebida."}), 400

        if not OPENROUTER_API_KEY:
            app.logger.error("Chave da OpenRouter não definida.")
            return jsonify({"resposta": "❌ Chave da OpenRouter ausente no servidor."}), 500

        prompt = (
            f"Você é um assistente virtual com tom {tom} especializado em {tipo}. "
            f"Crie uma resposta clara, simpática e profissional para a seguinte mensagem de um cliente:\n\n"
            f"Mensagem do cliente: \"{mensagem}\"\n\n"
            f"Responda de forma direta e eficaz."
        )

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            # Se esses headers não forem necessários para OpenRouter, podem ser removidos
            "Referer": "https://zapagent-ai-builder.lovable.app",
            "X-Title": "ZapAgent Gerador Profissional"
        }

        body = {
            "model": "deepseek/deepseek-r1:free",  # Ajuste conforme modelo disponível
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": mensagem}
            ]
        }

        app.logger.debug(f"Enviando para OpenRouter: {body}")

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=body,
            timeout=15  # Timeout de 15 segundos para evitar travamentos
        )
        response.raise_for_status()

        resposta_data = response.json()
        app.logger.debug(f"Resposta OpenRouter: {resposta_data}")

        if "choices" in resposta_data and resposta_data["choices"]:
            resposta_texto = resposta_data["choices"][0]["message"]["content"].strip()
        else:
            resposta_texto = "⚠️ Nenhuma resposta válida recebida da IA."

        return jsonify({"resposta": resposta_texto})

    except requests.exceptions.Timeout:
        app.logger.error("Timeout ao conectar com OpenRouter.")
        return jsonify({"resposta": "❌ Tempo esgotado ao tentar gerar resposta. Tente novamente."}), 504

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Erro na requisição OpenRouter: {str(e)}")
        return jsonify({"resposta": f"❌ Erro na requisição ao gerar resposta: {str(e)}"}), 502

    except Exception as e:
        app.logger.error(f"Erro interno: {str(e)}")
        return jsonify({"resposta": f"❌ Erro interno ao gerar resposta: {str(e)}"}), 500

if __name__ == '__main__':
    # Usa porta do ambiente (Render define variável PORT)
    port = int(os.environ.get("PORT", 4000))
    app.run(host='0.0.0.0', port=port)
    
    # Em produção, usar gunicorn ou waitress:
    # gunicorn main:app --bind 0.0.0.0:$PORT
