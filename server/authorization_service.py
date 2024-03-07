import oc
import multiprocessing
from quart import Quart, request, jsonify
from database import requests_user, requests_sub

app = Quart(__name__)


@app.route('/login', methods=['POST'])
async def login():
    try:
        data = await request.get_json()

        telegram_id = int(data['telegram_id'])
        product_id = int(data['product_id'])
        hwid = str(data['hwid'])

        print(data)
        user = await requests_user.get_user_by_telegram_id(telegram_id)

        if not user:
            return jsonify({'status': 'error', 'message': 'USER_NOT_FOUND', 'end_date': 0}), 404
        else:
            if user.hwid == "@":
                user.hwid = hwid
            if user.hwid == hwid:
                subscriptions = await requests_sub.get_user_subscriptions(telegram_id)

                for subscription in subscriptions:
                    if subscription.product_id == product_id:
                        return jsonify({'status': 'success',
                                        'message': 'SUB_ACTIVE',
                                        'end_date': subscription.end_date,
                                        }), 200
                await requests_user.update_user(user)
                return jsonify({'status': 'error', 'message': 'SUB_NOT_FOUND', 'end_date': 0}), 404
            else:
                return jsonify({'status': 'error', 'message': 'OTHER_HWID', 'end_date': 0}), 404
    except Exception as e:
        pass


def run_server():
    oc.log("info", "Сервис авторизации успешно запущен")
    app.run()


def init_auth_server():
    p = multiprocessing.Process(target=run_server)
    p.start()
