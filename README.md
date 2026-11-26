## Требования
- Python 3.11+
- Git

## Установка

1. Клонируйте репозиторий:
   git clone <ссылка на ваш репозиторий>
2. Перейдите в папку проекта:
   cd project
3. Создайте виртуальное окружение:
   python -m venv .venv
4. Активируйте окружение:
   - Windows: .venv\Scripts\Activate.ps1
   - macOS/Linux: source .venv/bin/activate
5. Установите зависимости:
   python -m pip install fastapi uvicorn

## Запуск
Запустите сервер командой:
python -m uvicorn main:app --reload

Откройте в браузере: http://127.0.0.1:8000/health
Ожидаемый ответ: {"status":"ok"}