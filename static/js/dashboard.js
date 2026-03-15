document.addEventListener("DOMContentLoaded", () => {

    // -------------------------------
    // Инициализация Popover для всех задач
    // -------------------------------
    const popoverTriggerList = [].slice.call(document.querySelectorAll('.task-icon-btn'))
    popoverTriggerList.forEach(el => {
        new bootstrap.Popover(el, {
            trigger: 'hover',
            placement: 'top'
        })
    })

    // -------------------------------
    // Удаление блока
    // -------------------------------
    document.querySelectorAll('.btn-block-delete').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const blockId = btn.dataset.blockId
            if (!confirm("Вы уверены, что хотите удалить блок?")) return

            const response = await fetch(`/api/block/${blockId}/delete/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/json"
                }
            })

            const data = await response.json()
            if (data.status === "ok") {
                // удалить блок из DOM
                const blockEl = document.querySelector(`[data-block-id="${blockId}"]`)
                if (blockEl) blockEl.remove()
            } else {
                alert("Ошибка при удалении блока")
            }
        })
    })

    document.querySelectorAll(".block-title-clickable").forEach(el => {
        el.addEventListener("click", () => {
            const blockId = el.closest(".task-block").dataset.blockId;
            window.location.href = `/block/${blockId}/view/`;
        });
    });
    // -------------------------------
    // Скрыть блок
    // -------------------------------
    document.querySelectorAll('.btn-block-hide').forEach(btn => {
        btn.addEventListener('click', async e => {
            const blockId = btn.dataset.blockId
            const blockEl = document.querySelector(`[data-block-id="${blockId}"]`)

            const response = await fetch(`/api/block/${blockId}/hide/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/json"
                }
            })

            const data = await response.json()
            if (data.status === "ok") {
                if (data.is_hided) {
                    blockEl.classList.add("d-none")
                } else {
                    blockEl.classList.remove("d-none")
                }
            } else {
                alert("Ошибка при изменении состояния блока")
            }
        })
    })

    // -------------------------------
    // CSRF helper
    // -------------------------------
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie) {
            const cookies = document.cookie.split(';')
            for (let cookie of cookies) {
                cookie = cookie.trim()
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
                    break
                }
            }
        }
        return cookieValue
    }

})