import oc
import multiprocessing
import logging
from hypercorn.config import Config
from hypercorn.asyncio import serve
from quart import Quart, request, jsonify
from database import requests_user, requests_sub

app = Quart(__name__)
logger = logging.getLogger(__name__)

@app.route('/login', methods=['POST'])
async def login():
    try:
        data = await request.get_json()

        telegram_id = int(data['telegram_id'])
        product_id = int(data['product_id'])
        hwid = str(data['hwid'])
        logger.fatal(f"Попытка авторизации пользователя | $ID: [{telegram_id}] $Product ID: [{product_id}] $HWID: [{hwid}]")
        user = await requests_user.get_user_by_telegram_id(telegram_id)

        if not user:
            logger.fatal(f"Пользователь не найден | ID: [{telegram_id}]")
            return jsonify({'status': 'error', 'message': 'USER_NOT_FOUND', 'end_date': 0}), 404
        else:
            if user.hwid == "@":
                user.hwid = hwid
            if user.hwid == hwid:
                subscriptions = await requests_sub.get_user_subscriptions(telegram_id)

                for subscription in subscriptions:
                    if subscription.product_id == product_id:
                        logger.fatal(f"Успешная авторизация | $ID: [{telegram_id}] $Product ID: [{product_id}] $HWID: [{hwid}]")
                        return jsonify({'status': 'success',
                                        'message': 'SUB_ACTIVE',
                                        'end_date': subscription.end_date,
                                        }), 200
                await requests_user.update_user(user)
                logger.fatal(f"Отказано в авторизации. Причина: Отсутствует подписка | $ID: [{telegram_id}] $Product ID: [{product_id}] $HWID: [{hwid}]")
                return jsonify({'status': 'error', 'message': 'SUB_NOT_FOUND', 'end_date': 0}), 404
            else:
                logger.fatal(f"Отказано в авторизации. Причина: Несоотвествие HWID | $ID: [{telegram_id}] $CURRENT_HWID: [{user.hwid}] $ NEW_HWID: [{hwid}]")
                return jsonify({'status': 'error', 'message': 'OTHER_HWID', 'end_date': 0}), 404
    except Exception as e:
        print(e)
        pass


def run_server():
    import asyncio

    config = Config()
    config.bind = ["94.241.168.39:5052"]  # Пример настройки IP адреса и порта для прослушивания
    oc.log("info", "Сервис авторизации успешно запущен")
    asyncio.run(serve(app, config))
    #app.run(port=5055)


def init_auth_server():
    p = multiprocessing.Process(target=run_server)
    p.start()
