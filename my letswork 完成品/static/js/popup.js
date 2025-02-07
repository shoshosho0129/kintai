const popup = document.getElementById('popup');
const openPopupBtn = document.getElementById('vacation-register-btn');

openPopupBtn.addEventListener('click', (event) => {
    event.preventDefault();
    popup.style.display = 'flex';
    document.body.classList.add('popup-open'); // スクロール防止
});

function closePopup() {
    popup.style.display = 'none';
    document.body.classList.remove('popup-open'); // スクロール有効化
}

// ボタンとポップアップの対応を設定
const popupMappings = {
    'vacation-register-btn': 'popup-register',
    'vacation-confirm-btn': 'popup-confirm'
};

// 各ボタンにクリックイベントを設定
Object.keys(popupMappings).forEach((buttonId) => {
    const button = document.getElementById(buttonId);
    const popupId = popupMappings[buttonId];
    const popup = document.getElementById(popupId);

    button.addEventListener('click', (event) => {
        event.preventDefault(); // デフォルトの動作を防ぐ
        popup.style.display = 'flex'; // ポップアップを表示
        document.body.classList.add('popup-open'); // スクロール防止
    });
});

// ポップアップを閉じる関数
function closePopup(popupId) {
    const popup = document.getElementById(popupId);
    popup.style.display = 'none'; // ポップアップを非表示
    document.body.classList.remove('popup-open'); // スクロール有効化
}