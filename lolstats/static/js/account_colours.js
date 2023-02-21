document.addEventListener('DOMContentLoaded', function() {
    let wrtags = document.getElementsByClassName('winrate');
    for (let i = 0; i < wrtags.length; i++)
    {
        let wr = parseInt(wrtags[i].innerHTML);
        if (wr >= 50)
        {
            wrtags[i].classList.add("win"); 
        }
        else
        {
            wrtags[i].classList.add("loss");
        }
    }
    let tiertags = document.getElementsByClassName('tier');
    let ranktags = document.getElementsByClassName('rank');
    for (let i = 0; i < tiertags.length; i++)
    {
        let rank = tiertags[i].innerHTML;
        tiertags[i].classList.add(rank); 
        ranktags[i].classList.add(rank);
    }
});