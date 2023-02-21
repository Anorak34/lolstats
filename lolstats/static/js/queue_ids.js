document.addEventListener('DOMContentLoaded', function() {
    let queue_ids = JSON.parse(document.getElementById('queue_ids').textContent);
    let queues = document.getElementsByClassName('queue');
    for (let i = 0; i < queues.length; i++)
    {
        let queue = parseInt(queues[i].innerHTML);
        for (let j = 0; j < queue_ids.length; j++)
        {
            if (queue_ids[j].queueId == queue) {
                let game = queue_ids[j].description
                game = game.replace('games', '')
                queues[i].innerHTML = game;
            }
        }
    }
});