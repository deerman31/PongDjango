// hashはurlにある #/homeのようなもの
const NON_RESTRICTED_PAGE_HASHES = [
    '',
    '#/',
    '#',
    '#/login',
    '#/signup',
    '#/oauth/login',
];

export async function navigate(hash) {
    // Get mainContet
    const mainContent = document.getElementById('main-content');
    // Get sidebar
    const navbarStyle = document.getElementById('navbar-style');
    const navbarCollapse = document.getElementsByClassName('navbar-collapse')?.[0];

    // If there is no maincontent, it will exit with an error.
    if (!mainContent) {
        console.error('Main content container is missing');
        return;
    }

    // Set html corresponding to each hash value.
    const routes = {
        '': './srcs/pages/start/start.html',
        '#/': './srcs/pages/start/start.html',
        '#': './srcs/pages/start/start.html',
        '#/login': './srcs/pages/login/login.html',
        '#/signup': './srcs/pages/signup/signup.html',
        '#/oauth/login': './srcs/pages/oauth/oauth_login.html',
        '#/home': './srcs/pages/home/home.html',
        '#/user_information': './srcs/pages/user_info/user_infomation.html',
        '#/user_information/username': './srcs/pages/user_info/username.html',
        '#/user_information/email': './srcs/pages/user_info/email.html',
        '#/user_information/avatar_update': './srcs/pages/user_info/avatar_update.html',
        '#/user_information/password_update': './srcs/pages/user_info/password_update.html',
        '#/user_information/user_delete': './srcs/pages/user_info/user_delete.html',
        '#/otp-setup': './srcs/pages/otp/otp_setup.html',
        '#/friend': './srcs/pages/friend/friend.html',
        '#/history': './srcs/pages/history/history.html',
        '#/rps_history': './srcs/pages/rps_history/rps_history.html',
        '#/tournament_waiting': './srcs/pages/tournament_waiting/tournament_waiting.html',
        '#/single_game': './srcs/pages/single_game/single_game.html',
        '#/rock_paper_scissors': './srcs/pages/rock_paper_scissors/rock_paper_scissors.html',
    };

    const defaultPage = '<p>ページが見つかりません</p>';

    // サイドバーの表示をチェックしながらページをロードする関数
    async function loadPageAndCheckSidebar(url) {
        const isLoggedIn = getLocalAccessToken() != null;
        const isRestrictedArea = !NON_RESTRICTED_PAGE_HASHES.includes(hash);
        if (isRestrictedArea) {
            if (!isLoggedIn || !(await isTokenValid())) {
                window.location.hash = '#/';
                return;
            }
        } else if (isLoggedIn) {
            window.location.hash = '#/home';
            return;
        }
        if (hash === '#/home' || hash === '#/user_information' ||
            hash === '#/user_information/username' || hash === '#/user_information/email' ||
            hash === '#/user_information/avatar_update' || hash === '#/user_information/password_update' ||
            hash === '#/otp-setup' || hash === '#/user_information/user_delete' ||
            hash === '#/history'|| hash === '#/rps_history'||
            hash === '#/friend') {
            if (navbarStyle) {
                navbarStyle.innerText = `
                .login-required {
                    visibility: visible;
                }`;
            }
        } else {
            if (navbarStyle) {
                navbarStyle.innerText = `
                .login-required {
                    visibility: hidden;
                }`;
            }
        }

        if (navbarCollapse?.classList.contains('show')) {
            const collapse = new bootstrap.Collapse(navbarCollapse, {toggle: false});
            collapse.hide();
        }

        loadPage(url, mainContent, hash); // ページをロード
    }

    function getHashBase(hash) {
        let index = hash.indexOf('?');
        if (index === -1) {
            return hash;
        }
        index -= 1;
        return hash.slice(0, index);
    }

    async function isTokenValid() {
        const token = await verifyAndFetchToken();
        return !!token;
    }
    const baseHash = getHashBase(hash);

    console.log(`hash: ${baseHash}`);

    if (baseHash in routes) {
        await loadPageAndCheckSidebar(routes[baseHash]);
    } else {
        mainContent.dataset.currentUrl = undefined;
        mainContent.innerHTML = defaultPage;
    }
}

// ページがロードされたときに初期ハッシュ値に対してnavigateを呼び出し、hashchangeイベントを監視
document.addEventListener('DOMContentLoaded', async () => {
    const initialHash = window.location.hash || '#/';
    window.addEventListener('hashchange', onHashChange); // hashchangeイベントを先に設定
    await navigate(initialHash); // 初期ハッシュ値に基づいてnavigateを呼び出し
});

// ハッシュが変更されたときにnavigateを呼び出す関数
function onHashChange() {
    navigate(window.location.hash);
}

const FT_PAGE_CHANGED_EVENT_TYPE = 'ftPageChanged';
// ページをロードする関数
function loadPage(url, content, hash) {
    if (content.dataset.currentUrl === url) {
        console.log('Already loaded:', url);
        return;
    }
    content.dataset.currentUrl = url;

    fetch(`${url}?${new Date().getTime()}`)
        .then(response => response.text())
        .then(html => {
            content.innerHTML = html;
            const pageChangedEvent = new CustomEvent(FT_PAGE_CHANGED_EVENT_TYPE, {
                detail: hash,
            });
            window.dispatchEvent(pageChangedEvent);
        })
        .catch(err => {
            content.innerHTML = '<p>コンテンツを読み込めませんでした</p>';
            console.error('Error loading page:', err);
        });
}