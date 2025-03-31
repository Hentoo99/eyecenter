from flask import Flask, render_template, request, redirect, url_for, flash
import os
import telegram
import asyncio
from threading import Thread
from dotenv import load_dotenv
from datetime import datetime


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key')  # Aggiunto secret_key
app.config['WTF_CSRF_ENABLED'] = True  

async def send_telegram_message_async(message):
    bot = telegram.Bot(token=os.getenv('TOKEN_TELEGRAM'))
    await bot.send_message(chat_id=os.getenv('ID_CHAT'), text=message)

def send_telegram_message(message):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_telegram_message_async(message))
    finally:
        loop.close()

@app.route('/')
def home():
    return render_template('index.html', 
                         email=os.getenv('EMAIL'), 
                         numero=os.getenv('NUMBER'))

@app.route('/studio')
def thestudio():
    return render_template('studio.html', 
                         email=os.getenv('EMAIL'), 
                         numero=os.getenv('NUMBER'))

@app.route('/contatti', methods=['GET', 'POST'])
def contatti():
    if request.method == 'POST':
        print("Mando form")
        try:
            # Recupera i dati dal form
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            reason = request.form.get('reason')
            message = request.form.get('message', '')
            print(1)
            # Validazione
            if not all([name, email, phone, reason]):
                flash('Per favore compila tutti i campi obbligatori', 'error')
                return redirect(url_for('contatti'))

            # Prepara il messaggio per Telegram
            telegram_msg = (
                "🆕 Nuova richiesta dal sito web!\n\n"
                f"🏥 Centro Oculistico Rubino\n"
                f"👤 Nome: {name}\n"
                f"📧 Email: {email}\n"
                f"📞 Tel: {phone}\n"
                f"🔍 Motivo: {reason}\n"
                f"📝 Messaggio: {message or 'Nessun messaggio'}\n\n"
                f"⏰ Richiesta ricevuta il: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            )

            print("Sto inviando il messaggio")
            # Invia a Telegram in background
            Thread(target=send_telegram_message, args=(telegram_msg,)).start()

            flash('Grazie! La tua richiesta è stata inviata con successo.', 'success')
            return redirect(url_for('contatti'))

        except Exception as e:
            app.logger.error(f"Errore nell'invio del form: {str(e)}")
            flash('Si è verificato un errore durante l\'invio della richiesta.', 'error')
            return redirect(url_for('contatti'))

    return render_template('contacts.html', 
                         email=os.getenv('EMAIL'), 
                         numero=os.getenv('NUMBER'))

if __name__ == '__main__':
    app.run(debug=True)