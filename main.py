from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Carrega a chave da OpenRouter
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

@app.route('/')
def home():
    return "🧠 API ZapAgent Gerador Profissional está online."

@app.route('/gerar-resposta-profissional', methods=['POST'])
def gerar_resposta():
    data = request.get_json()

    mensagem = data.get("mensagem", "").strip()
    tom = data.get("tom", "Profissional").strip()
    tipo = data.get("tipo", "Resposta").strip()

    if not mensagem:
        return jsonify({"resposta": "⚠️ Nenhuma mensagem recebida."}), 400

    if not OPENROUTER_API_KEY:
        return jsonify({"resposta": "❌ Chave da OpenRouter ausente no servidor."}), 500

    prompt = f"""
Você é um assistente virtual com tom {tom.lower()} especializado em {tipo.lower()}.
Crie uma resposta clara, simpática e profissional para a seguinte mensagem de um cliente:

Mensagem do cliente: "{mensagem}"

Responda de forma direta e eficaz.
""".strip()

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://zapagent-ai-builder.lovable.app",
        "X-Title": "ZapAgent Gerador Profissional"
    }

    body = {
        "model": "deepseek/deepseek-r1:free",  # Pode trocar por outro da OpenRouter
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": mensagem}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
        response.raise_for_status()
        resposta_data = response.json()

        if "choices" in resposta_data and resposta_data["choices"]:
            resposta_texto = resposta_data["choices"][0]["message"]["content"].strip()
        else:
            resposta_texto = "⚠️ Nenhuma resposta válida recebida da IA."

        return jsonify({"resposta": resposta_texto})

    except Exception as e:
        return jsonify({"resposta": f"❌ Erro ao gerar resposta: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
