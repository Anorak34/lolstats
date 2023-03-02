document.addEventListener('DOMContentLoaded', function() {
    let items_dd = JSON.parse(document.getElementById('item_dd').textContent);
    let tooltips = document.getElementsByClassName('tooltiptext');
    for (let i = 0; i < tooltips.length; i++)
    {
        let itemId = tooltips[i].dataset.itemid;
        tooltips[i].innerHTML = `<span class="item-name">${items_dd['data'][itemId]['name']}</span><br>Price: <span class="item-price">${items_dd['data'][itemId]['gold']['total']}</span><br>${items_dd['data'][itemId]['description']}`;
    }
});