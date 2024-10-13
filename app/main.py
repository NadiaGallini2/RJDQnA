from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import chromadb
import uvicorn
from pydantic import BaseModel
import html  # Добавляем стандартную библиотеку для экранирования HTML

app = FastAPI()

# Подключение статических файлов и шаблонов
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

client = chromadb.Client()
collection = client.create_collection('documents')

class ChatMessage(BaseModel):
    message: str

@app.get('/', response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post('/upload-pdf')
async def upload_pdf(file: UploadFile = File(...)):
    contents = await file.read()
    doc_id = str(file.filename)
    collection.add([contents], ids=[doc_id])
    return {'filename': file.filename, 'file_id': doc_id}

@app.get('/documents')
async def list_documents():
    docs = collection.list()
    return docs

@app.get('/document/{doc_id}')
async def get_document(doc_id: str):
    doc = collection.get(doc_ids=[doc_id])
    return doc

@app.post('/sync-db')
async def sync_db():
    # Здесь добавьте логику для синхронизации с базой данных
    return {"status": "Синхронизация успешно завершена"}

@app.post('/chat')
async def chat_endpoint(chat: ChatMessage):
    user_message = chat.message
    response = chatbot_response(user_message)
    return {"response": response}

def chatbot_response(escaped_message):
    if "0" in escaped_message.lower():
        return "Здравствуйте! Как я могу помочь Вам сегодня?\n\n**Мои функции Вы можете получить набрав**, *ф*, или посмотреть по [ссылке](https://example.com)."
    
    elif "ф" in escaped_message.lower():
        return ("Вот что я могу для вас сделать:\n\n"
                "0 - **Поддержка Разметки** для сообщений.\n\n"
                "1 - **Размер оплаты за посещение дошкольного учреждения**\n\n"
                "2 - **Как подать заявку на путёвку в лагерь детям?**\n\n"
                "3 - **Условия направления ребенка в детский лагерь компании**\n\n"
                "4 - **Какие льготы положены моей семье?**\n\n"
                "5 - **Какие льготы мне положены?**\n\n"
                "Введите номер категории, чтобы получить больше информации.")
    
    elif "1" in escaped_message:
        return "# Размер оплаты за посещение дошкольного учреждения\nОплата за посещение ребёнком детского сада определяется в соответствии с Положением об установлении стоимости и оплате услуг в дошкольных группах частных образовательных учреждений ОАО «РЖД» и зависит от количества детей в семье и социального статуса работника."
    
    elif "2" in escaped_message:
        return "# Как подать заявку на путёвку в лагерь детям?\nПутевки предоставляются работникам, имеющим детей школьного возраста от 7 до 16 лет. Работнику необходимо подать заявку через Сервисный портал работника или написать заявление в Комиссию по распределению путевок."
    
    elif "3" in escaped_message:
        return "# Условия направления ребенка в детский лагерь компании\nПутевки предоставляются работникам, имеющим детей школьного возраста от 7 до 16 лет. Порядок получения путевок в детские оздоровительные лагеря определен распоряжением ОАО «РЖД»."
    
    elif "4" in escaped_message:
        return "# Какие льготы положены моей семье?\nПодробную информацию можно получить у специалистов по управлению персоналом, в профсоюзной организации или на Сервисном портале."
    
    elif "5" in escaped_message:
        return "# Какие льготы мне положены?\nОзнакомиться с Путеводителем по льготам можно на Сервисном портале в блоге «Социальная поддержка»."
    
    else:
        return "Извините, я не понимаю ваш запрос."


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
